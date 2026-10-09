"""Aceptación de ayuda local, consulta literal y notas con saltos de línea."""
from dataclasses import replace
import os
from pathlib import Path
import sys
import tempfile
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QApplication, QAbstractItemView, QPlainTextEdit

from socavacion_ll.calculo.coeficientes import TABLA_BETA, TABLA_Z, TABLA_MU, LUCES_M
from socavacion_ll.dominio.modelos import proyecto_ejemplo
from socavacion_ll.infraestructura.proyectos import abrir_proyecto, guardar_proyecto
from socavacion_ll.presentacion.ventana import VentanaPrincipal


class PruebasIngresoTrazable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.aplicacion = QApplication.instance() or QApplication([])

    def setUp(self):
        self.ventana = VentanaPrincipal()
        self.pagina = self.ventana.pagina_ingreso
        self.pagina.cargar(proyecto_ejemplo())

    def tearDown(self):
        self.ventana.sesion.modificado = False
        self.ventana.close()
        self.ventana.deleteLater()
        self.aplicacion.processEvents()

    def test_ayuda_visible_vecina_de_luz_y_valor_conservado(self):
        self.assertTrue(hasattr(self.pagina, "ayuda_luz"), "Falta ayuda visible junto a L")
        luz = self.pagina.campos["luz_libre_m"]
        self.pagina.show()
        self.aplicacion.processEvents()
        self.assertEqual(luz.parentWidget(), self.pagina.sin_obstaculos.parentWidget())
        self.assertEqual(luz.parentWidget(), self.pagina.ayuda_luz.parentWidget())
        luz.setText("42.12345")
        self.assertFalse(luz.isEnabled())
        self.assertIn("mu = 1", self.pagina.ayuda_luz.text())
        self.assertIn("no se utiliza", self.pagina.ayuda_luz.text())
        self.assertFalse(self.pagina.ayuda_luz.isHidden())
        self.pagina.sin_obstaculos.setChecked(False)
        self.assertTrue(luz.isEnabled())
        self.assertIn("interpolación lineal", self.pagina.ayuda_luz.text())
        self.assertIn("10", self.pagina.ayuda_luz.text())
        self.assertIn("200", self.pagina.ayuda_luz.text())
        self.pagina.sin_obstaculos.setChecked(True)
        self.assertEqual(luz.text(), "42.12345")

    def test_notas_multilinea_formulario_archivo_y_carga_sin_senales(self):
        notas = "Datum: IGN\n\nOrigen: levantamiento topográfico\nQ: estudio hidráulico\n"
        editor = self.pagina.campos["notas"]
        self.assertIsInstance(editor, QPlainTextEdit)
        self.assertIn("datum", editor.placeholderText().lower())
        self.assertIn("origen", editor.placeholderText().lower())
        cambios = QSignalSpy(self.pagina.cambiado)
        self.pagina.cargar(replace(proyecto_ejemplo(), notas=notas))
        self.assertEqual(cambios.count(), 0)
        self.assertEqual(editor.toPlainText(), notas)
        editor.insertPlainText("Fuente adicional\n")
        esperado = editor.toPlainText()
        self.assertGreater(cambios.count(), 0)
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "notas.ll.json"
            guardar_proyecto(ruta, self.pagina.obtener_proyecto())
            self.pagina.cargar(abrir_proyecto(ruta))
        self.assertEqual(self.pagina.obtener_proyecto().notas, esperado)

    def test_marcar_sin_obstaculos_restaura_l_invalida_y_avisa(self):
        for texto in ("", "foo", "nan", "inf", "-1"):
            with self.subTest(luz=texto):
                self.pagina.cargar(proyecto_ejemplo())
                self.pagina.sin_obstaculos.setChecked(False)
                self.pagina.campos["luz_libre_m"].setText(texto)
                cambios = QSignalSpy(self.pagina.cambiado)
                self.pagina.sin_obstaculos.setChecked(True)
                self.assertEqual(self.pagina.campos["luz_libre_m"].text(), "0")
                self.assertIn("restauró L a 0", self.pagina.ayuda_luz.text())
                self.assertIn("no válido", self.pagina.ayuda_luz.text())
                self.assertEqual(cambios.count(), 1)
                self.assertTrue(self.ventana.controlador.calcular())
                with tempfile.TemporaryDirectory() as directorio:
                    ruta = Path(directorio) / "sin_obstaculos.ll.json"
                    guardar_proyecto(ruta, self.pagina.obtener_proyecto())
                    self.assertEqual(abrir_proyecto(ruta).luz_libre_m, 0)

    def test_marcar_sin_obstaculos_conserva_texto_de_l_valida(self):
        for texto in ("30", "30.0000", "42,12345", "0"):
            with self.subTest(luz=texto):
                self.pagina.sin_obstaculos.setChecked(False)
                self.pagina.campos["luz_libre_m"].setText(texto)
                self.pagina.sin_obstaculos.setChecked(True)
                self.assertEqual(self.pagina.campos["luz_libre_m"].text(), texto)
                self.assertNotIn("restauró", self.pagina.ayuda_luz.text())

    def test_editar_notas_y_estado_invalidan_resultado_y_exportacion(self):
        self.assertIsInstance(self.pagina.campos["notas"], QPlainTextEdit)
        for editar in (
            lambda: self.pagina.campos["notas"].insertPlainText("\nOrigen actualizado"),
            lambda: self.pagina.sin_obstaculos.setChecked(False),
        ):
            self.assertTrue(self.ventana.controlador.calcular())
            editar()
            self.assertIsNone(self.ventana.sesion.resultado)
            self.assertTrue(self.ventana.sesion.modificado)
            self.assertFalse(self.ventana.acciones["Word"].isEnabled())
            self.assertFalse(self.ventana.acciones["PDF"].isEnabled())
            self.assertEqual(self.ventana.pagina_resultados.tabla.rowCount(), 0)

    def _consultar(self):
        self.assertTrue(hasattr(self.pagina, "boton_tablas"), "Falta acceso a tablas")
        abiertos = []

        def cerrar():
            dialogo = self.aplicacion.activeModalWidget()
            if dialogo is not None:
                abiertos.append(dialogo)
                dialogo.reject()

        QTimer.singleShot(0, cerrar)
        self.pagina.boton_tablas.click()
        self.assertEqual(len(abiertos), 1)
        return abiertos[0]

    def test_consulta_no_modifica_proyecto_constantes_ni_resultados(self):
        self.assertTrue(self.ventana.controlador.calcular())
        resultado = self.ventana.sesion.resultado
        proyecto = self.pagina.obtener_proyecto()
        constantes = (dict(TABLA_BETA), dict(TABLA_Z), dict(TABLA_MU))
        cambios = QSignalSpy(self.pagina.cambiado)
        modificado = self.ventana.sesion.modificado
        self._consultar()
        self.assertEqual(cambios.count(), 0)
        self.assertEqual(self.pagina.obtener_proyecto(), proyecto)
        self.assertIs(self.ventana.sesion.resultado, resultado)
        self.assertEqual(self.ventana.sesion.modificado, modificado)
        self.assertTrue(self.ventana.acciones["Word"].isEnabled())
        self.assertTrue(self.ventana.acciones["PDF"].isEnabled())
        self.assertEqual((TABLA_BETA, TABLA_Z, TABLA_MU), constantes)

    def test_tablas_completas_exactas_y_no_editables(self):
        dialogo = self._consultar()
        esperadas = {
            "beta": list(TABLA_BETA.items()), "z": list(TABLA_Z.items()),
            "mu": [(velocidad, *valores) for velocidad, valores in TABLA_MU.items()],
        }
        for nombre, filas in esperadas.items():
            tabla = dialogo.tablas[nombre]
            self.assertEqual(tabla.rowCount(), len(filas))
            self.assertEqual(tabla.columnCount(), len(filas[0]))
            self.assertEqual(tabla.editTriggers(), QAbstractItemView.EditTrigger.NoEditTriggers)
            for fila, valores in enumerate(filas):
                for columna, valor in enumerate(valores):
                    celda = tabla.item(fila, columna)
                    self.assertFalse(celda.flags() & Qt.ItemFlag.ItemIsEditable)
                    if isinstance(valor, str):
                        self.assertEqual(celda.text(), valor)
                    else:
                        self.assertEqual(float(celda.text()), valor)
        mu = dialogo.tablas["mu"]
        self.assertEqual(mu.item(7, 6).text(), "0.94")
        self.assertEqual(mu.item(7, 7).text(), "0.95")
        self.assertEqual([float(mu.horizontalHeaderItem(i).text()) for i in range(1, 14)],
                         list(LUCES_M))

    def test_fuentes_y_limites_visibles_en_cada_tabla(self):
        dialogo = self._consultar()
        for nombre in ("beta", "z"):
            fuente = dialogo.fuentes[nombre].text()
            self.assertIn("DGA_2022_Cachapoal_SIT527.pdf", fuente)
            self.assertIn("69", fuente)
            self.assertIn("79", fuente)
            self.assertIn("complementaria", fuente.lower())
        self.assertIn("7-1", dialogo.fuentes["beta"].text())
        self.assertIn("7-2", dialogo.fuentes["z"].text())
        fuente = dialogo.fuentes["mu"].text()
        for texto in ("MAN_11 HHD-2011.pdf", "107", "13", "3.5", "4"):
            self.assertIn(texto, fuente)


if __name__ == "__main__":
    unittest.main()
