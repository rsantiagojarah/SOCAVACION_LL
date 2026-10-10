"""Memoria PDF con el mismo desarrollo que la memoria Word."""
from pathlib import Path
from xml.sax.saxutils import escape

import matplotlib
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable, Image, KeepTogether, LongTable, PageBreak, Paragraph, SimpleDocTemplate,
    Spacer, TableStyle,
)

from .atomico import guardar_atomico
from .contenido import grafico_png, preparar_contenido

TEAL = colors.HexColor("#155E75")
NAVY = colors.HexColor("#173746")
GRIS = colors.HexColor("#61737D")


def _registrar_fuentes():
    windows = Path(r"C:\Windows\Fonts")
    pares = (("LLNormal", windows / "ARIALN.TTF"),
             ("LLNegrita", windows / "ARIALNB.TTF"),
             ("LLCursiva", windows / "ARIALNI.TTF"))
    if not all(ruta.is_file() for _, ruta in pares):
        carpeta = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
        pares = (("LLNormal", carpeta / "DejaVuSans.ttf"),
                 ("LLNegrita", carpeta / "DejaVuSans-Bold.ttf"),
                 ("LLCursiva", carpeta / "DejaVuSans-Oblique.ttf"))
    for nombre, ruta in pares:
        if nombre not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(nombre, str(ruta)))


def preparar_estilos():
    _registrar_fuentes()
    base = ParagraphStyle("Cuerpo", fontName="LLNormal", fontSize=11, leading=16,
                          spaceAfter=4, textColor=colors.black, alignment=TA_JUSTIFY,
                          splitLongWords=True)
    return {
        "parrafo": base,
        "parrafo_entero": base,
        "titulo": ParagraphStyle("Titulo", parent=base, fontName="LLNegrita",
                                 fontSize=22, leading=26, alignment=TA_CENTER,
                                 spaceBefore=28, spaceAfter=8),
        "subtitulo": ParagraphStyle("Seccion", parent=base, fontName="LLNegrita",
                                    fontSize=11, leading=16, spaceBefore=14,
                                    spaceAfter=6, textColor=colors.black),
        "apartado": ParagraphStyle("Apartado", parent=base, fontName="LLNegrita",
                                   fontSize=11, leading=16, spaceBefore=10, spaceAfter=4),
        "marca": ParagraphStyle("Marca", parent=base, fontName="LLNegrita",
                                textColor=TEAL, alignment=0, spaceAfter=2),
        "cinta": ParagraphStyle("Cinta", parent=base, textColor=GRIS,
                                alignment=TA_CENTER, spaceAfter=8),
        "rotulo": ParagraphStyle("Rotulo", parent=base, fontName="LLNegrita",
                                 textColor=TEAL, spaceBefore=4, spaceAfter=2),
        "nota": ParagraphStyle("Nota", parent=base, fontName="LLCursiva",
                               textColor=GRIS, spaceBefore=10),
        "viñeta": ParagraphStyle("Vineta", parent=base, leftIndent=12,
                                 textColor=NAVY, spaceAfter=2),
        "conclusion": ParagraphStyle("Conclusion", parent=base, textColor=NAVY,
                                     spaceBefore=4, spaceAfter=4),
        "referencia": ParagraphStyle("Referencia", parent=base, textColor=GRIS,
                                     spaceBefore=2, spaceAfter=8),
        "ecuacion": ParagraphStyle("Ecuacion", parent=base, fontSize=11, leading=16,
                                   leftIndent=18, rightIndent=12,
                                   alignment=TA_JUSTIFY, spaceBefore=2, spaceAfter=4),
        "celda": ParagraphStyle("Celda", parent=base, fontSize=11, leading=14,
                                spaceAfter=0, alignment=TA_JUSTIFY),
        "numero": ParagraphStyle("Numero", parent=base, fontSize=11, leading=14,
                                 spaceAfter=0, alignment=TA_JUSTIFY),
    }


def parrafo(texto, estilo):
    return Paragraph(escape(str(texto)).replace("\n", "<br/>"), estilo)


def agregar_tabla(contenido, estilos):
    cabecera, filas, anchos = contenido
    anchos = [float(ancho) for ancho in anchos]
    if sum(anchos) > 15.8:
        anchos = [ancho * 15.8 / sum(anchos) for ancho in anchos]
    estilo = estilos["numero"] if len(cabecera) > 3 else estilos["celda"]
    datos = [[parrafo(celda, estilo) for celda in fila] for fila in (cabecera, *filas)]
    tabla = LongTable(datos, colWidths=[ancho * cm for ancho in anchos],
                      repeatRows=1, hAlign="LEFT", spaceAfter=8)
    comandos = [
        ("GRID", (0, 0), (-1, -1), 0.4, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9D9D9")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("FONTNAME", (0, 0), (-1, 0), "LLNegrita"),
    ]
    for fila in range(2, len(datos), 2):
        comandos.append(("BACKGROUND", (0, fila), (-1, fila), colors.HexColor("#F5F7F8")))
    tabla.setStyle(TableStyle(comandos))
    return tabla


def numerar_pagina(lienzo, documento):
    lienzo.saveState()
    if documento.page > 1:
        lienzo.setFillColor(TEAL)
        lienzo.setFont("LLNegrita", 11)
        lienzo.drawRightString(A4[0] - 2.54 * cm, A4[1] - 1.35 * cm,
                               "MEMORIA DE CÁLCULO · SOCAVACIÓN")
        lienzo.setStrokeColor(colors.HexColor("#B7C6CC"))
        lienzo.setLineWidth(0.6)
        lienzo.line(2.54 * cm, A4[1] - 1.5 * cm, A4[0] - 2.54 * cm, A4[1] - 1.5 * cm)
    lienzo.setFillColor(GRIS)
    lienzo.setFont("LLNormal", 11)
    lienzo.drawRightString(A4[0] - 2.54 * cm, 1.15 * cm,
                           f"INGENIERÍA HIDRÁULICA  ·  {documento.page}")
    lienzo.restoreState()


def _html(bloque, estilos):
    if bloque.tipo == "viñeta":
        variable, separador, descripcion = str(bloque.contenido).partition(":")
        if separador:
            html = f"• <b>{escape(variable.strip())} = </b>{escape(descripcion.strip())}"
        else:
            html = "• " + escape(str(bloque.contenido))
        return Paragraph(html, estilos["viñeta"])
    if bloque.tipo == "conclusion":
        html = f"Por lo tanto, <b>{escape(str(bloque.contenido))}</b>"
        return Paragraph(html, estilos["conclusion"])
    if bloque.tipo == "referencia":
        html = f"<b>Referencia normativa: </b><i>{escape(str(bloque.contenido))}</i>"
        return Paragraph(html, estilos["referencia"])
    if bloque.tipo == "ecuacion":
        return Paragraph(_html_formula(str(bloque.contenido)), estilos["ecuacion"])
    return parrafo(bloque.contenido, estilos[bloque.tipo])


def _html_formula(texto: str) -> str:
    texto = texto.replace("*", " · ").replace(" - ", " − ")
    while "  " in texto:
        texto = texto.replace("  ", " ")
    salida, indice = [], 0
    while indice < len(texto):
        if texto[indice] == "_" and indice + 1 < len(texto) and texto[indice + 1].isalnum():
            fin = indice + 1
            while fin < len(texto) and texto[fin].isalnum():
                fin += 1
            salida.append(f"<sub>{escape(texto[indice + 1:fin])}</sub>")
            indice = fin
        elif texto[indice] == "^" and indice + 1 < len(texto) and texto[indice + 1] == "(":
            profundidad, fin = 0, indice + 1
            while fin < len(texto):
                profundidad += texto[fin] == "("
                profundidad -= texto[fin] == ")"
                fin += 1
                if profundidad == 0:
                    break
            salida.append(f"<super>{_html_formula(texto[indice + 2:fin - 1])}</super>")
            indice = fin
        elif texto[indice] == "^":
            fin = indice + 1
            while fin < len(texto) and texto[fin] not in " =+−·":
                fin += 1
            salida.append(f"<super>{escape(texto[indice + 1:fin])}</super>")
            indice = fin
        else:
            salida.append(escape(texto[indice]))
            indice += 1
    return "".join(salida)


def exportar_pdf(ruta, resultado):
    estilos = preparar_estilos()
    elementos = []
    for bloque in preparar_contenido(resultado):
        if bloque.tipo == "salto":
            elementos.append(PageBreak())
        elif bloque.tipo == "tabla":
            elementos.append(agregar_tabla(bloque.contenido, estilos))
        elif bloque.tipo == "grafico":
            elementos.append(Image(grafico_png(resultado), width=15.8 * cm,
                                   height=15.8 * cm * 3.5 / 7.1))
            elementos.append(Spacer(1, 8))
        elif bloque.tipo == "marca":
            elementos.append(parrafo(bloque.contenido, estilos["marca"]))
            elementos.append(HRFlowable(width="100%", thickness=1.5, color=TEAL,
                                        spaceBefore=0, spaceAfter=8))
        elif bloque.tipo == "parrafo_entero":
            elementos.append(KeepTogether([parrafo(bloque.contenido, estilos["parrafo"])]))
        else:
            elementos.append(_html(bloque, estilos))

    def escribir(temporal):
        documento = SimpleDocTemplate(
            str(temporal), pagesize=A4, leftMargin=2.54 * cm, rightMargin=2.54 * cm,
            topMargin=2.54 * cm, bottomMargin=2.2 * cm,
            title="Memoria de cálculo de socavación general",
            author=resultado.proyecto.responsable,
        )
        documento.build(elementos, onFirstPage=numerar_pagina, onLaterPages=numerar_pagina)

    guardar_atomico(ruta, escribir)
