"""Selección de destinos y confirmaciones sin lógica hidráulica."""
from pathlib import Path
import sys

from PySide6.QtWidgets import QFileDialog, QMessageBox

RAIZ = Path(__file__).resolve().parents[3]


def elegir_destino(ventana, titulo, sugerencia, extension):
    nombre, _ = QFileDialog.getSaveFileName(
        ventana, titulo, str(sugerencia), f"Archivo {extension} (*{extension})"
    )
    if not nombre:
        return None
    ruta = Path(nombre)
    agregada = not ruta.name.lower().endswith(extension)
    if agregada:
        ruta = Path(str(ruta) + extension)
    # Nunca permitir sustituir las fuentes técnicas de este proyecto.
    recursos = Path(getattr(sys, "_MEIPASS", RAIZ))
    if ruta.resolve().is_relative_to((recursos / "docs").resolve()):
        QMessageBox.warning(ventana, "Destino protegido", "Guarda proyectos y memorias fuera de la carpeta docs.")
        return None
    if ruta.exists() and agregada:
        respuesta = QMessageBox.question(
            ventana, "Reemplazar archivo", f"El archivo {ruta.name} existe. ¿Reemplazarlo?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if respuesta != QMessageBox.StandardButton.Yes:
            return None
    return ruta


def confirmar_cambios(ventana, guardar):
    if not ventana.sesion.modificado:
        return True
    respuesta = QMessageBox.question(
        ventana, "Cambios sin guardar", "¿Quieres guardar los cambios antes de continuar?",
        QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
        QMessageBox.StandardButton.Save,
    )
    if respuesta == QMessageBox.StandardButton.Save:
        return guardar()
    return respuesta == QMessageBox.StandardButton.Discard
