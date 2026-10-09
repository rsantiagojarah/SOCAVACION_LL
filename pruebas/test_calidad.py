"""Controles independientes: el verificador debe aceptar y rechazar evidencia."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from calidad import comprobar_cobertura, ejecutar_comprobaciones


class PruebasCalidad(unittest.TestCase):
    @unittest.skipUnless(os.name == "nt", "Lanzador PowerShell para Windows")
    def test_lanzador_powershell_propaga_cero_error_y_python_ausente(self):
        lanzador = Path(__file__).resolve().parents[1] / "scripts/verificar.ps1"
        with tempfile.TemporaryDirectory() as carpeta:
            simulado = Path(carpeta) / "python_simulado.cmd"
            for codigo in (0, 7):
                simulado.write_text(f"@exit /b {codigo}\n", encoding="ascii")
                proceso = subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy",
                    "Bypass", "-File", str(lanzador), "-Python", str(simulado)],
                    capture_output=True, check=False)
                self.assertEqual(proceso.returncode, codigo)
            proceso = subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy",
                "Bypass", "-File", str(lanzador), "-Python", str(Path(carpeta) / "ausente.exe")],
                capture_output=True, check=False)
            self.assertNotEqual(proceso.returncode, 0)

    def test_orquestador_propaga_error_y_no_ejecuta_pasos_posteriores(self):
        with tempfile.TemporaryDirectory() as carpeta:
            raiz = Path(carpeta)
            comandos = [("positivo", [sys.executable, "-c", "print('positivo')"]),
                        ("fallo", [sys.executable, "-c", "raise SystemExit(7)"]),
                        ("no_ejecutado", [sys.executable, "-c", "print('incorrecto')"])]
            self.assertEqual(ejecutar_comprobaciones(comandos, raiz), 7)
            self.assertFalse((raiz / "tmp/calidad/03-no_ejecutado.log").exists())
            self.assertIn("positivo", (raiz / "tmp/calidad/01-positivo.log").read_text())

    def test_orquestador_positivo_y_herramienta_ausente(self):
        with tempfile.TemporaryDirectory() as carpeta:
            raiz = Path(carpeta)
            self.assertEqual(ejecutar_comprobaciones(
                [("bueno", [sys.executable, "-c", "pass"])], raiz), 0)
            self.assertNotEqual(ejecutar_comprobaciones(
                [("ausente", [str(raiz / "inexistente.exe")])], raiz), 0)

    def _comprobar(self, cubiertas, total, archivos=None, ramas=True):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "cobertura.json"
            resumen = {"covered_branches": cubiertas, "num_branches": total}
            ruta.write_text(json.dumps({"meta": {"branch_coverage": ramas},
                "files": archivos if archivos is not None else {"nucleo.py": {"summary": resumen}}}),
                encoding="utf-8")
            return comprobar_cobertura(ruta, {"nucleo.py"})

    def test_cobertura_acepta_umbral_exacto_y_total(self):
        self.assertEqual(self._comprobar(9, 10), 90)
        self.assertEqual(self._comprobar(10, 10), 100)

    def test_cobertura_rechaza_debajo_del_umbral_sin_redondear(self):
        with self.assertRaises(ValueError):
            self._comprobar(899, 1000)

    def test_cobertura_rechaza_evidencia_ausente_o_inconsistente(self):
        for cubiertas, total in ((0, 0), (11, 10), (-1, 10), (True, 10)):
            with self.subTest(cubiertas=cubiertas, total=total), self.assertRaises(ValueError):
                self._comprobar(cubiertas, total)
        with self.assertRaises(ValueError):
            self._comprobar(10, 10, archivos={})
        with self.assertRaises(ValueError):
            self._comprobar(10, 10, ramas=False)
        with self.assertRaises(OSError):
            comprobar_cobertura(Path("archivo-inexistente.json"), {"nucleo.py"})


if __name__ == "__main__":
    unittest.main()
