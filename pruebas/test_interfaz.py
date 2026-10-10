"""Regresión del estilo aprobado y navegación de la versión funcional."""
import os
from pathlib import Path
import sys
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from PySide6.QtCore import Qt
from PySide6.QtGui import QFontDatabase, QFontMetrics, QPalette
from PySide6.QtWidgets import QApplication, QAbstractItemView, QLineEdit

from socavacion_ll.presentacion.ventana import VentanaPrincipal


class PruebasInterfaz(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.aplicacion = QApplication.instance() or QApplication([])
        for archivo in ("segoeui.ttf", "segoeuib.ttf", "seguisym.ttf"):
            ruta = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / archivo
            if ruta.exists():
                QFontDatabase.addApplicationFont(str(ruta))

    def setUp(self):
        self.ventana = VentanaPrincipal()
        self.ventana.show()
        self.aplicacion.processEvents()

    def tearDown(self):
        self.ventana.close()
        self.ventana.deleteLater()
        self.aplicacion.processEvents()

    def test_paleta_y_tipografia_de_referencia(self):
        paleta = self.aplicacion.palette()
        self.assertEqual(paleta.color(QPalette.ColorRole.Window).name(), "#11151b")
        self.assertEqual(paleta.color(QPalette.ColorRole.Link).name(), "#25b9c4")
        self.assertEqual(self.aplicacion.font().family(), "Segoe UI")
        self.assertEqual(self.aplicacion.font().pixelSize(), 11)

    def test_datos_y_resultados_visibles_en_la_misma_ventana(self):
        self.ventana.resize(1360, 720)
        self.aplicacion.processEvents()
        self.assertTrue(self.ventana.pagina_ingreso.isVisible())
        self.assertTrue(self.ventana.pagina_resultados.isVisible())
        self.assertTrue(self.ventana.pagina_nucleo.isVisible())
        self.assertFalse(hasattr(self.ventana, "navegacion"))
        self.assertIn("Sin resultados", self.ventana.pagina_resultados.estado.text())

    def test_acciones_de_proyecto_activas_y_reportes_sin_calculo_bloqueados(self):
        for nombre in ("Nuevo", "Abrir", "Guardar", "Calcular", "Ejemplo"):
            with self.subTest(accion=nombre):
                self.assertTrue(self.ventana.acciones[nombre].isEnabled())
        for nombre in ("Word", "PDF"):
            self.assertFalse(self.ventana.acciones[nombre].isEnabled())
        self.assertNotIn("Resultados", self.ventana.acciones)

    def test_entradas_editables_y_resultados_solo_lectura(self):
        campos = self.ventana.pagina_ingreso.findChildren(QLineEdit)
        self.assertGreater(len(campos), 6)
        self.assertTrue(all(not campo.isReadOnly() for campo in campos))
        tabla = self.ventana.pagina_resultados.tabla
        self.assertEqual(tabla.editTriggers(), QAbstractItemView.EditTrigger.NoEditTriggers)
        for fila in range(tabla.rowCount()):
            for columna in range(tabla.columnCount()):
                self.assertFalse(tabla.item(fila, columna).flags() & Qt.ItemFlag.ItemIsEditable)

    def test_paneles_y_tamanos_compactos(self):
        self.assertFalse(hasattr(self.ventana, "cabecera"))
        self.assertEqual(self.ventana.barra_acciones.height(), 38)
        self.assertEqual(self.ventana.statusBar().height(), 24)
        self.ventana.resize(1360, 720)
        self.aplicacion.processEvents()
        self.assertEqual(self.ventana.divisor.count(), 2)
        self.assertTrue(all(ancho > 0 for ancho in self.ventana.divisor.sizes()))

    def test_modulos_maximo_250_lineas_y_sin_dependencia_metrados(self):
        for ruta in [*(RAIZ / "src").rglob("*.py"), RAIZ / "iniciar_interfaz.py"]:
            with self.subTest(modulo=str(ruta.relative_to(RAIZ))):
                contenido = ruta.read_text(encoding="utf-8")
                self.assertLessEqual(len(contenido.splitlines()), 250)
                self.assertNotIn("from metrado", contenido)
                self.assertNotIn("import metrado", contenido)

    def test_titulo_de_proyecto_cabe_en_la_barra(self):
        self.ventana.resize(1360, 720)
        self.aplicacion.processEvents()
        rotulo = self.ventana.titulo_proyecto
        self.assertFalse(rotulo.wordWrap())
        ancho_texto = QFontMetrics(rotulo.font()).horizontalAdvance(rotulo.text())
        self.assertLessEqual(ancho_texto, rotulo.width())


if __name__ == "__main__":
    unittest.main()
