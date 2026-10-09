"""Capturas reproducibles de consultas y granulometría para revisión visual."""
import os
from pathlib import Path
import sys

os.environ["QT_QPA_PLATFORM"] = "offscreen"
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication
from socavacion_ll.presentacion.ventana import VentanaPrincipal
from socavacion_ll.presentacion.consulta_tablas import ConsultaTablas
from socavacion_ll.presentacion.granulometria import DialogoGranulometria


def principal():
    aplicacion = QApplication([])
    for nombre in ("segoeui.ttf", "segoeuib.ttf", "seguisym.ttf"):
        QFontDatabase.addApplicationFont(str(Path("C:/Windows/Fonts") / nombre))
    ventana = VentanaPrincipal()
    destino = RAIZ / "tmp/interfaz"
    destino.mkdir(parents=True, exist_ok=True)
    tablas = ConsultaTablas(ventana)
    tablas.show()
    for indice, nombre in enumerate(("beta", "z", "mu")):
        tablas.pestanas.setCurrentIndex(indice)
        aplicacion.processEvents()
        if not tablas.grab().save(str(destino / f"consulta_{nombre}.png")):
            raise RuntimeError("No se guardó captura de tablas.")
    tablas.close()
    dialogo = DialogoGranulometria("", ventana)
    dialogo.fuente.setText("Ensayo de ejemplo: marcas de clase documentadas")
    dialogo.intervalos.setChecked(True)
    for fila, valores in enumerate(((.2, 20), (.6, 50), (1, 30))):
        for columna, valor in enumerate(valores):
            dialogo.tabla.item(fila, columna).setText(str(valor))
    dialogo.previsualizar.click()
    dialogo.show()
    aplicacion.processEvents()
    if not dialogo.grab().save(str(destino / "granulometria.png")):
        raise RuntimeError("No se guardó captura de granulometría.")
    dialogo.reject()
    ventana.sesion.modificado = False
    ventana.close()


if __name__ == "__main__":
    principal()
