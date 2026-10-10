"""Tablas verificadas; solo mu admite interpolación lineal aprobada respecto a L."""
from bisect import bisect_right
from dataclasses import dataclass
import math


# DGA 2022 Cachapoal SIT527, impresa 69/PDF79, tablas 7-1 y 7-2 (Mery 2013).
# Son complementarias: no son tablas publicadas por MTC.
TABLA_BETA: dict[float, float] = {2: .82, 5: .86, 10: .90, 20: .94, 50: .97,
              100: 1.00, 500: 1.05, 1000: 1.07}
TABLA_Z: dict[float, float] = {.05: .43, .15: .42, .5: .41, 1: .40, 1.5: .39,
           2.5: .38, 4: .37, 6: .36, 8: .35, 10: .34, 15: .33,
           20: .32, 25: .31, 40: .30, 60: .29, 90: .28, 140: .27,
           190: .26, 250: .25, 310: .24, 370: .23, 450: .22,
           570: .21, 750: .20}

# MTC MAN_11 HHD-2011.pdf, p.107 tabla 13. Categorías <1 y >4 literales.
LUCES_M: tuple[float, ...] = (10, 13, 16, 18, 21, 25, 30, 42, 52, 63, 106, 124, 200)
TABLA_MU: dict[str | float, tuple[float, ...]] = {
    "<1": (1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.),
    1.: (.96, .97, .98, .98, .99, .99, .99, 1., 1., 1., 1., 1., 1.),
    1.5: (.94, .96, .97, .97, .97, .98, .99, .99, .99, .99, 1., 1., 1.),
    2.: (.93, .94, .95, .96, .97, .97, .98, .98, .99, .99, .99, .99, 1.),
    2.5: (.90, .93, .94, .95, .96, .96, .97, .98, .98, .99, .99, .99, 1.),
    3.: (.89, .91, .93, .94, .95, .96, .96, .97, .98, .98, .99, .99, .99),
    3.5: (.87, .90, .92, .93, .94, .95, .96, .97, .98, .98, .99, .99, .99),
    ">4": (.85, .89, .91, .92, .93, .94, .95, .96, .97, .98, .99, .99, .99),
}


@dataclass(frozen=True)
class SeleccionMu:
    valor: float
    detalle: str
    interpolado: bool


def _numero_positivo(valor: float, nombre: str) -> None:
    try:
        es_valido = type(valor) in (int, float) and math.isfinite(valor) and valor > 0
    except OverflowError:
        es_valido = False
    if not es_valido:
        raise ValueError(f"{nombre}: se requiere un número finito mayor que cero.")


@dataclass(frozen=True)
class SeleccionCoeficiente:
    valor: float
    detalle: str
    por_formula: bool


def _extremos(tabla: dict[float, float]) -> tuple[float, float]:
    claves = tuple(tabla)
    return claves[0], claves[-1]


def dm_en_tramo_z(diametro_medio_mm: float) -> bool:
    """Verdadero si Dm cae entre 0.05 y 750 mm y no es una celda publicada."""
    if type(diametro_medio_mm) not in (int, float):
        return False
    try:
        finito = math.isfinite(diametro_medio_mm)
    except OverflowError:
        return False
    menor, mayor = _extremos(TABLA_Z)
    return finito and menor < diametro_medio_mm < mayor and diametro_medio_mm not in TABLA_Z


def seleccionar_beta(periodo_retorno_anios: float) -> SeleccionCoeficiente:
    """Celda literal de la tabla 7-1, o la fórmula de usuario dentro de 2 a 1000 años."""
    _numero_positivo(periodo_retorno_anios, "Período T (años)")
    if periodo_retorno_anios in TABLA_BETA:
        valor = TABLA_BETA[periodo_retorno_anios]
        return SeleccionCoeficiente(
            valor,
            "DGA/MOP 2022, tabla 7-1, p. 69 / PDF 79: "
            f"T={periodo_retorno_anios:g} años, beta={valor:g}; celda literal.",
            False,
        )
    menor, mayor = _extremos(TABLA_BETA)
    if not menor < periodo_retorno_anios < mayor:
        raise ValueError(
            f"Período T (años)={periodo_retorno_anios}: fuera de {menor:g} a {mayor:g} años; "
            "no se extrapola.")
    logaritmo = math.log10(periodo_retorno_anios)
    valor = 0.7929 + 0.0973 * logaritmo
    return SeleccionCoeficiente(
        valor,
        "Fórmula aprobada por el usuario para T sin celda publicada, "
        f"dentro de {menor:g} a {mayor:g} años. No es tabla DGA ni norma MTC. "
        f"beta = 0.7929 + 0.0973*log10({periodo_retorno_anios:g}) = {valor:.12g}.",
        True,
    )


def seleccionar_z(diametro_medio_mm: float) -> SeleccionCoeficiente:
    """Celda literal de la tabla 7-2, o la fórmula de usuario dentro de 0.05 a 750 mm."""
    _numero_positivo(diametro_medio_mm, "Diámetro Dm (mm)")
    if diametro_medio_mm in TABLA_Z:
        valor = TABLA_Z[diametro_medio_mm]
        return SeleccionCoeficiente(
            valor,
            "DGA/MOP 2022, tabla 7-2, p. 69 / PDF 79: "
            f"Dm={diametro_medio_mm:g} mm, z={valor:g}; celda literal. No es 1/(1+z).",
            False,
        )
    menor, mayor = _extremos(TABLA_Z)
    if not menor < diametro_medio_mm < mayor:
        raise ValueError(
            f"Diámetro Dm (mm)={diametro_medio_mm}: fuera de {menor:g} a {mayor:g} mm; "
            "no se extrapola.")
    logaritmo = math.log10(diametro_medio_mm)
    valor = 0.394557 - 0.04136 * logaritmo - 0.00891 * logaritmo ** 2
    return SeleccionCoeficiente(
        valor,
        "Fórmula aprobada por el usuario para Dm sin celda publicada, "
        f"dentro de {menor:g} a {mayor:g} mm. No es tabla DGA ni norma MTC. "
        f"z = 0.394557 - 0.04136*log10({diametro_medio_mm:g}) "
        f"- 0.00891*(log10({diametro_medio_mm:g}))^2 = {valor:.12g}.",
        True,
    )


def obtener_beta(periodo_retorno_anios: float) -> float:
    """Devolver beta; la celda publicada prevalece sobre la fórmula."""
    return seleccionar_beta(periodo_retorno_anios).valor


def obtener_z(diametro_medio_mm: float) -> float:
    """Devolver z, no 1/(1+z); la celda publicada prevalece sobre la fórmula."""
    return seleccionar_z(diametro_medio_mm).valor


def _fila_mu(velocidad_m_s: float) -> str | float:
    fila: str | float = ("<1" if velocidad_m_s < 1 else
                         ">4" if velocidad_m_s > 4 else velocidad_m_s)
    if fila not in TABLA_MU:
        raise ValueError("La velocidad no tiene fila publicada en MTC tabla 13; no se interpola.")
    return fila


def _rotulo_fila(fila: str | float) -> str:
    return f"V{fila}" if isinstance(fila, str) else f"V={fila:g}"


def seleccionar_mu(sin_obstaculos: bool, velocidad_m_s: float,
                   luz_libre_m: float) -> SeleccionMu:
    """Seleccionar fila literal e interpolar mu linealmente solo respecto a L."""
    if type(sin_obstaculos) is not bool:
        raise ValueError("La condición sin obstáculos debe ser verdadero o falso.")
    _numero_positivo(velocidad_m_s, "Velocidad (m/s)")
    if sin_obstaculos:
        return SeleccionMu(1., "Sin obstáculos: mu = 1; L no participa.", False)
    _numero_positivo(luz_libre_m, "Luz libre (m)")
    if not LUCES_M[0] <= luz_libre_m <= LUCES_M[-1]:
        raise ValueError("Luz libre fuera de 10 a 200 m; no se extrapola mu.")
    fila = _fila_mu(velocidad_m_s)
    valores = TABLA_MU[fila]
    rotulo = _rotulo_fila(fila)
    if luz_libre_m in LUCES_M:
        indice = LUCES_M.index(luz_libre_m)
        valor = valores[indice]
        detalle = (f"MTC HHD 2011 p.107 tabla 13: {rotulo} m/s, "
                   f"L={luz_libre_m:g} m, mu={valor:g}; celda literal.")
        return SeleccionMu(valor, detalle, False)
    superior = bisect_right(LUCES_M, luz_libre_m)
    inferior = superior - 1
    luz_1, luz_2 = LUCES_M[inferior], LUCES_M[superior]
    mu_1, mu_2 = valores[inferior], valores[superior]
    valor = mu_1 + (mu_2 - mu_1) * (luz_libre_m - luz_1) / (luz_2 - luz_1)
    detalle = (
        f"MTC HHD 2011 p.107 tabla 13, {rotulo} m/s: celdas L1={luz_1:g} m, "
        f"mu1={mu_1:g}; L2={luz_2:g} m, mu2={mu_2:g}. Criterio de interpolación "
        "lineal aprobado por el usuario; regla no publicada por MTC. "
        f"mu = {mu_1:g} + ({mu_2:g} - {mu_1:g}) * "
        f"({luz_libre_m:g} - {luz_1:g}) / ({luz_2:g} - {luz_1:g}) = {valor:.12g}."
    )
    return SeleccionMu(valor, detalle, True)


def obtener_mu(sin_obstaculos: bool, velocidad_m_s: float, luz_libre_m: float) -> float:
    """Devolver mu; compatibilidad para consumidores que solo necesitan el valor."""
    return seleccionar_mu(sin_obstaculos, velocidad_m_s, luz_libre_m).valor
