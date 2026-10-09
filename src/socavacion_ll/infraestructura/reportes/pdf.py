"""Memoria PDF con texto escapado, fuentes Unicode y tablas multipágina."""
from pathlib import Path
from xml.sax.saxutils import escape

import matplotlib
from socavacion_ll import __version__
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image, KeepTogether, LongTable, Paragraph, SimpleDocTemplate, Spacer, TableStyle,
)

from .atomico import guardar_atomico
from .contenido import grafico_png, preparar_contenido


def preparar_estilos():
    carpeta = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
    for nombre, archivo in (("LLNormal", "DejaVuSans.ttf"),
                            ("LLNegrita", "DejaVuSans-Bold.ttf")):
        if nombre not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(nombre, str(carpeta / archivo)))
    base = ParagraphStyle("Cuerpo", fontName="LLNormal", fontSize=10, leading=14,
                          spaceAfter=6, textColor=colors.black, splitLongWords=True)
    return {
        "parrafo": base,
        "titulo": ParagraphStyle("Titulo", parent=base, fontName="LLNegrita",
                                  fontSize=17, leading=22, spaceAfter=12),
        "subtitulo": ParagraphStyle("Seccion", parent=base, fontName="LLNegrita",
                                     fontSize=12, leading=16, spaceBefore=12,
                                     spaceAfter=7, keepWithNext=True),
        "ecuacion": ParagraphStyle("Ecuacion", parent=base, fontSize=8.5, leading=12),
        "celda": ParagraphStyle("Celda", parent=base, fontSize=8.5, leading=11, spaceAfter=0),
        "numero": ParagraphStyle("Numero", parent=base, fontSize=7.5, leading=10,
                                  spaceAfter=0, alignment=TA_CENTER),
    }


def parrafo(texto, estilo):
    return Paragraph(escape(str(texto)).replace("\n", "<br/>"), estilo)


def agregar_tabla(contenido, estilos):
    cabecera, filas, anchos = contenido
    estilo = estilos["numero"] if len(cabecera) > 3 else estilos["celda"]
    datos = [[parrafo(celda, estilo) for celda in fila] for fila in (cabecera, *filas)]
    tabla = LongTable(datos, colWidths=[ancho * cm for ancho in anchos],
                      repeatRows=1, hAlign="LEFT", spaceAfter=10)
    tabla.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D9D9D9")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EEF1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return tabla


def numerar_pagina(lienzo, documento):
    lienzo.saveState()
    lienzo.setFont("LLNormal", 8)
    lienzo.drawRightString(A4[0] - 2 * cm, 1.2 * cm,
                          f"Socavación LL {__version__} | Página {documento.page}")
    lienzo.restoreState()


def exportar_pdf(ruta, resultado):
    estilos = preparar_estilos()
    elementos = []
    for bloque in preparar_contenido(resultado):
        if bloque.tipo == "tabla":
            elementos.append(agregar_tabla(bloque.contenido, estilos))
        elif bloque.tipo == "grafico":
            elementos.append(Image(grafico_png(resultado), width=17 * cm,
                                   height=17 * cm * 3.5 / 7.1))
            elementos.append(Spacer(1, 8))
        elif bloque.tipo == "parrafo_entero":
            elementos.append(KeepTogether([parrafo(bloque.contenido, estilos["parrafo"])]))
        else:
            elementos.append(parrafo(bloque.contenido, estilos[bloque.tipo]))

    def escribir(temporal):
        documento = SimpleDocTemplate(
            str(temporal), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
            topMargin=2 * cm, bottomMargin=2 * cm,
            title="Memoria de cálculo de socavación general",
            author=resultado.proyecto.responsable,
        )
        documento.build(elementos, onFirstPage=numerar_pagina, onLaterPages=numerar_pagina)

    guardar_atomico(ruta, escribir)
