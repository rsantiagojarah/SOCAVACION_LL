"""Presentación y memorias de una evaluación LL irregular."""
from dataclasses import replace
import os
from pathlib import Path
import sys
import tempfile
import unittest
from zipfile import ZipFile

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pypdf import PdfReader
from PySide6.QtWidgets import QApplication
from socavacion_ll.calculo.motor import calcular_proyecto
from socavacion_ll.dominio.modelos import PuntoTerreno, proyecto_ejemplo
from socavacion_ll.infraestructura.graficos import crear_figura
from socavacion_ll.infraestructura.reportes import exportar_pdf, exportar_word
from socavacion_ll.infraestructura.reportes.contenido import preparar_contenido
from socavacion_ll.presentacion.ventana import VentanaPrincipal


def resultado_irregular():
    proyecto = replace(
        proyecto_ejemplo(), nombre="Sección irregular verificada",
        tipo_seccion="irregular", numero_franjas=4,
        puntos_terreno=(PuntoTerreno(0, 104), PuntoTerreno(10, 100),
                         PuntoTerreno(20, 104)),
    )
    return calcular_proyecto(proyecto)


class PruebasReportesIrregular(unittest.TestCase):
    def test_contenido_incluye_reparto_cierre_refinamiento_y_fuentes(self):
        contenido = "\n".join(str(b.contenido) for b in preparar_contenido(resultado_irregular()))
        for texto in (
            "Sección irregular", "alpha = Q", "q_j", "Q_j", "h_j", "K=1",
            "Cierre de caudal", "Error relativo N/2N", "DGA/MOP", "no es norma MTC",
        ):
            self.assertIn(texto, contenido)

    def test_grafico_conserva_todo_el_terreno_y_perfil_en_centros(self):
        resultado = resultado_irregular()
        figura = crear_figura(resultado)
        ejes = figura.axes[0]
        lineas = {linea.get_label(): linea for linea in ejes.lines}
        self.assertEqual(list(lineas["Terreno natural"].get_xdata()), [0, 10, 20])
        self.assertEqual(list(lineas["Terreno natural"].get_ydata()), [104, 100, 104])
        self.assertEqual(len(lineas["Perfil LL algebraico"].get_xdata()),
                         resultado.numero_franjas)
        self.assertIn("irregular", ejes.get_title().lower())

    def test_word_pdf_y_tabla_de_pantalla_muestran_franjas(self):
        resultado = resultado_irregular()
        with tempfile.TemporaryDirectory() as carpeta:
            word = Path(carpeta) / "irregular.docx"
            pdf = Path(carpeta) / "irregular.pdf"
            exportar_word(word, resultado)
            exportar_pdf(pdf, resultado)
            with ZipFile(word) as archivo:
                texto_word = archivo.read("word/document.xml").decode("utf-8")
            self.assertIn("alpha", texto_word)
            self.assertIn("SUMA", texto_word)
            self.assertIn("<m:f>", texto_word)
            texto_pdf = "\n".join(p.extract_text() for p in PdfReader(pdf).pages)
            for texto in ("Sección irregular", "Caudal Q_j", "Cierre de caudal", "DGA/MOP"):
                self.assertIn(texto, texto_word)
                self.assertIn(texto, texto_pdf)
        aplicacion = QApplication.instance() or QApplication([])
        ventana = VentanaPrincipal()
        try:
            ventana.pagina_resultados.mostrar(resultado)
            self.assertEqual(ventana.pagina_resultados.tabla.columnCount(), 8)
            self.assertEqual(ventana.pagina_resultados.tabla.rowCount(), resultado.numero_franjas)
        finally:
            ventana.sesion.modificado = False
            ventana.close()
            ventana.deleteLater()
            aplicacion.processEvents()


if __name__ == "__main__":
    unittest.main()
