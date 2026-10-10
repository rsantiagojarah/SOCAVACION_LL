"""Genera capturas locales para revisar el diseño sin abrir ventanas visibles."""
import os
from pathlib import Path
import sys

os.environ["QT_QPA_PLATFORM"] = "offscreen"
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase

from socavacion_ll.presentacion.ventana import VentanaPrincipal
from socavacion_ll.dominio.modelos import proyecto_ejemplo


def principal():
    destino = RAIZ / "tmp" / "interfaz"
    destino.mkdir(parents=True, exist_ok=True)
    aplicacion = QApplication([])
    # La plataforma offscreen no enumera las fuentes de Windows automáticamente.
    for archivo in ("segoeui.ttf", "segoeuib.ttf", "seguisym.ttf"):
        ruta_fuente = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / archivo
        if QFontDatabase.addApplicationFont(str(ruta_fuente)) < 0:
            raise RuntimeError(f"No se pudo cargar la fuente para revisión: {ruta_fuente}")
    ventana = VentanaPrincipal()
    ventana.pagina_ingreso.cargar(proyecto_ejemplo())
    ventana.controlador.calcular()
    ventana.show()
    for ancho, alto, nombre in ((1600, 900, "normal"), (1360, 720, "minimo")):
        ventana.resize(ancho, alto)
        aplicacion.processEvents()
        ruta = destino / f"{nombre}.png"
        if not ventana.grab().save(str(ruta)):
            raise RuntimeError(f"No se pudo guardar la captura: {ruta}")
        print(ruta)
    ventana.sesion.modificado = False
    ventana.close()


if __name__ == "__main__":
    principal()
