"""Orquestación pura del cálculo LL rectangular o irregular."""
import math

from ..dominio.modelos import Proyecto, PuntoResultado, Resultado
from ..dominio.validacion import validar_proyecto
from .coeficientes import seleccionar_beta, seleccionar_mu, seleccionar_z
from .geometria_irregular import formar_franjas
from .irregular import evaluar_franjas

FUENTES = (
    "Principal: docs/MAN_11 HHD-2011.pdf, pp. 107-108, tabla 13 y ecuación 59; "
    "Dm en mm conforme a p. 108 (discrepancia con resumen p. 158).",
    "Principal: docs/Manual de Puentes MTC 2018 (PGA).pdf, impresa 47/PDF 51, "
    "§1.2.3a: escenarios y diferencia respecto a socavación total.",
    "Complementaria: docs/complementarias/Schreider_2001_referencia.md; "
    "Schreider et al. (2001), ecuación 1, p. 16: alpha rectangular.",
    "Complementaria: docs/complementarias/DGA_2022_Cachapoal_SIT527.pdf, "
    "impresas 68-69/PDF 78-79: reparto por franjas, beta y z; no es norma MTC.",
    "Fórmula de usuario, no publicada en esas tablas, solo entre sus extremos: "
    "beta = 0.7929 + 0.0973*log10(T); "
    "z = 0.394557 - 0.04136*log10(Dm) - 0.00891*(log10(Dm))^2.",
)
TOLERANCIA_REFINAMIENTO = 1e-3


def _positivo_finito(valor: float, nombre: str) -> float:
    try:
        valido = math.isfinite(valor) and valor > 0
    except (OverflowError, TypeError):
        valido = False
    if not valido:
        raise ValueError(f"{nombre}: el cálculo excede la precisión numérica admitida.")
    return valor


def _advertencias(
    proyecto: Proyecto, velocidad: float, detalle_mu: str, interpolado: bool,
    puntos: tuple[PuntoResultado, ...], formula_beta: bool, formula_z: bool,
) -> list[str]:
    tipo = "irregular por franjas" if proyecto.tipo_seccion == "irregular" else "rectangular"
    avisos = [
        f"Sección {tipo}, lecho homogéneo no cohesivo y agua clara (phi=1).",
        "Socavación general LL: no es socavación total ni determina la cimentación.",
        "La pendiente se conserva como antecedente; el nivel de agua es un dato externo.",
        "Beta y z de celda publicada proceden de una fuente complementaria, no de tablas MTC.",
    ]
    if formula_beta:
        avisos.append(
            "T no tiene celda de beta: se usó la fórmula logarítmica aprobada por el usuario. "
            "No sustituye la tabla DGA ni se extrapola fuera de 2 a 1000 años."
        )
    if formula_z:
        avisos.append(
            "Dm no tiene celda de z: se usó la fórmula logarítmica aprobada por el usuario. "
            "No sustituye la tabla DGA ni se extrapola fuera de 0.05 a 750 mm."
        )
    if not math.isclose(proyecto.velocidad_m_s, velocidad, rel_tol=1e-6, abs_tol=0):
        avisos.append(
            "La velocidad ingresada difiere de Q/A; revise la hidráulica. Para mu se "
            "conserva la ingresada. Tolerancia relativa 1e-6, no normativa."
        )
    if interpolado:
        avisos.append(
            "Mu fue interpolado linealmente solo respecto a L por criterio aprobado; "
            "la tabla 13 MTC no publica esa regla. No se interpoló V."
        )
    if any(p.socavacion_m < 0 for p in puntos):
        avisos.append(
            "Existe Sg negativa: no se interpreta como sedimentación. El perfil limitado "
            "usa max(0,Sg) solo como convención gráfica."
        )
    return avisos


def _calcular_rectangular(
    proyecto: Proyecto, beta: float, mu: float, z: float, detalle_mu: str,
    interpolado: bool, detalle_beta: str, detalle_z: str, formula_beta: bool,
    formula_z: bool,
) -> Resultado:
    try:
        tirante = proyecto.cota_agua_m - proyecto.cota_fondo_m
        area = _positivo_finito(proyecto.ancho_m * tirante, "Área hidráulica")
        velocidad = _positivo_finito(proyecto.caudal_m3s / area, "Velocidad Q/A")
        potencia = _positivo_finito(tirante ** (5 / 3), "Potencia del tirante")
        alpha = _positivo_finito(
            proyecto.caudal_m3s / (potencia * proyecto.ancho_m), "Alpha",
        )
        numerador = _positivo_finito(alpha * potencia, "Numerador LL")
        denominador = _positivo_finito(
            .68 * beta * mu * proyecto.diametro_medio_mm ** .28, "Denominador LL",
        )
        exponente = 1 / (1 + z)
        profundidad = _positivo_finito((numerador / denominador) ** exponente, "Hs")
    except (OverflowError, ZeroDivisionError) as error:
        raise ValueError("Los datos exceden el intervalo numérico del cálculo LL.") from error
    socavacion = profundidad - tirante
    cota_ll = proyecto.cota_agua_m - profundidad
    cota_perfil = proyecto.cota_fondo_m - max(0, socavacion)
    puntos = tuple(PuntoResultado(
        proyecto.ancho_m * indice / (proyecto.numero_puntos - 1),
        proyecto.cota_fondo_m, tirante, profundidad, socavacion, cota_ll, cota_perfil,
    ) for indice in range(proyecto.numero_puntos))
    avisos = _advertencias(
        proyecto, velocidad, detalle_mu, interpolado, puntos, formula_beta, formula_z,
    )
    return Resultado(
        proyecto, alpha, beta, mu, 1.0, z, area, tirante, velocidad,
        numerador, denominador, exponente, puntos, tuple(avisos), FUENTES,
        detalle_mu, "rectangular", proyecto.ancho_m, detalle_beta=detalle_beta,
        detalle_z=detalle_z,
    )


def _calcular_irregular(
    proyecto: Proyecto, beta: float, mu: float, z: float, detalle_mu: str,
    interpolado: bool, detalle_beta: str, detalle_z: str, formula_beta: bool,
    formula_z: bool,
) -> Resultado:
    base = formar_franjas(
        proyecto.puntos_terreno, proyecto.cota_agua_m, proyecto.numero_franjas,
    )
    refinadas = formar_franjas(
        proyecto.puntos_terreno, proyecto.cota_agua_m, proyecto.numero_franjas * 2,
    )
    suma_base = sum(f.tirante_m ** (5 / 3) * f.ancho_m for f in base)
    suma_refinada = sum(f.tirante_m ** (5 / 3) * f.ancho_m for f in refinadas)
    error = abs(suma_refinada - suma_base) / suma_refinada
    evaluacion = evaluar_franjas(
        refinadas, proyecto.caudal_m3s, proyecto.diametro_medio_mm,
        beta, mu, z, proyecto.cota_agua_m,
    )
    velocidad = _positivo_finito(proyecto.caudal_m3s / evaluacion.area_m2, "Velocidad Q/A")
    avisos = _advertencias(
        proyecto, velocidad, detalle_mu, interpolado, evaluacion.puntos,
        formula_beta, formula_z,
    )
    avisos.append(
        "Reparto por franjas con K=1 según fuente DGA/MOP complementaria; alpha se "
        "deriva del cierre de caudal y mu se aplica una sola vez en la ecuación LL."
    )
    if error > TOLERANCIA_REFINAMIENTO:
        avisos.append(
            f"El control N/2N difiere {error:.6g}, mayor que 0.001; aumente las franjas "
            "base. Es un control numérico, no una regla MTC."
        )
    primero = evaluacion.puntos[0]
    return Resultado(
        proyecto, evaluacion.alpha, beta, mu, 1.0, z, evaluacion.area_m2,
        evaluacion.tirante_medio_potencial_m, velocidad,
        primero.caudal_unitario_m2s, evaluacion.denominador, evaluacion.exponente,
        evaluacion.puntos, tuple(avisos), FUENTES, detalle_mu, "irregular",
        evaluacion.ancho_mojado_m, len(refinadas), evaluacion.cierre_caudal_m3s,
        error, evaluacion.suma_reparto, detalle_beta=detalle_beta, detalle_z=detalle_z,
    )


def calcular_proyecto(proyecto: Proyecto) -> Resultado:
    """Devolver una evaluación inmutable o ValueError, sin IO ni estado compartido."""
    validar_proyecto(proyecto)
    beta = seleccionar_beta(proyecto.periodo_retorno_anios)
    z = seleccionar_z(proyecto.diametro_medio_mm)
    seleccion = seleccionar_mu(
        proyecto.sin_obstaculos, proyecto.velocidad_m_s, proyecto.luz_libre_m,
    )
    argumentos = (
        proyecto, beta.valor, seleccion.valor, z.valor, seleccion.detalle,
        seleccion.interpolado, beta.detalle, z.detalle, beta.por_formula, z.por_formula,
    )
    if proyecto.tipo_seccion == "irregular":
        return _calcular_irregular(*argumentos)
    return _calcular_rectangular(*argumentos)
