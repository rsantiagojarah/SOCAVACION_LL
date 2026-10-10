"""Ecuación 52, trazabilidad y aplicación atómica desde Qt real."""
from dataclasses import replace
from decimal import Decimal, ROUND_HALF_UP
import importlib
import math
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
        self.assertIn("fórmula", dialogo.estado.text())
        self.assertTrue(hasattr(self.pagina, "ayuda_granulometria"), "Aviso Dm visible tras aplicar")
        self.assertIn("fórmula", self.pagina.ayuda_granulometria.text())
        self.assertTrue(proyecto.notas.startswith(notas_previas))
        for texto in ("Ensayo E-01", "MAN_11 HHD-2011.pdf", "92", "52", "0.2", "20.0",
                      "0.6", "50.0", "30.0", "64.0", "0.64", "100.0"):
            self.assertIn(texto, proyecto.notas)
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "fracciones.ll.json"
            guardar_proyecto(ruta, proyecto)
            self.assertEqual(abrir_proyecto(ruta), proyecto)
        calculado = calcular_proyecto(proyecto)
        logaritmo = math.log10(0.64)
        self.assertEqual(
            calculado.z, 0.394557 - 0.04136 * logaritmo - 0.00891 * logaritmo ** 2)

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

    def test_importar_muestra_la_tabla_y_aplica_dm(self):
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "aberturas.xlsx"
            _libro_aberturas(ruta)

            def aplicar(dialogo):
                dialogo.cargar_archivo(ruta)
                self.assertEqual(dialogo.desarrollo.rowCount(), 19)
                self.assertEqual(dialogo.desarrollo.item(1, 1).text(), "75-63")
                self.assertEqual(dialogo.desarrollo.item(1, 4).text(), "69")
                self.assertEqual(dialogo.desarrollo.item(1, 6).text(), "324.3")
                self.assertEqual(dialogo.desarrollo.item(18, 1).text(), "Fondo")
                self.assertEqual(dialogo.desarrollo.item(18, 4).text(), "--")
                self.assertIn("12.503", dialogo.cierre.text())
                self.assertIn("Σ (Di × Pi)", dialogo.cierre.text())
                dialogo.accept()

            self._abrir(aplicar)
        proyecto = self.pagina.obtener_proyecto()
        self.assertEqual(self.pagina.campos["diametro_medio_mm"].text(), "12.503")
        self.assertEqual(proyecto.diametro_medio_mm, 12.503)
        self.assertIn("D superior (mm)", proyecto.notas)
        self.assertIn("Fondo", proyecto.notas)
        self.assertIn("12.503", proyecto.notas)
        self.assertIn("fórmula", self.pagina.ayuda_granulometria.text())


class PruebasDiametroTamices(unittest.TestCase):
    def setUp(self):
        modulo = importlib.import_module("socavacion_ll.calculo.granulometria")
        self.calcular = modulo.calcular_diametro_medio_por_tamices

    def test_limite_superior_obligatorio_y_media_de_aberturas(self):
        with self.assertRaises(ValueError):
            self.calcular([(50.8, 13.35)], fondo=86.65)
        resultado = self.calcular([(76.2, 0), (50.8, 13.35)], fondo=86.65)
        fila = resultado.filas[1]
        self.assertEqual(fila.d_superior_mm, Decimal("76.2"))
        self.assertEqual(fila.d_inferior_mm, Decimal("50.8"))
        self.assertEqual(fila.di_mm, Decimal("63.5"))
        self.assertEqual(fila.aporte, Decimal("63.5") * Decimal("13.35"))
        self.assertEqual(resultado.diametro_medio_mm, Decimal("8.477"))
        con_dmax = self.calcular([(50.8, 13.35)], fondo=86.65, dmax_mm=76.2)
        self.assertEqual(con_dmax.filas[0].di_mm, Decimal("63.5"))

    def test_no_salta_tamiz_con_retenido_cero(self):
        resultado = self.calcular([(76.2, 0), (63, 0), (50.8, 5)], fondo=95)
        fila = resultado.filas[2]
        self.assertEqual(fila.d_superior_mm, Decimal("63"))
        self.assertEqual(fila.di_mm, Decimal("56.9"))
        self.assertEqual(resultado.filas[1].di_mm, None)
        self.assertEqual(resultado.filas[1].aporte, Decimal(0))

    def test_fondo_no_recibe_di_ni_cambia_el_denominador(self):
        resultado = self.calcular([(10, 0), (5, 50)], fondo=50)
        fondo = resultado.filas[-1]
        self.assertEqual(fondo.fraccion, "Fondo")
        self.assertEqual(fondo.d_superior_mm, Decimal("5"))
        self.assertIsNone(fondo.d_inferior_mm)
        self.assertIsNone(fondo.di_mm)
        self.assertIsNone(fondo.aporte)
        self.assertEqual(resultado.suma_productos, Decimal("375"))
        self.assertEqual(resultado.diametro_medio_mm, Decimal("3.750"))
        self.assertNotEqual(resultado.diametro_medio_mm, Decimal("7.500"))

    def test_excel_de_aberturas_conserva_fondo_fuera_del_producto(self):
        tamices = [
            (75, 0), (63, 4.7), (50, 3), (37.5, 4.35), (25, 3.56), (19, 5.67),
            (12.5, 7.08), (9.5, 5.6), (4.75, 11.75), (2.36, 10.23), (2, 4.82),
            (1.19, 7.28), (0.6, 10.2), (0.425, 5.42), (0.3, 3.24), (0.18, 5.06),
            (0.15, 1.65), (0.075, 2.43),
        ]
        resultado = self.calcular(tamices, fondo=3.98)
        retenido_63 = resultado.filas[1]
        self.assertEqual(retenido_63.di_mm, Decimal("69"))
        self.assertEqual(retenido_63.aporte, Decimal("324.3"))
        self.assertIsNone(resultado.filas[-1].di_mm)
        self.assertEqual(resultado.suma_porcentajes, Decimal("100.02"))
        productos = Decimal(0)
        for anterior, actual in zip(tamices, tamices[1:]):
            if actual[1] == 0:
                continue
            di = (Decimal(str(anterior[0])) + Decimal(str(actual[0]))) / 2
            productos += di * Decimal(str(actual[1]))
        self.assertEqual(resultado.suma_productos, productos)
        self.assertEqual(
            resultado.diametro_medio_mm,
            (productos / 100).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP))

    def test_boloneria_adicional_escala_el_laboratorio(self):
        resultado = self.calcular(
            [(76.2, 0), (50, 100)], fondo=0,
            boloneria=[(101.6, 76.2, 10)])
        self.assertEqual(resultado.filas[0].di_mm, Decimal("88.9"))
        self.assertEqual(resultado.filas[0].aporte, Decimal("889"))
        self.assertEqual(resultado.filas[2].porcentaje, Decimal("90"))
        self.assertEqual(resultado.filas[2].di_mm, Decimal("63.1"))
        self.assertEqual(resultado.suma_porcentajes, Decimal("100"))
        with self.assertRaises(ValueError):
            self.calcular([(50, 100)], boloneria=[(101.6, 76.2, 10)])

    def test_rechaza_orden_suma_y_no_redondea_di_intermedio(self):
        with self.assertRaises(ValueError):
            self.calcular([(10, 0), (12, 100)])
        with self.assertRaises(ValueError):
            self.calcular([(10, 0), (5, 96)])
        resultado = self.calcular([(1.469, 0), (1, 100)])
        self.assertEqual(resultado.filas[1].di_mm, Decimal("1.2345"))
        self.assertEqual(resultado.diametro_medio_mm, Decimal("1.235"))


TAMICES_EXCEL = (
    (75, 0), (63, 4.7), (50, 3), (37.5, 4.35), (25, 3.56), (19, 5.67),
    (12.5, 7.08), (9.5, 5.6), (4.75, 11.75), (2.36, 10.23), (2, 4.82),
    (1.19, 7.28), (0.6, 10.2), (0.425, 5.42), (0.3, 3.24), (0.18, 5.06),
    (0.15, 1.65), (0.075, 2.43),
)


def _libro_aberturas(ruta, tamices=TAMICES_EXCEL, fondo=3.98, encabezado=("Abertura (mm)", "% Retenido")):
    from openpyxl import Workbook
    libro = Workbook()
    hoja = libro.active
    hoja.append(list(encabezado))
    for abertura, porcentaje in tamices:
        hoja.append([abertura, porcentaje])
    if fondo is not None:
        hoja.append(["FONDO", fondo])
    libro.save(ruta)


class PruebasLecturaAberturas(unittest.TestCase):
    def test_lee_fondo_y_rechaza_encabezado_o_formula(self):
        from socavacion_ll.infraestructura.aberturas_xlsx import leer_aberturas_retenido
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "muestra.xlsx"
            _libro_aberturas(ruta)
            lectura = leer_aberturas_retenido(ruta)
            self.assertEqual(lectura.tamices, TAMICES_EXCEL)
            self.assertEqual(lectura.fondo, 3.98)
            _libro_aberturas(ruta, encabezado=("Diametro", "Pasa"))
            with self.assertRaises(ValueError):
                leer_aberturas_retenido(ruta)
            from openpyxl import Workbook
            libro = Workbook()
            hoja = libro.active
            hoja.append(["Abertura (mm)", "% Retenido"])
            hoja["A2"] = "=75"
            hoja["B2"] = 100
            libro.save(ruta)
            with self.assertRaises(ValueError):
                leer_aberturas_retenido(ruta)


if __name__ == "__main__":
    unittest.main()
