"""Presentación de cada cálculo: expresión, leyenda, sustitución y resultado."""
from datetime import datetime

from socavacion_ll import __version__

from .ecuaciones import es_formula


def n(valor: float) -> str:
    return format(valor, ".12g")


def portada(agregar, resultado, seccion, cinta):
    proyecto = resultado.proyecto
    agregar("marca", "INGENIERÍA HIDRÁULICA")
    agregar("titulo", "Memoria de cálculo\nde socavación general")
    agregar("cinta", cinta)
    agregar("rotulo", "DOCUMENTO TÉCNICO DE CÁLCULO")
    filas = (
        ("Proyecto", proyecto.nombre),
        ("Ubicación", proyecto.ubicacion or "No consignada"),
        ("Responsable", proyecto.responsable or "No consignado"),
        ("Sección", seccion),
        ("Norma principal", "MTC HHD 2011, ecuación 59, p. 108"),
        ("Método", "Lischtvan–Levediev, suelo no cohesivo, agua clara"),
        ("Versión del programa", __version__),
        ("Fecha de emisión", datetime.now().strftime("%d/%m/%Y")),
    )
    agregar("tabla", (("Dato", "Descripción"), filas, (5.2, 11.8)))
    agregar("nota", (
        "La presente memoria desarrolla las expresiones, leyendas, sustituciones "
        "numéricas, resultados y criterios técnicos de la socavación general. "
        "El resultado requiere revisión del ingeniero responsable; no determina "
        "la cimentación del puente."))
    agregar("salto", "")


def indice(agregar, filas):
    agregar("subtitulo", "Contenido")
    agregar("parrafo", (
        "La memoria se organiza siguiendo la secuencia del cálculo. Los títulos "
        "conservan estilos jerárquicos de Word para permitir navegación desde "
        "el panel de títulos."))
    agregar("tabla", (("Sección", "Contenido desarrollado"), tuple(filas), (2.4, 14.6)))
    agregar("salto", "")


def identificacion(agregar, proyecto):
    """La línea de notas queda antes del capítulo de datos: la memoria larga se verifica así."""
    agregar("subtitulo", "1. Identificación del proyecto")
    for etiqueta, valor in (("Proyecto", proyecto.nombre),
                            ("Ubicación", proyecto.ubicacion),
                            ("Responsable", proyecto.responsable)):
        agregar("parrafo", f"{etiqueta}: {valor or 'No consignado'}")
    agregar("parrafo", "Notas: " + (proyecto.notas or "No consignado"))


def paso(agregar, titulo, formulas, leyenda, sustitucion, resultado, comentario, referencia):
    agregar("apartado", titulo)
    verbo = ("emplean las siguientes expresiones" if len(formulas) > 1
             else "emplea la siguiente expresión")
    agregar("parrafo", f"Para desarrollar este cálculo se {verbo}:")
    for formula in formulas:
        agregar("ecuacion", formula)
    agregar("rotulo", "Donde:")
    for item in leyenda:
        agregar("viñeta", item)
    agregar("rotulo", "Reemplazando los valores correspondientes:")
    for linea in sustitucion:
        agregar("ecuacion" if es_formula(linea) else "parrafo", linea)
    agregar("conclusion", resultado)
    if comentario:
        agregar("parrafo", comentario)
    if referencia:
        agregar("referencia", referencia)
