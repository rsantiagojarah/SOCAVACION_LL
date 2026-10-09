"""Autocomprobación y preservación de destinos de distribución."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))


class PruebasDistribucion(unittest.TestCase):
    def test_autocomprobacion_fallida_no_abre_dialogo_invisible(self):
        from socavacion_ll.infraestructura.autocomprobacion import comprobar_instalacion
        with tempfile.TemporaryDirectory() as carpeta, \
             patch("socavacion_ll.aplicacion.sesion.SesionProyecto.calcular", side_effect=ValueError("fallo")), \
             patch("PySide6.QtWidgets.QMessageBox.warning") as aviso:
            with self.assertRaises((ValueError, RuntimeError)):
                comprobar_instalacion(carpeta)
            aviso.assert_not_called()

    def test_autocomprobacion_real_sin_sobrescribir(self):
        nombre = "socavacion_ll.infraestructura.autocomprobacion"
        self.assertIsNotNone(importlib.util.find_spec(nombre), "Falta autocomprobación")
        from socavacion_ll.infraestructura.autocomprobacion import comprobar_instalacion
        with tempfile.TemporaryDirectory(prefix="prueba LL ") as carpeta:
            informe = comprobar_instalacion(Path(carpeta))
            datos = json.loads(informe.read_text(encoding="utf-8"))
            self.assertAlmostEqual(datos["hs_m"], 4.736513861635, places=9)
            self.assertAlmostEqual(datos["mu_interpolado"], .974, places=15)
            self.assertAlmostEqual(datos["hs_interpolado_m"], 4.826485283163771, places=12)
            self.assertAlmostEqual(datos["area_irregular_m2"], 22.5, places=12)
            self.assertAlmostEqual(datos["ancho_mojado_irregular_m"], 15.0, places=12)
            self.assertAlmostEqual(datos["cierre_irregular_m3s"], 0.0, places=12)
            self.assertGreaterEqual(datos["franjas_irregulares"], 8)
            self.assertTrue(datos["proyecto_recuperado"])
            for nombre in ("ejemplo.ll.json", "interpolacion.ll.json", "memoria.docx",
                           "memoria.pdf", "irregular.ll.json", "memoria_irregular.docx",
                           "memoria_irregular.pdf", "interfaz.png"):
                self.assertGreater((informe.parent / nombre).stat().st_size, 100)
            segundo = comprobar_instalacion(Path(carpeta))
            self.assertNotEqual(informe.parent, segundo.parent)
            self.assertTrue(informe.exists())

    def test_empaquetado_rechaza_destino_existente(self):
        archivo = RAIZ / "scripts" / "empaquetar.py"
        self.assertTrue(archivo.exists(), "Falta script de empaquetado")
        especificacion = importlib.util.spec_from_file_location("empaquetar", archivo)
        modulo = importlib.util.module_from_spec(especificacion)
        especificacion.loader.exec_module(modulo)
        with tempfile.TemporaryDirectory() as carpeta:
            destino = Path(carpeta) / "Socavacion_LL"
            destino.mkdir()
            with self.assertRaises(FileExistsError):
                modulo.preparar_comando(destino)
            self.assertTrue(destino.exists())


if __name__ == "__main__":
    unittest.main()
