"""Protección de fuentes en ejecución local y empaquetada."""
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from socavacion_ll.presentacion.dialogos import elegir_destino


class PruebasRecursos(unittest.TestCase):
    def test_fuentes_empaquetadas_no_se_sobrescriben(self):
        with tempfile.TemporaryDirectory() as carpeta:
            destino = Path(carpeta) / "docs" / "manual.pdf"
            with patch.object(sys, "_MEIPASS", carpeta, create=True), \
                 patch("PySide6.QtWidgets.QFileDialog.getSaveFileName", return_value=(str(destino), "")), \
                 patch("PySide6.QtWidgets.QMessageBox.warning") as aviso:
                self.assertIsNone(elegir_destino(None, "Guardar", "memoria.pdf", ".pdf"))
                aviso.assert_called_once()

    def test_carpeta_personal_docs_no_es_la_fuente_protegida(self):
        with tempfile.TemporaryDirectory() as carpeta:
            destino = Path(carpeta) / "mis docs" / "memoria.pdf"
            with patch("PySide6.QtWidgets.QFileDialog.getSaveFileName", return_value=(str(destino), "")), \
                 patch("PySide6.QtWidgets.QMessageBox.warning") as aviso:
                self.assertEqual(elegir_destino(None, "Guardar", "memoria.pdf", ".pdf"), destino)
                aviso.assert_not_called()


if __name__ == "__main__":
    unittest.main()
