"""Datos SI de una sección rectangular homogénea y su evaluación LL."""
from dataclasses import dataclass


@dataclass(frozen=True)
class PuntoTerreno:
    abscisa_m: float
    cota_m: float


@dataclass(frozen=True)
class Proyecto:
    nombre: str = "Nuevo proyecto"
    ubicacion: str = ""
    responsable: str = ""
    notas: str = ""
    caudal_m3s: float = 0.0
    periodo_retorno_anios: float = 100.0
    ancho_m: float = 0.0
    cota_fondo_m: float = 0.0
    cota_agua_m: float = 0.0
    velocidad_m_s: float = 0.0
    pendiente_m_m: float = 0.0
    diametro_medio_mm: float = 1.0
    no_cohesivo: bool = False
    agua_clara: bool = True
    sin_obstaculos: bool = True
    luz_libre_m: float = 0.0
    numero_puntos: int = 11
    tipo_seccion: str = "rectangular"
    puntos_terreno: tuple[PuntoTerreno, ...] = ()
    numero_franjas: int = 20


@dataclass(frozen=True)
class PuntoResultado:
    abscisa_m: float
    cota_fondo_m: float
    tirante_m: float
    profundidad_hs_m: float
    socavacion_m: float
    cota_ll_m: float
    cota_perfil_m: float
    ancho_franja_m: float = 0.0
    area_franja_m2: float = 0.0
    caudal_unitario_m2s: float = 0.0
    caudal_franja_m3s: float = 0.0


@dataclass(frozen=True)
class Resultado:
    proyecto: Proyecto
    alpha: float
    beta: float
    mu: float
    phi: float
    z: float
    area_m2: float
    tirante_m: float
    velocidad_control_m_s: float
    numerador: float
    denominador: float
    exponente: float
    puntos: tuple[PuntoResultado, ...]
    advertencias: tuple[str, ...]
    fuentes: tuple[str, ...]
    detalle_mu: str = ""
    tipo_seccion: str = "rectangular"
    ancho_mojado_m: float = 0.0
    numero_franjas: int = 0
    cierre_caudal_m3s: float = 0.0
    error_refinamiento_relativo: float = 0.0
    suma_reparto: float = 0.0
    detalle_beta: str = ""
    detalle_z: str = ""


def proyecto_ejemplo() -> Proyecto:
    return Proyecto(
        nombre="Ejemplo rectangular verificado", ubicacion="Caso didáctico",
        responsable="Por completar",
        notas="Ejemplo aritmético; no corresponde a una obra real.",
        caudal_m3s=120.0, periodo_retorno_anios=100.0, ancho_m=20.0,
        cota_fondo_m=100.0, cota_agua_m=103.0, velocidad_m_s=2.0,
        pendiente_m_m=0.001, diametro_medio_mm=1.0, no_cohesivo=True,
    )
