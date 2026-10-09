"""Interfaz de ingreso y vigencia para una sección irregular."""
from dataclasses import replace
import os
from pathlib import Path
import sys
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PySide6.QtWidgets import QApplication
from socavacion_ll.dominio.modelos import PuntoTerreno, proyecto_ejemplo
from socavacion_ll.presentacion.ventana import VentanaPrincipal


def proyecto_irregular():
    return replace(
        proyecto_ejemplo(), tipo_seccion="irregular", numero_franjas=16,
        puntos_terreno=(PuntoTerreno(0, 104), PuntoTerreno(10, 100),
                         PuntoTerreno(20, 104)),
    )


class PruebasInterfazIrregular(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.aplicacion = QApplication.instance() or QApplication([])

    def setUp(self):
        self.ventana = VentanaPrincipal()

    def tearDown(self):
        self.ventana.sesion.modificado = False
        self.ventana.close()
        self.ventana.deleteLater()
        self.aplicacion.processEvents()

    def test_carga_tipo_puntos_y_resolucion_sin_perder_datos(self):
        pagina = self.ventana.pagina_ingreso
        pagina.cargar(proyecto_irregular())
        self.assertEqual(pagina.tipo_seccion.currentData(), "irregular")
        self.assertFalse(pagina.campos["ancho_m"].isEnabled())
        self.assertFalse(pagina.campos["cota_fondo_m"].isEnabled())
        self.assertTrue(pagina.boton_seccion.isEnabled())
        self.assertEqual(pagina.numero_franjas.value(), 16)
        self.assertIn("3 puntos", pagina.boton_seccion.text())
        self.assertEqual(pagina.obtener_proyecto(), proyecto_irregular())

    def test_cambiar_tipo_y_puntos_invalida_resultado(self):
        pagina = self.ventana.pagina_ingreso
        pagina.cargar(proyecto_ejemplo())
        self.assertTrue(self.ventana.controlador.calcular())
        self.assertIsNotNone(self.ventana.sesion.resultado)
        pagina.tipo_seccion.setCurrentIndex(1)
        self.assertIsNone(self.ventana.sesion.resultado)
        pagina.establecer_puntos_terreno((PuntoTerreno(0, 104), PuntoTerreno(10, 100)))
        self.assertTrue(self.ventana.sesion.modificado)
        self.assertFalse(self.ventana.acciones["PDF"].isEnabled())


if __name__ == "__main__":
    unittest.main()
