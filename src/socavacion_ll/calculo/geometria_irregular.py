"""Recorte y discretización lineal de una única rama mojada."""
from bisect import bisect_left, bisect_right
from dataclasses import dataclass
import math
from typing import cast

from ..dominio.modelos import PuntoTerreno


@dataclass(frozen=True)
class FranjaMojada:
    x_inicio_m: float
    x_fin_m: float
    abscisa_m: float
    ancho_m: float
    area_m2: float
    tirante_m: float
    cota_centro_m: float


def _finito(valor: object) -> bool:
    if type(valor) not in (int, float):
        return False
    try:
        return math.isfinite(cast(int | float, valor))
    except OverflowError:
        return False


def _validar(puntos: tuple[PuntoTerreno, ...], agua: float, divisiones: int) -> None:
    if type(puntos) is not tuple or not 2 <= len(puntos) <= 200:
        raise ValueError("La sección irregular requiere entre 2 y 200 puntos.")
    if type(divisiones) is not int or not 2 <= divisiones <= 400:
        raise ValueError("La discretización debe usar un entero entre 2 y 400 divisiones.")
    if not _finito(agua):
        raise ValueError("La cota de agua debe ser finita.")
    anterior = None
    for punto in puntos:
        if type(punto) is not PuntoTerreno:
            raise ValueError("La sección contiene un punto de terreno no válido.")
        if not _finito(punto.abscisa_m) or not _finito(punto.cota_m):
            raise ValueError("Las coordenadas del terreno deben ser finitas.")
        if anterior is not None and punto.abscisa_m < anterior.abscisa_m:
            raise ValueError("Las abscisas no pueden ser decrecientes.")
        if punto == anterior:
            raise ValueError("No se admiten puntos idénticos consecutivos.")
        anterior = punto


def _cruce(x0: float, d0: float, x1: float, d1: float) -> float:
    return x0 - d0 * (x1 - x0) / (d1 - d0)


def _ramas_mojadas(
    puntos: tuple[PuntoTerreno, ...], agua: float,
) -> list[tuple[float, float]]:
    intervalos: list[tuple[float, float]] = []
    for p0, p1 in zip(puntos, puntos[1:]):
        d0, d1 = agua - p0.cota_m, agua - p1.cota_m
        intervalo = None
        if d0 > 0 and d1 > 0:
            intervalo = (p0.abscisa_m, p1.abscisa_m)
        elif d0 <= 0 < d1:
            intervalo = (_cruce(p0.abscisa_m, d0, p1.abscisa_m, d1), p1.abscisa_m)
        elif d0 > 0 >= d1:
            intervalo = (p0.abscisa_m, _cruce(p0.abscisa_m, d0, p1.abscisa_m, d1))
        if intervalo is None or intervalo[1] <= intervalo[0]:
            continue
        if intervalos and intervalos[-1][1] == intervalo[0] and d0 > 0:
            intervalos[-1] = (intervalos[-1][0], intervalo[1])
        else:
            intervalos.append(intervalo)
    return intervalos


def _cota_en(
    puntos: tuple[PuntoTerreno, ...], x: float, lado_derecho: bool = True,
) -> float:
    abscisas = [p.abscisa_m for p in puntos]
    posicion = bisect_right(abscisas, x) if lado_derecho else bisect_left(abscisas, x)
    indice = min(max(posicion - 1, 0), len(puntos) - 2)
    p0, p1 = puntos[indice], puntos[indice + 1]
    proporcion = (x - p0.abscisa_m) / (p1.abscisa_m - p0.abscisa_m)
    return p0.cota_m + proporcion * (p1.cota_m - p0.cota_m)


def _limites(
    puntos: tuple[PuntoTerreno, ...], inicio: float, fin: float, divisiones: int,
) -> list[float]:
    ancho = fin - inicio
    candidatos = [inicio + ancho * indice / divisiones for indice in range(divisiones + 1)]
    candidatos.extend(p.abscisa_m for p in puntos if inicio < p.abscisa_m < fin)
    ordenados = sorted(candidatos)
    unicos = [ordenados[0]]
    for valor in ordenados[1:]:
        if valor != unicos[-1]:
            unicos.append(valor)
    unicos[0], unicos[-1] = inicio, fin
    return unicos


def formar_franjas(
    puntos: tuple[PuntoTerreno, ...], cota_agua_m: float, divisiones: int,
) -> tuple[FranjaMojada, ...]:
    """Formar franjas trapezoidales exactas sobre tramos lineales del terreno."""
    _validar(puntos, cota_agua_m, divisiones)
    ramas = _ramas_mojadas(puntos, cota_agua_m)
    if not ramas:
        raise ValueError("El perfil no contiene un área mojada positiva.")
    if len(ramas) != 1:
        raise ValueError("El perfil contiene más de una rama mojada; este alcance admite una sola.")
    inicio, fin = ramas[0]
    limites = _limites(puntos, inicio, fin, divisiones)
    franjas = []
    for x0, x1 in zip(limites, limites[1:]):
        ancho = x1 - x0
        d0 = max(0.0, cota_agua_m - _cota_en(puntos, x0, True))
        d1 = max(0.0, cota_agua_m - _cota_en(puntos, x1, False))
        area = (d0 + d1) * ancho / 2
        if area <= 0:
            continue
        centro = (x0 + x1) / 2
        franjas.append(FranjaMojada(
            x0, x1, centro, ancho, area, area / ancho, _cota_en(puntos, centro),
        ))
    if not franjas:
        raise ValueError("La discretización no produjo franjas mojadas positivas.")
    return tuple(franjas)
