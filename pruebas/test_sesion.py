"""Cambios, resultados obsoletos y fallos de archivo en una sesión real."""
from dataclasses import replace
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from socavacion_ll.aplicacion.sesion import SesionProyecto
from socavacion_ll.dominio.modelos import Proyecto, proyecto_ejemplo


class PruebasSesion(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.ruta = Path(self.temporal.name) / "caso.ll.json"
        self.sesion = SesionProyecto(proyecto_ejemplo())

    def test_actualizar_cambia_proyecto(self):
        cambiado = replace(self.sesion.proyecto, nombre="Otro proyecto")
        self.sesion.actualizar(cambiado)
        self.assertEqual(self.sesion.proyecto, cambiado)

    def test_calcular_y_editar_invalida_resultado(self):
        resultado = self.sesion.calcular()
        self.assertIs(self.sesion.resultado, resultado)
        self.assertAlmostEqual(resultado.puntos[0].socavacion_m, 1.736513861635, places=9)
        self.sesion.guardar(self.ruta)
        self.sesion.actualizar(replace(self.sesion.proyecto, caudal_m3s=125))
        self.assertIsNone(self.sesion.resultado)
        self.assertTrue(self.sesion.modificado)

    def test_calculo_fallido_no_conserva_resultado_anterior(self):
        self.sesion.calcular()
        with patch("socavacion_ll.aplicacion.sesion.calcular_proyecto", side_effect=ValueError("Fallo")):
            with self.assertRaises(ValueError):
                self.sesion.calcular()
        self.assertIsNone(self.sesion.resultado)

    def test_actualizacion_identica_no_invalida(self):
        resultado = self.sesion.calcular()
        self.sesion.guardar(self.ruta)
        self.sesion.actualizar(self.sesion.proyecto)
        self.assertIs(self.sesion.resultado, resultado)
        self.assertFalse(self.sesion.modificado)

    def test_guardar_y_reabrir_no_restaura_resultados(self):
        self.sesion.calcular()
        self.sesion.guardar(self.ruta)
        self.assertEqual(self.sesion.ruta, self.ruta)
        self.assertFalse(self.sesion.modificado)
        otra = SesionProyecto()
        otra.abrir(self.ruta)
        self.assertEqual(otra.proyecto, self.sesion.proyecto)
        self.assertIsNone(otra.resultado)
        self.assertFalse(otra.modificado)

    def test_guardar_sin_ruta_informa_error(self):
        with self.assertRaisesRegex(ValueError, "ruta"):
            self.sesion.guardar()

    def test_guardar_reutiliza_ruta_actual(self):
        self.sesion.guardar(self.ruta)
        self.sesion.actualizar(replace(self.sesion.proyecto, nombre="Modificado"))
        self.sesion.guardar()
        otra = SesionProyecto()
        otra.abrir(self.ruta)
        self.assertEqual(otra.proyecto.nombre, "Modificado")

    def test_guardado_fallido_no_cambia_ruta_ni_modificado(self):
        self.sesion.guardar(self.ruta)
        self.sesion.actualizar(replace(self.sesion.proyecto, nombre="Pendiente"))
        with patch("socavacion_ll.infraestructura.proyectos.os.replace", side_effect=OSError("Fallo")):
            with self.assertRaises(OSError):
                self.sesion.guardar(self.ruta.parent / "otra.json")
        self.assertEqual(self.sesion.ruta, self.ruta)
        self.assertTrue(self.sesion.modificado)

    def test_apertura_invalida_conserva_todo_el_trabajo(self):
        resultado = self.sesion.calcular()
        self.sesion.guardar(self.ruta)
        anterior = self.sesion.proyecto
        mala = self.ruta.parent / "invalido.json"
        mala.write_text("{}", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.sesion.abrir(mala)
        self.assertIs(self.sesion.proyecto, anterior)
        self.assertIs(self.sesion.resultado, resultado)
        self.assertEqual(self.sesion.ruta, self.ruta)
        self.assertFalse(self.sesion.modificado)

    def test_nuevo_limpia_y_ejemplo_se_marca_sin_guardar(self):
        self.sesion.guardar(self.ruta)
        self.sesion.calcular()
        self.sesion.nuevo()
        self.assertEqual(self.sesion.proyecto, Proyecto())
        self.assertIsNone(self.sesion.ruta)
        self.assertIsNone(self.sesion.resultado)
        self.assertFalse(self.sesion.modificado)
        self.sesion.nuevo(proyecto_ejemplo())
        self.assertTrue(self.sesion.modificado)


if __name__ == "__main__":
    unittest.main()
