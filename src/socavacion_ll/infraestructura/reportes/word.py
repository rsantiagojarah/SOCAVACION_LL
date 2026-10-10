"""Memoria Word con la letra, las tablas y las ecuaciones de la memoria del acueducto."""
from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Mm, Pt, RGBColor

from .atomico import guardar_atomico
from .contenido import grafico_png, preparar_contenido
from .ecuaciones import agregar_ecuacion

TEAL = RGBColor(0x15, 0x5E, 0x75)
NAVY = RGBColor(0x17, 0x37, 0x46)
GRIS = RGBColor(0x61, 0x73, 0x7D)
FUENTE = "Arial Narrow"
ANCHO = 158.0


def configurar_documento(documento):
    seccion = documento.sections[0]
    seccion.page_width, seccion.page_height = Mm(210), Mm(297)
    seccion.top_margin = seccion.bottom_margin = Mm(25.4)
    seccion.left_margin = seccion.right_margin = Mm(25.4)
    seccion.header_distance = Mm(12.7)
    seccion.footer_distance = Mm(12.7)
    seccion.different_first_page_header_footer = True
    for nombre, tamano, antes, negrita in (
            ("Normal", 11, 0, False), ("Title", 22, 28, True),
            ("Heading 1", 11, 14, True), ("Heading 2", 11, 10, True)):
        _estilo(documento.styles[nombre], tamano, antes, negrita)
    documento.styles["Title"].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    documento.styles["Title"].paragraph_format.line_spacing = 1.0
    for nombre in ("Heading 1", "Heading 2"):
        documento.styles[nombre].paragraph_format.keep_with_next = True
    if "Equation" not in documento.styles:
        documento.styles.add_style("Equation", WD_STYLE_TYPE.PARAGRAPH)
    ecuacion = documento.styles["Equation"]
    _estilo(ecuacion, 11, 2, False)
    ecuacion.paragraph_format.left_indent = Mm(7)
    ecuacion.paragraph_format.right_indent = Mm(5)
    viñeta = documento.styles["List Bullet"]
    _estilo(viñeta, 11, 0, False)
    viñeta.paragraph_format.left_indent = Mm(11)
    viñeta.paragraph_format.first_line_indent = Mm(-5)
    _encabezado(seccion.header.paragraphs[0])
    _pie(seccion.footer.paragraphs[0])


def _estilo(estilo, tamano, antes, negrita):
    estilo.font.name = FUENTE
    estilo.font.size = Pt(tamano)
    estilo.font.bold = negrita
    estilo.font.color.rgb = RGBColor(0, 0, 0)
    estilo.paragraph_format.space_before = Pt(antes)
    estilo.paragraph_format.space_after = Pt(4 if tamano == 11 else 8)
    estilo.paragraph_format.line_spacing = 1.5
    estilo.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    fuentes = estilo.element.get_or_add_rPr().get_or_add_rFonts()
    for tema in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
        if qn(tema) in fuentes.attrib:
            del fuentes.attrib[qn(tema)]
    for atributo in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        fuentes.set(qn(atributo), FUENTE)


def _encabezado(parrafo):
    parrafo.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    _run(parrafo, "MEMORIA DE CÁLCULO · SOCAVACIÓN", negrita=True, color=TEAL)
    _borde_inferior(parrafo, "B7C6CC", "6")


def _pie(parrafo):
    parrafo.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    _run(parrafo, "INGENIERÍA HIDRÁULICA  ·  ", color=GRIS)
    campo = OxmlElement("w:fldSimple")
    campo.set(qn("w:instr"), "PAGE")
    parrafo._p.append(campo)


def _borde_inferior(parrafo, color, tamano):
    borde = OxmlElement("w:pBdr")
    inferior = OxmlElement("w:bottom")
    for clave, valor in (("val", "single"), ("sz", tamano), ("space", "1"), ("color", color)):
        inferior.set(qn(f"w:{clave}"), valor)
    borde.append(inferior)
    parrafo._p.get_or_add_pPr().append(borde)


def _run(parrafo, texto, *, negrita=False, cursiva=False, color=None, tamano=11):
    segmento = parrafo.add_run(texto)
    segmento.font.name = FUENTE
    segmento.font.size = Pt(tamano)
    segmento.bold = negrita
    segmento.italic = cursiva
    segmento.font.color.rgb = color or RGBColor(0, 0, 0)
    fuentes = segmento._element.get_or_add_rPr().get_or_add_rFonts()
    for atributo in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        fuentes.set(qn(atributo), FUENTE)
    return segmento


def agregar_tabla(documento, contenido):
    cabecera, filas, anchos = contenido
    anchos = [float(ancho) * 10 for ancho in anchos]
    total = sum(anchos)
    if total > ANCHO:
        anchos = [ancho * ANCHO / total for ancho in anchos]
    tabla = documento.add_table(rows=1, cols=len(cabecera))
    tabla.alignment = WD_TABLE_ALIGNMENT.CENTER
    tabla.autofit = False
    tabla.style = "Table Grid"
    tabla.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))
    for indice, fila in enumerate((cabecera, *filas)):
        celdas = tabla.rows[0].cells if indice == 0 else tabla.add_row().cells
        for celda, texto, ancho in zip(celdas, fila, anchos):
            celda.width = Mm(ancho)
            celda.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if indice == 0 or indice % 2 == 0:
                fondo = OxmlElement("w:shd")
                fondo.set(qn("w:fill"), "D9D9D9" if indice == 0 else "F5F7F8")
                celda._tc.get_or_add_tcPr().append(fondo)
            parrafo = celda.paragraphs[0]
            parrafo.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            parrafo.paragraph_format.line_spacing = 1.5
            parrafo.paragraph_format.space_after = Pt(0)
            _run(parrafo, str(texto), negrita=indice == 0)
    _geometria(tabla, anchos)
    documento.add_paragraph().paragraph_format.space_after = Pt(0)


def _geometria(tabla, anchos):
    twips = tuple(round(ancho * 56.692913) for ancho in anchos)
    propiedades = tabla._tbl.tblPr
    ancho = propiedades.find(qn("w:tblW"))
    if ancho is None:
        ancho = OxmlElement("w:tblW")
        propiedades.append(ancho)
    ancho.set(qn("w:type"), "dxa")
    ancho.set(qn("w:w"), str(sum(twips)))
    diseno = propiedades.find(qn("w:tblLayout"))
    if diseno is None:
        diseno = OxmlElement("w:tblLayout")
        propiedades.append(diseno)
    diseno.set(qn("w:type"), "fixed")
    grilla = tabla._tbl.tblGrid
    for hijo in list(grilla):
        grilla.remove(hijo)
    for medida in twips:
        columna = OxmlElement("w:gridCol")
        columna.set(qn("w:w"), str(medida))
        grilla.append(columna)


def _viñeta(documento, texto):
    parrafo = documento.add_paragraph(style="List Bullet")
    variable, separador, descripcion = str(texto).partition(":")
    if separador:
        _run(parrafo, variable.strip() + " = ", negrita=True, color=NAVY)
        _run(parrafo, descripcion.strip(), color=NAVY)
    else:
        _run(parrafo, str(texto), color=NAVY)


def _titulo(documento, texto):
    parrafo = documento.add_paragraph(style="Title")
    parrafo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    parrafo.paragraph_format.line_spacing = 1.0
    for indice, linea in enumerate(str(texto).split("\n")):
        if indice:
            parrafo.add_run().add_break()
        _run(parrafo, linea, negrita=True, tamano=22)


def exportar_word(ruta, resultado):
    documento = Document()
    configurar_documento(documento)
    documento.core_properties.title = "Memoria de cálculo de socavación general"
    documento.core_properties.author = resultado.proyecto.responsable[:255]
    for bloque in preparar_contenido(resultado):
        _bloque(documento, bloque, resultado)
    guardar_atomico(ruta, documento.save)


def _bloque(documento, bloque, resultado):
    if bloque.tipo == "salto":
        documento.add_page_break()
    elif bloque.tipo == "titulo":
        _titulo(documento, bloque.contenido)
    elif bloque.tipo == "subtitulo":
        documento.add_heading(str(bloque.contenido), level=1)
    elif bloque.tipo == "apartado":
        documento.add_heading(str(bloque.contenido), level=2)
    elif bloque.tipo == "marca":
        parrafo = documento.add_paragraph()
        _run(parrafo, str(bloque.contenido), negrita=True, color=TEAL)
        _borde_inferior(parrafo, "155E75", "16")
    elif bloque.tipo == "cinta":
        parrafo = documento.add_paragraph()
        parrafo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        _run(parrafo, str(bloque.contenido), color=GRIS)
    elif bloque.tipo == "rotulo":
        parrafo = documento.add_paragraph()
        _run(parrafo, str(bloque.contenido), negrita=True, color=TEAL)
    elif bloque.tipo == "nota":
        parrafo = documento.add_paragraph()
        _run(parrafo, str(bloque.contenido), cursiva=True, color=GRIS)
    elif bloque.tipo == "viñeta":
        _viñeta(documento, bloque.contenido)
    elif bloque.tipo == "conclusion":
        parrafo = documento.add_paragraph()
        _run(parrafo, "Por lo tanto, ", color=NAVY)
        _run(parrafo, str(bloque.contenido), negrita=True, color=NAVY)
    elif bloque.tipo == "referencia":
        parrafo = documento.add_paragraph()
        _run(parrafo, "Referencia normativa: ", negrita=True, color=GRIS)
        _run(parrafo, str(bloque.contenido), cursiva=True, color=GRIS)
    elif bloque.tipo == "tabla":
        agregar_tabla(documento, bloque.contenido)
    elif bloque.tipo == "ecuacion":
        agregar_ecuacion(documento, bloque.contenido)
    elif bloque.tipo == "grafico":
        parrafo = documento.add_paragraph()
        parrafo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        parrafo.add_run().add_picture(grafico_png(resultado), width=Mm(ANCHO))
    else:
        parrafo = documento.add_paragraph()
        parrafo.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        parrafo.paragraph_format.line_spacing = 1.5
        _run(parrafo, str(bloque.contenido))
