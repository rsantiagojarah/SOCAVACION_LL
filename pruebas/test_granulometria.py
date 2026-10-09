"""Ecuación 52, trazabilidad y aplicación atómica desde Qt real."""
from dataclasses import replace
import importlib
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PySide6.QtCore import QTimer
from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QApplication, QTableWidgetItem

from socavacion_ll.calculo.motor import calcular_proyecto
from socavacion_ll.dominio.modelos import proyecto_ejemplo
from socavacion_ll.infraestructura.proyectos import guardar_proyecto, abrir_proyecto
from socavacion_ll.infraestructura.reportes.contenido import preparar_contenido
from socavacion_ll.presentacion.ventana import VentanaPrincipal


class PruebasDiametroMedio(unittest.TestCase):
    def setUp(self):
        nombre = "socavacion_ll.calculo.granulometria"
        self.assertIsNotNone(importlib.util.find_spec(nombre), "Falta cálculo de fracciones")
        self.calcular = importlib.import_module(nombre).calcular_diametro_medio

    def test_referencias_manuales_sin_mutacion(self):
        fracciones = [(0.2, 20), (0.6, 50), (1.0, 30)]
        self.assertEqual(self.calcular(fracciones), 0.64)
        self.assertEqual(fracciones, [(0.2, 20), (0.6, 50), (1.0, 30)])
        self.assertEqual(self.calcular([(0.5, 50), (1.5, 50)]), 1.0)
        self.assertEqual(self.calcular([(1.0, 100), (2.0, 0)]), 1.0)

    def test_rechaza_tipos_formas_y_limites_invalidos(self):
        casos = [None, (), {}, "datos", [], [(1.0, 1.0)] * 101,
                 [None], [(1,)], [(1, 50, 2)], [[1, 100]],
                 [(True, 100)], [(1, True)], [("1", 100)], [(1, "100")],
                 [(0, 100)], [(-1, 100)], [(1, -1)], [(1, 101)],
                 [(float("nan"), 100)], [(float("inf"), 100)],
                 [(1, float("nan"))], [(1, float("inf"))],
                 [(10**1000, 100)], [(1, 10**1000)], [(1e308, 100)],
                 [(2e306, 50), (2e306, 50)],
                 [(1, 99)], [(1, 100 - 2e-8)], [(1, 50), (1, 50 + 2e-8)]]
        for caso in casos:
            with self.subTest(caso=str(caso)[:80]), self.assertRaises(ValueError):
                self.calcular(caso)

    def test_tolerancia_absoluta_sin_normalizacion(self):
        porcentaje = 100 - 5e-9
        self.assertEqual(self.calcular([(2, porcentaje)]), 2 * porcentaje / 100)
        self.assertNotEqual(self.calcular([(2, porcentaje)]), 2)
        self.assertEqual(self.calcular([(1, 1)] * 100), 1)


class PruebasDialogoGranulometria(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.aplicacion = QApplication.instance() or QApplication([])

    def setUp(self):
        self.ventana = VentanaPrincipal()
        self.pagina = self.ventana.pagina_ingreso
        self.pagina.cargar(proyecto_ejemplo())
        self.assertTrue(hasattr(self.pagina, "boton_granulometria"), "Falta herramienta Dm")

    def tearDown(self):
        self.ventana.sesion.modificado = False
        self.ventana.close()
        self.ventana.deleteLater()
        self.aplicacion.processEvents()

    def _rellenar(self, dialogo, fracciones=((0.2, 20), (0.6, 50), (1.0, 30))):
        dialogo.fuente.setText("Ensayo E-01 · laboratorio, muestra A")
        dialogo.intervalos.setChecked(True)
        dialogo.tabla.setRowCount(len(fracciones))
        for fila, valores in enumerate(fracciones):
            for columna, valor in enumerate(valores):
                dialogo.tabla.setItem(fila, columna, QTableWidgetItem(str(valor)))

    def _abrir(self, operar):
        errores = []
        abiertos = []

        def actuar():
            dialogo = self.aplicacion.activeModalWidget()
            abiertos.append(dialogo)
            try:
                self._rellenar(dialogo)
                operar(dialogo)
            except BaseException as error:
                errores.append(error)
            finally:
                if dialogo is not None and dialogo.isVisible():
                    dialogo.reject()

        QTimer.singleShot(0, actuar)
        self.pagina.boton_granulometria.click()
        if errores:
            raise errores[0]
        self.assertEqual(len(abiertos), 1)
        return abiertos[0]

    def test_cancelar_conserva_proyecto_resultado_y_exportacion(self):
        self.ventana.controlador.calcular()
        anterior = self.pagina.obtener_proyecto()
        resultado = self.ventana.sesion.resultado
        cambios = QSignalSpy(self.pagina.cambiado)
        self._abrir(lambda dialogo: dialogo.reject())
        self.assertEqual(self.pagina.obtener_proyecto(), anterior)
        self.assertIs(self.ventana.sesion.resultado, resultado)
        self.assertTrue(self.ventana.acciones["PDF"].isEnabled())
        self.assertEqual(cambios.count(), 0)

    def test_aceptar_conserva_anexo_real_y_bloquea_dm_no_tabulado(self):
        self.ventana.controlador.calcular()
        notas_previas = self.pagina.obtener_proyecto().notas
        cambios = QSignalSpy(self.pagina.cambiado)
        dialogo = self._abrir(lambda dialogo: dialogo.accept())
        proyecto = self.pagina.obtener_proyecto()
        self.assertEqual(proyecto.diametro_medio_mm, 0.64)
        self.assertEqual(cambios.count(), 1)
        self.assertIsNone(self.ventana.sesion.resultado)
        self.assertFalse(self.ventana.acciones["Word"].isEnabled())
        self.assertFalse(self.ventana.acciones["PDF"].isEnabled())
        self.assertIn("no habilita LL", dialogo.estado.text())
        self.assertTrue(hasattr(self.pagina, "ayuda_granulometria"), "Aviso Dm visible tras aplicar")
        self.assertIn("no habilita LL", self.pagina.ayuda_granulometria.text())
        self.assertTrue(proyecto.notas.startswith(notas_previas))
        for texto in ("Ensayo E-01", "MAN_11 HHD-2011.pdf", "92", "52", "0.2", "20.0",
                      "0.6", "50.0", "30.0", "64.0", "0.64", "100.0"):
            self.assertIn(texto, proyecto.notas)
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "fracciones.ll.json"
            guardar_proyecto(ruta, proyecto)
            self.assertEqual(abrir_proyecto(ruta), proyecto)
        with self.assertRaisesRegex(ValueError, "celda"):
            calcular_proyecto(proyecto)

    def test_dm_tabulado_aparece_en_contenido_de_memorias(self):
        def aplicar(dialogo):
            self._rellenar(dialogo, ((0.5, 50), (1.5, 50)))
            dialogo.accept()
        self._abrir(aplicar)
        proyecto = self.pagina.obtener_proyecto()
        self.assertEqual(proyecto.diametro_medio_mm, 1.0)
        contenido = preparar_contenido(calcular_proyecto(proyecto))
        self.assertTrue(any(b.contenido == "Notas: " + proyecto.notas for b in contenido))

    def test_aplicar_recalcula_ediciones_posteriores_a_vista_previa(self):
        def aplicar(dialogo):
            dialogo.previsualizar.click()
            self.assertIn("0.64", dialogo.estado.text())
            dialogo.tabla.item(0, 0).setText("0,3")
            dialogo.accept()
        self._abrir(aplicar)
        self.assertEqual(self.pagina.obtener_proyecto().diametro_medio_mm, 0.66)

    def test_rechazo_atomico_por_limite_de_notas(self):
        self.pagina.cargar(replace(proyecto_ejemplo(), notas="n" * 20000))
        anterior = self.pagina.obtener_proyecto()
        cambios = QSignalSpy(self.pagina.cambiado)
        def rechazar(dialogo):
            dialogo.accept()
            self.assertIn("20000", dialogo.estado.text())
            self.assertTrue(dialogo.isVisible())
        self._abrir(rechazar)
        self.assertEqual(self.pagina.obtener_proyecto(), anterior)
        self.assertEqual(cambios.count(), 0)

    def test_validacion_fuente_confirmacion_y_celdas_sin_cambios(self):
        anterior = self.pagina.obtener_proyecto()
        def probar(dialogo):
            for fuente in ("", " ", "x" * 501, "fuente\x01"):
                dialogo.fuente.setText(fuente)
                dialogo.accept()
                self.assertTrue(dialogo.isVisible())
            dialogo.fuente.setText("Ensayo")
            dialogo.intervalos.setChecked(False)
            dialogo.accept()
            self.assertTrue(dialogo.isVisible())
            dialogo.intervalos.setChecked(True)
            dialogo.tabla.item(0, 0).setText("")
            dialogo.accept()
            self.assertTrue(dialogo.isVisible())
        self._abrir(probar)
        self.assertEqual(self.pagina.obtener_proyecto(), anterior)


if __name__ == "__main__":
    unittest.main()
