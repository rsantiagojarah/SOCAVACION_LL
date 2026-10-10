"""Diámetro medio por fracciones: MTC HHD p. 92, ecuación 52.

La media aritmética de aberturas es una regla aprobada por el usuario.
La ecuación 52 no la escribe: allí Di ya es la marca de clase.
"""
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
import math
from typing import cast

TOLERANCIA_PORCENTAJE = 1e-8
MAXIMO_FRACCIONES = 100
_CIEN = Decimal(100)
_SUMA_MINIMA = Decimal("99.5")
_SUMA_MAXIMA = Decimal("100.5")


def calcular_diametro_medio(fracciones: list[tuple[float, float]]) -> float:
    """Recibir Di documentado en mm y porcentaje por intervalo, sin normalizar."""
    if type(fracciones) is not list or not 1 <= len(fracciones) <= MAXIMO_FRACCIONES:
        raise ValueError("Ingrese de 1 a 100 fracciones (límite informático).")
    productos: list[float] = []
    porcentajes: list[float] = []
    for fraccion in fracciones:
        if type(fraccion) is not tuple or len(fraccion) != 2:
            raise ValueError("Cada fracción requiere Di y porcentaje por intervalo.")
        diametro, porcentaje = fraccion
        try:
            validos = (type(diametro) in (int, float) and type(porcentaje) in (int, float)
                       and math.isfinite(diametro) and math.isfinite(porcentaje)
                       and diametro > 0 and 0 <= porcentaje <= 100)
        except OverflowError:
            validos = False
        if not validos:
            raise ValueError("Di debe ser finito y positivo; porcentaje finito entre 0 y 100.")
        productos.append(diametro * porcentaje)
        porcentajes.append(porcentaje)
    if abs(math.fsum(porcentajes) - 100) > TOLERANCIA_PORCENTAJE:
        raise ValueError("Los porcentajes deben sumar 100 (tolerancia absoluta 1e-8); no se normalizan.")
    try:
        diametro_medio = math.fsum(productos) / 100
    except OverflowError as error:
        raise ValueError("El cálculo de Dm excede el rango numérico representable.") from error
    if not math.isfinite(diametro_medio) or diametro_medio <= 0:
        raise ValueError("El cálculo de Dm debe producir un número finito positivo.")
    return diametro_medio


@dataclass(frozen=True)
class FilaDm:
    fraccion: str
    d_superior_mm: Decimal | None
    d_inferior_mm: Decimal | None
    di_mm: Decimal | None
    porcentaje: Decimal
    aporte: Decimal | None


@dataclass(frozen=True)
class CalculoDmTamices:
    filas: tuple[FilaDm, ...]
    suma_porcentajes: Decimal
    suma_productos: Decimal
    diametro_medio_mm: Decimal


def calcular_diametro_medio_por_tamices(
    tamices: list[tuple[float, float]], fondo: float = 0,
    dmax_mm: float | None = None,
    boloneria: list[tuple[float, float, float]] | None = None,
) -> CalculoDmTamices:
    """Dm = Σ(Di × Pi) / 100, con Di = (D superior + D inferior) / 2.

    Pi es el retenido parcial ingresado. El fondo suma en los porcentajes
    y no aporta producto. La bolonería, si se entrega, es adicional al laboratorio.
    """
    serie, fondo_dec, dmax, gravas = _leer_tamices(tamices, fondo, dmax_mm, boloneria)
    factor = (_CIEN - sum((item[2] for item in gravas), Decimal(0))) / _CIEN
    if factor < 0:
        raise ValueError("La bolonería no puede superar el 100 %.")
    serie = [(abertura, porcentaje * factor) for abertura, porcentaje in serie]
    fondo_dec *= factor
    filas = _filas_boloneria(gravas) + _filas_tamices(serie, dmax)
    if fondo_dec != 0:
        superior = serie[-1][0] if serie else None
        filas.append(FilaDm("Fondo", superior, None, None, fondo_dec, None))
    suma_porcentajes = sum((fila.porcentaje for fila in filas), Decimal(0))
    if not _SUMA_MINIMA <= suma_porcentajes <= _SUMA_MAXIMA:
        raise ValueError(
            "Los porcentajes retenidos, incluido el fondo, deben sumar entre 99.5 y 100.5. "
            "No se normalizan.")
    productos = [fila.aporte for fila in filas if fila.di_mm is not None and fila.aporte is not None]
    if not productos:
        raise ValueError("No hay fracciones con Di definido. Dm no es definitivo.")
    suma_productos = sum(productos, Decimal(0))
    diametro = (suma_productos / _CIEN).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
    if diametro <= 0:
        raise ValueError("El cálculo de Dm debe producir un número finito positivo.")
    return CalculoDmTamices(tuple(filas), suma_porcentajes, suma_productos, diametro)


def _leer_tamices(
    tamices: list[tuple[float, float]], fondo: float, dmax_mm: float | None,
    boloneria: list[tuple[float, float, float]] | None,
) -> tuple[list[tuple[Decimal, Decimal]], Decimal, Decimal | None, list[tuple[Decimal, Decimal, Decimal]]]:
    if type(tamices) is not list or len(tamices) > MAXIMO_FRACCIONES:
        raise ValueError("Ingrese de 0 a 100 tamices (límite informático).")
    serie = [_tamiz(item) for item in tamices]
    for anterior, actual in zip(serie, serie[1:]):
        if anterior[0] <= actual[0]:
            raise ValueError("Las aberturas deben estar ordenadas de mayor a menor.")
    if type(boloneria) is not list and boloneria is not None:
        raise ValueError("La bolonería se entrega como lista de intervalos.")
    gravas = [] if boloneria is None else [_grava(item) for item in boloneria]
    if len(gravas) > MAXIMO_FRACCIONES:
        raise ValueError("Ingrese de 0 a 100 intervalos de bolonería (límite informático).")
    if not serie and not any(item[2] > 0 for item in gravas):
        raise ValueError("Se requiere al menos una fracción con retenido.")
    return serie, _porcentaje(fondo), None if dmax_mm is None else _abertura(dmax_mm), gravas


def _filas_boloneria(gravas: list[tuple[Decimal, Decimal, Decimal]]) -> list[FilaDm]:
    filas: list[FilaDm] = []
    for superior, inferior, porcentaje in gravas:
        di = (superior + inferior) / 2 if porcentaje > 0 else None
        aporte = di * porcentaje if di is not None else Decimal(0)
        filas.append(FilaDm(_intervalo(superior, inferior), superior, inferior, di, porcentaje, aporte))
    return filas


def _filas_tamices(serie: list[tuple[Decimal, Decimal]], dmax: Decimal | None) -> list[FilaDm]:
    filas: list[FilaDm] = []
    for indice, (abertura, porcentaje) in enumerate(serie):
        superior = serie[indice - 1][0] if indice else None
        if porcentaje > 0 and superior is None:
            if dmax is None or dmax <= abertura:
                raise ValueError(
                    "La primera fracción con retenido no tiene límite superior. "
                    "No se calcula un Dm definitivo.")
            superior = dmax
        if porcentaje > 0 and superior is not None:
            di = (superior + abertura) / 2
            filas.append(FilaDm(_intervalo(superior, abertura), superior, abertura, di, porcentaje, di * porcentaje))
        else:
            nombre = _texto(abertura) if superior is None else _intervalo(superior, abertura)
            filas.append(FilaDm(nombre, superior, abertura, None, porcentaje, Decimal(0)))
    return filas


def _tamiz(item: object) -> tuple[Decimal, Decimal]:
    if type(item) is not tuple or len(item) != 2:
        raise ValueError("Cada tamiz requiere abertura y porcentaje retenido parcial.")
    abertura, porcentaje = cast(tuple[object, object], item)
    return _abertura(abertura), _porcentaje(porcentaje)


def _grava(item: object) -> tuple[Decimal, Decimal, Decimal]:
    if type(item) is not tuple or len(item) != 3:
        raise ValueError("Cada intervalo de bolonería requiere límite superior, inferior y Pi.")
    superior_bruto, inferior_bruto, porcentaje = cast(tuple[object, object, object], item)
    superior, inferior = _abertura(superior_bruto), _abertura(inferior_bruto)
    if superior <= inferior:
        raise ValueError("En bolonería el límite superior debe ser mayor que el inferior.")
    return superior, inferior, _porcentaje(porcentaje)


def _decimal(valor: object, mensaje: str) -> Decimal:
    if type(valor) not in (int, float):
        raise ValueError(mensaje)
    numero = Decimal(str(valor))
    if not numero.is_finite():
        raise ValueError(mensaje)
    return numero


def _porcentaje(valor: object) -> Decimal:
    numero = _decimal(valor, "Pi debe ser finito y estar entre 0 y 100.")
    if numero < 0 or numero > _CIEN:
        raise ValueError("Pi debe ser finito y estar entre 0 y 100.")
    return numero


def _abertura(valor: object) -> Decimal:
    numero = _decimal(valor, "La abertura debe ser finita y positiva.")
    if numero <= 0:
        raise ValueError("La abertura debe ser finita y positiva.")
    return numero


def _texto(valor: Decimal) -> str:
    texto = format(valor, "f")
    return texto.rstrip("0").rstrip(".") if "." in texto else texto


def _intervalo(superior: Decimal, inferior: Decimal) -> str:
    return f"{_texto(superior)}-{_texto(inferior)}"
