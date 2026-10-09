"""Memoria Word editable con tablas continuas y ecuaciones OMML nativas."""
from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from socavacion_ll import __version__

from .atomico import guardar_atomico
from .contenido import grafico_png, preparar_contenido
from .ecuaciones import agregar_ecuacion


def configurar_documento(documento):
    seccion = documento.sections[0]
    seccion.page_width, seccion.page_height = Cm(21), Cm(29.7)
    seccion.top_margin = seccion.bottom_margin = Cm(2)
    seccion.left_margin = seccion.right_margin = Cm(2)
    for nombre, tamano in (("Normal", 10), ("Title", 17), ("Heading 1", 12)):
        estilo = documento.styles[nombre]
        estilo.font.name = "Calibri"
        estilo.font.size = Pt(tamano)
        estilo.font.color.rgb = RGBColor(0, 0, 0)
        estilo.paragraph_format.space_after = Pt(6)
    documento.styles["Normal"].paragraph_format.line_spacing = 1.08
    documento.styles["Heading 1"].paragraph_format.space_before = Pt(12)
    documento.styles["Heading 1"].paragraph_format.keep_with_next = True
    titulo = documento.styles["Title"]
    propiedades_titulo = titulo.element.get_or_add_pPr()
    borde_titulo = propiedades_titulo.find(qn("w:pBdr"))
    if borde_titulo is not None:
        propiedades_titulo.remove(borde_titulo)
    pie = seccion.footer.paragraphs[0]
    pie.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    pie.add_run(f"Socavación LL {__version__} | Página ").font.size = Pt(8)
    campo = OxmlElement("w:fldSimple")
    campo.set(qn("w:instr"), "PAGE")
    pie._p.append(campo)


def agregar_tabla(documento, contenido):
    cabecera, filas, anchos = contenido
    tabla = documento.add_table(rows=1, cols=len(cabecera))
    tabla.autofit = False
    propiedades = tabla._tbl.tblPr
    bordes = OxmlElement("w:tblBorders")
    for lado in ("top", "left", "bottom", "right", "insideH", "insideV"):
        borde = OxmlElement(f"w:{lado}")
        for clave, valor in (("val", "single"), ("sz", "4"), ("color", "D9D9D9")):
            borde.set(qn(f"w:{clave}"), valor)
        bordes.append(borde)
    propiedades.append(bordes)
    margenes = OxmlElement("w:tblCellMar")
    for lado in ("top", "left", "bottom", "right"):
        margen = OxmlElement(f"w:{lado}")
        margen.set(qn("w:w"), "85")
        margen.set(qn("w:type"), "dxa")
        margenes.append(margen)
    propiedades.append(margenes)
    repetir = OxmlElement("w:tblHeader")
    tabla.rows[0]._tr.get_or_add_trPr().append(repetir)
    for indice, fila in enumerate((cabecera, *filas)):
        celdas = tabla.rows[0].cells if indice == 0 else tabla.add_row().cells
        for columna, (celda, texto, ancho) in enumerate(zip(celdas, fila, anchos)):
            tabla.columns[columna].width = Cm(ancho)
            celda.width = Cm(ancho)
            celda.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            parrafo = celda.paragraphs[0]
            parrafo.paragraph_format.space_after = Pt(1)
            parrafo.paragraph_format.line_spacing = 1.05
            if indice == 0:
                parrafo.paragraph_format.keep_with_next = True
            if len(cabecera) > 3 or columna == 1:
                parrafo.alignment = WD_ALIGN_PARAGRAPH.CENTER
            segmento = parrafo.add_run(str(texto))
            segmento.font.size = Pt(8 if len(cabecera) > 3 else 9)
            if indice == 0:
                segmento.bold = True
                fondo = OxmlElement("w:shd")
                fondo.set(qn("w:fill"), "E8EEF1")
                celda._tc.get_or_add_tcPr().append(fondo)
    documento.add_paragraph().paragraph_format.space_after = Pt(1)


def exportar_word(ruta, resultado):
    documento = Document()
    configurar_documento(documento)
    documento.core_properties.title = "Memoria de cálculo de socavación general"
    # python-docx limita a 255 caracteres el autor de las propiedades OOXML.
    # El responsable completo permanece en el cuerpo de la memoria sin recorte.
    documento.core_properties.author = resultado.proyecto.responsable[:255]
    for bloque in preparar_contenido(resultado):
        if bloque.tipo == "titulo":
            documento.add_paragraph(bloque.contenido, "Title")
        elif bloque.tipo == "subtitulo":
            documento.add_paragraph(bloque.contenido, "Heading 1")
        elif bloque.tipo == "tabla":
            agregar_tabla(documento, bloque.contenido)
        elif bloque.tipo == "ecuacion":
            agregar_ecuacion(documento, bloque.contenido)
        elif bloque.tipo == "grafico":
            documento.add_picture(grafico_png(resultado), width=Cm(17))
        else:
            documento.add_paragraph(bloque.contenido)
    guardar_atomico(ruta, documento.save)
