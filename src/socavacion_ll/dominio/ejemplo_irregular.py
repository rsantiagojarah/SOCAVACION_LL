"""Caso didáctico de una sección irregular con fondo variable."""
from .modelos import Proyecto, PuntoTerreno

PERFIL_EJEMPLO_IRREGULAR = (
    PuntoTerreno(0, 108),
    PuntoTerreno(15, 107.2),
    PuntoTerreno(30, 106),
    PuntoTerreno(40, 104.8),
    PuntoTerreno(48, 102.4),
    PuntoTerreno(56, 101.6),
    PuntoTerreno(64, 101.1),
    PuntoTerreno(72, 100.2),
    PuntoTerreno(80, 100.9),
    PuntoTerreno(88, 100.4),
    PuntoTerreno(96, 101.8),
    PuntoTerreno(104, 102.8),
    PuntoTerreno(112, 105.2),
    PuntoTerreno(124, 107),
    PuntoTerreno(140, 108.5),
)


def proyecto_ejemplo_irregular() -> Proyecto:
    """Sección didáctica: una rama mojada a la cota 103 m y V = Q/A = 2 m/s."""
    return Proyecto(
        nombre="Ejemplo de terreno variable",
        ubicacion="Caso didáctico",
        responsable="Por completar",
        notas=(
            "Ejemplo aritmético de sección irregular; no corresponde a una obra real. "
            "Con la cota de agua 103 m hay una sola rama mojada y las bermas quedan secas. "
            "El fondo tiene dos vaguadas y un lomo intermedio. "
            "El caudal se fijó para que la velocidad Q/A sea 2 m/s."
        ),
        caudal_m3s=2996 / 15,
        periodo_retorno_anios=100,
        cota_agua_m=103,
        velocidad_m_s=2,
        pendiente_m_m=0.001,
        diametro_medio_mm=1,
        no_cohesivo=True,
        tipo_seccion="irregular",
        puntos_terreno=PERFIL_EJEMPLO_IRREGULAR,
        numero_franjas=24,
    )
