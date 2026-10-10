"""Exportaciones reales, contenido trazable y gráfico sin dependencia de Qt."""
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree
from zipfile import ZipFile

from pypdf import PdfReader

from socavacion_ll.dominio.modelos import (
    PuntoResultado, Resultado, proyecto_ejemplo,
)
from socavacion_ll.calculo.motor import calcular_proyecto
from socavacion_ll.infraestructura.graficos import crear_figura
from socavacion_ll.infraestructura.reportes import exportar_pdf, exportar_word
from socavacion_ll.infraestructura.reportes.contenido import preparar_contenido


def resultado_ejemplo(numero=11, negativo=False):
    proyecto = replace(proyecto_ejemplo(), numero_puntos=numero)
    hs = 2.0 if negativo else 4.736513861635
    puntos = tuple(PuntoResultado(
        20 * indice / (numero - 1), 100.0, 3.0, hs, hs - 3.0,
        103.0 - hs, min(100.0, 103.0 - hs),
    ) for indice in range(numero))
    return Resultado(
        proyecto, 0.961499713538, 1.0, 1.0, 1.0, 0.4, 60.0, 3.0,
        2.0, 6.0, 0.68, 1 / 1.4, puntos,
        ("Sin profundización predicha; no implica sedimentación.",) if negativo else (),
        ("MTC HHD 2011, ecuación 59, p. 108.",
         "MTC Manual de Puentes 2018, p. impresa 47 / PDF 51.",
         "DGA MOP 2022, tablas 7-1 y 7-2, p. 69 / PDF 79.",
         "Schreider y colaboradores 2001, ecuación 1, p. 16."),
    )


class PruebasReportes(unittest.TestCase):
    def test_interpolacion_mu_es_trazable_en_contenido_word_y_pdf(self):
        proyecto = replace(proyecto_ejemplo(), sin_obstaculos=False, luz_libre_m=27)
        resultado = calcular_proyecto(proyecto)
        contenido = "\n".join(str(bloque.contenido) for bloque in preparar_contenido(resultado))
        for texto in ("L1=25", "mu1=0.97", "L2=30", "mu2=0.98", "mu = 0.97 +",
                      "regla no publicada por MTC"):
            self.assertIn(texto, contenido)
        with tempfile.TemporaryDirectory() as carpeta:
            word = Path(carpeta) / "interpolacion.docx"
            pdf = Path(carpeta) / "interpolacion.pdf"
            exportar_word(word, resultado)
            exportar_pdf(pdf, resultado)
            with ZipFile(word) as archivo:
                texto_word = archivo.read("word/document.xml").decode("utf-8")
            texto_pdf = "\n".join(p.extract_text() for p in PdfReader(pdf).pages)
            for texto in ("L1=25", "mu1=0.97", "L2=30", "mu2=0.98", "mu = 0.97 +"):
                self.assertIn(texto, texto_word)
                self.assertIn(texto, texto_pdf)

    def test_grafico_representa_resultado_sin_recalcular(self):
        resultado = resultado_ejemplo(negativo=True)
        figura = crear_figura(resultado, oscuro=True)
        ejes = figura.axes[0]
        lineas = {linea.get_label(): linea for linea in ejes.lines}
        self.assertEqual(len(lineas), 4)
        self.assertIn("(m)", ejes.get_xlabel())
        self.assertEqual(list(lineas["Perfil LL algebraico"].get_ydata()), [101] * 11)
        self.assertEqual(list(lineas["Perfil de erosión limitado"].get_ydata()), [100] * 11)

    def test_word_contiene_ecuaciones_datos_y_grafico(self):
        resultado = resultado_ejemplo()
        resultado = replace(resultado, proyecto=replace(
            resultado.proyecto, nombre="Río <alto> & Peña", notas="Nota " * 400 + "FIN NOTAS"))
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "memoria.docx"
            exportar_word(ruta, resultado)
            with ZipFile(ruta) as archivo:
                xml = archivo.read("word/document.xml").decode()
                for texto in ("4.736514", "1.736514", "0.68", "0.28", "alpha",
                              "beta", "mu", "phi", "MTC", "Schreider", "DGA",
                              "Pendiente", "11", "no cohesivo"):
                    self.assertIn(texto, xml)
                self.assertIn("m:oMath", xml)
                self.assertIn("<m:f>", xml)
                self.assertIn("<m:sSup>", xml)
                self.assertIn("Arial Narrow", xml)
                arbol = ElementTree.fromstring(xml)
                espacio = {"m": "http://schemas.openxmlformats.org/officeDocument/2006/math"}
                formulas = arbol.findall(".//m:oMath", espacio)

                def texto_formula(formula):
                    return "".join(nodo.text or "" for nodo in formula.findall(".//m:t", espacio))

                fracciones = [len(formula.findall(".//m:f", espacio)) for formula in formulas]
                self.assertIn(2, fracciones)
                hs = next(formula for formula in formulas
                          if "0.68" in texto_formula(formula)
                          and len(formula.findall(".//m:f", espacio)) >= 3)
                self.assertEqual(len(hs.findall(".//m:sSup", espacio)), 3)
                for texto in ("Donde:", "Reemplazando los valores correspondientes:",
                              "Por lo tanto", "Referencia normativa"):
                    self.assertIn(texto, xml)
                self.assertIn("Río &lt;alto&gt; &amp; Peña", xml)
                self.assertIn("FIN NOTAS", xml)
                self.assertIn("tblHeader", xml)
                self.assertTrue(any(n.startswith("word/media/") for n in archivo.namelist()))

    def test_pdf_preserva_unicode_markup_y_todos_los_puntos(self):
        resultado = resultado_ejemplo(201)
        proyecto = replace(resultado.proyecto, nombre="Río <alto> & Peña",
                           notas="Nota extensa " * 400 + "FIN DE NOTAS")
        resultado = replace(resultado, proyecto=proyecto)
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "memoria.pdf"
            exportar_pdf(str(ruta), resultado)
            lector = PdfReader(ruta)
            texto = "\n".join(pagina.extract_text() for pagina in lector.pages)
            for fragmento in ("Río <alto> & Peña", "FIN DE NOTAS", "4.736514",
                              "201", "Schreider", "MTC", "0.68", "0.28"):
                self.assertIn(fragmento, texto)
            self.assertGreater(len(lector.pages), 4)
            self.assertTrue(any(len(pagina.images) for pagina in lector.pages))

    def test_reportes_advierten_socavacion_negativa(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "negativo.pdf"
            exportar_pdf(ruta, resultado_ejemplo(negativo=True))
            texto = "\n".join(p.extract_text() for p in PdfReader(ruta).pages)
            self.assertIn("no implica sedimentación", texto)
            self.assertIn("-1.000000", texto)
            self.assertIn("convención de presentación", texto)

    def test_error_al_reemplazar_conserva_destino_y_limpia_temporal(self):
        with tempfile.TemporaryDirectory() as carpeta:
            for exportador, extension in ((exportar_pdf, "pdf"), (exportar_word, "docx")):
                ruta = Path(carpeta) / f"existente.{extension}"
                ruta.write_bytes(b"contenido original")
                with patch("os.replace", side_effect=PermissionError("Archivo abierto")):
                    with self.assertRaises(PermissionError):
                        exportador(ruta, resultado_ejemplo())
                self.assertEqual(ruta.read_bytes(), b"contenido original")
            self.assertEqual(len(list(Path(carpeta).iterdir())), 2)

    def test_responsable_largo_se_conserva_en_cuerpo_y_acota_solo_metadato(self):
        resultado = resultado_ejemplo()
        responsable = "R" * 500
        resultado = replace(resultado, proyecto=replace(
            resultado.proyecto, responsable=responsable))
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "responsable.docx"
            exportar_word(ruta, resultado)
            with ZipFile(ruta) as archivo:
                cuerpo = archivo.read("word/document.xml").decode()
                self.assertIn(responsable, cuerpo)
                metadatos = ElementTree.fromstring(archivo.read("docProps/core.xml"))
                autor = metadatos.find("{http://purl.org/dc/elements/1.1/}creator")
                self.assertEqual(autor.text, responsable[:255])

    def test_pdf_admite_texto_largo_sin_espacios_hasta_limite_validado(self):
        resultado = resultado_ejemplo()
        resultado = replace(resultado, proyecto=replace(
            resultado.proyecto, responsable="R" * 500, notas="N" * 20000))
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "textos_largos.pdf"
            exportar_pdf(ruta, resultado)
            lector = PdfReader(ruta)
            paginas = lector.pages
            texto = "\n".join(pagina.extract_text() for pagina in paginas)
            notas = texto.split("Notas: ", 1)[1].split("Datos de entrada y geometría", 1)[0]
            notas = notas.replace("MEMORIA DE CÁLCULO · SOCAVACIÓN", "").replace("INGENIERÍA HIDRÁULICA", "")
            self.assertEqual(notas.count("N"), 20000)
            self.assertEqual(lector.metadata.author, "R" * 500)
            self.assertGreater(len(paginas), 4)


if __name__ == "__main__":
    unittest.main()
