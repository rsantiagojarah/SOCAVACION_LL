"""Aceptación de datos editables, cálculo e invalidación en la primera versión."""
from dataclasses import replace
import os
from pathlib import Path
import sys
import unittest
import tempfile
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from PySide6.QtWidgets import QApplication, QMessageBox
from socavacion_ll.dominio.modelos import proyecto_ejemplo
from socavacion_ll.infraestructura.proyectos import guardar_proyecto, abrir_proyecto
from socavacion_ll.presentacion.ventana import VentanaPrincipal


class PruebasInterfazV1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.aplicacion = QApplication.instance() or QApplication([])

    def setUp(self):
        self.ventana = VentanaPrincipal()

    def tearDown(self):
        if hasattr(self.ventana, "sesion"):
            self.ventana.sesion.modificado = False
        self.ventana.close()
        self.ventana.deleteLater()
        self.aplicacion.processEvents()

    def test_formulario_editable_y_redondeo_no_destruye_datos(self):
        self.assertTrue(hasattr(self.ventana.pagina_ingreso, "campos"))
        pagina = self.ventana.pagina_ingreso
        pagina.cargar(proyecto_ejemplo())
        self.assertEqual(pagina.obtener_proyecto(), proyecto_ejemplo())
        pagina.campos["caudal_m3s"].setText("123,45678912345")
        self.assertEqual(pagina.obtener_proyecto().caudal_m3s, 123.45678912345)

    def test_calcular_e_invalidar_al_editar(self):
        self.assertTrue(hasattr(self.ventana, "controlador"))
        self.ventana.pagina_ingreso.cargar(proyecto_ejemplo())
        self.ventana.controlador.calcular()
        self.assertAlmostEqual(self.ventana.sesion.resultado.puntos[0].profundidad_hs_m,
                               4.736513861635, places=9)
        self.assertTrue(self.ventana.acciones["PDF"].isEnabled())
        self.ventana.pagina_ingreso.campos["caudal_m3s"].setText("130")
        self.assertIsNone(self.ventana.sesion.resultado)
        self.assertFalse(self.ventana.acciones["PDF"].isEnabled())
        self.assertEqual(self.ventana.pagina_resultados.tabla.rowCount(), 0)

    def test_error_no_deja_resultado_anterior(self):
        self.assertTrue(hasattr(self.ventana, "controlador"))
        self.ventana.pagina_ingreso.cargar(proyecto_ejemplo())
        self.ventana.controlador.calcular()
        self.ventana.pagina_ingreso.campos["caudal_m3s"].setText("nan")
        with patch("PySide6.QtWidgets.QMessageBox.warning") as aviso:
            self.ventana.controlador.calcular()
        aviso.assert_called_once()
        self.assertIsNone(self.ventana.sesion.resultado)
        self.assertFalse(self.ventana.acciones["Word"].isEnabled())

    def test_recalcular_desvincula_lienzo_anterior_antes_de_insertar_otro(self):
        self.ventana.pagina_ingreso.cargar(proyecto_ejemplo())
        self.ventana.controlador.calcular()
        anterior = self.ventana.pagina_resultados.lienzo
        interpolado = replace(proyecto_ejemplo(), sin_obstaculos=False, luz_libre_m=27)
        self.ventana.sesion.actualizar(interpolado)
        self.ventana.sesion.calcular()
        self.ventana.controlador.mostrar_resultado()
        self.assertIsNone(anterior.parent())
        self.assertIsNot(anterior, self.ventana.pagina_resultados.lienzo)

    def test_abrir_mismo_archivo_tras_guardar_no_restaura_snapshot_viejo(self):
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "proyecto.ll.json"
            guardar_proyecto(ruta, proyecto_ejemplo())
            self.ventana.sesion.abrir(ruta)
            self.ventana.pagina_ingreso.cargar(self.ventana.sesion.proyecto)
            self.ventana.pagina_ingreso.campos["caudal_m3s"].setText("130")
            with patch("PySide6.QtWidgets.QFileDialog.getOpenFileName", return_value=(str(ruta), "")), \
                 patch("PySide6.QtWidgets.QMessageBox.question", return_value=QMessageBox.StandardButton.Save):
                self.assertTrue(self.ventana.controlador.abrir())
            self.assertEqual(self.ventana.pagina_ingreso.obtener_proyecto().caudal_m3s, 130)
            self.assertEqual(abrir_proyecto(ruta).caudal_m3s, 130)


if __name__ == "__main__":
    unittest.main()
