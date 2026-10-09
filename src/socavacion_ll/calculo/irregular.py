"""Reparto LL puro sobre franjas mojadas ya formadas."""
from dataclasses import dataclass
import math

from ..dominio.modelos import PuntoResultado
from .geometria_irregular import FranjaMojada


@dataclass(frozen=True)
class EvaluacionIrregular:
    alpha: float
    suma_reparto: float
    area_m2: float
    ancho_mojado_m: float
    tirante_medio_potencial_m: float
    denominador: float
    exponente: float
    puntos: tuple[PuntoResultado, ...]
    cierre_caudal_m3s: float


def _positivo(valor: float, nombre: str) -> float:
    try:
        valido = math.isfinite(valor) and valor > 0
    except (OverflowError, TypeError):
        valido = False
    if not valido:
        raise ValueError(f"{nombre}: se requiere un valor positivo y finito.")
    return valor


def evaluar_franjas(
    franjas: tuple[FranjaMojada, ...], caudal_m3s: float,
    diametro_medio_mm: float, beta: float, mu: float, z: float,
    cota_agua_m: float,
) -> EvaluacionIrregular:
    """Aplicar el reparto aprobado y la ecuación 59 sin redondeos."""
    if type(franjas) is not tuple or not franjas:
        raise ValueError("Se requiere al menos una franja mojada.")
    for nombre, valor in (
        ("Caudal", caudal_m3s), ("Dm", diametro_medio_mm),
        ("beta", beta), ("mu", mu), ("1+z", 1 + z),
    ):
        _positivo(valor, nombre)
    if not math.isfinite(cota_agua_m):
        raise ValueError("La cota de agua debe ser finita.")
    try:
        suma = sum(_positivo(f.tirante_m, "Tirante de franja") ** (5 / 3) *
                   _positivo(f.ancho_m, "Ancho de franja") for f in franjas)
        suma = _positivo(suma, "Suma de reparto")
        alpha = _positivo(caudal_m3s / suma, "Alpha")
        denominador = _positivo(
            .68 * beta * mu * diametro_medio_mm ** .28, "Denominador LL",
        )
        exponente = 1 / (1 + z)
        puntos = []
        for franja in franjas:
            q = _positivo(alpha * franja.tirante_m ** (5 / 3), "Caudal unitario")
            caudal_franja = _positivo(q * franja.ancho_m, "Caudal de franja")
            hs = _positivo((q / denominador) ** exponente, "Profundidad Hs")
            socavacion = hs - franja.tirante_m
            cota_ll = cota_agua_m - hs
            cota_perfil = franja.cota_centro_m - max(0.0, socavacion)
            puntos.append(PuntoResultado(
                franja.abscisa_m, franja.cota_centro_m, franja.tirante_m,
                hs, socavacion, cota_ll, cota_perfil, franja.ancho_m,
                franja.area_m2, q, caudal_franja,
            ))
        area = _positivo(sum(f.area_m2 for f in franjas), "Área mojada")
        ancho = _positivo(sum(f.ancho_m for f in franjas), "Ancho mojado")
        hm = _positivo((suma / ancho) ** (3 / 5), "Tirante medio potencial")
        cierre = sum(p.caudal_franja_m3s for p in puntos) - caudal_m3s
    except (OverflowError, ZeroDivisionError) as error:
        raise ValueError("Los datos exceden el intervalo numérico del cálculo LL.") from error
    if not math.isclose(cierre, 0.0, rel_tol=0.0, abs_tol=abs(caudal_m3s) * 1e-12):
        raise ValueError("El reparto por franjas no cierra el caudal dentro de 1e-12 relativo.")
    return EvaluacionIrregular(
        alpha, suma, area, ancho, hm, denominador, exponente,
        tuple(puntos), cierre,
    )
