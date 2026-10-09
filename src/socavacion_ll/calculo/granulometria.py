"""Diámetro medio por fracciones: MTC HHD p. 92, ecuación 52."""
import math

TOLERANCIA_PORCENTAJE = 1e-8
MAXIMO_FRACCIONES = 100


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
