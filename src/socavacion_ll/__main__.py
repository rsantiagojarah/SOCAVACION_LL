"""Punto de entrada de la aplicación de escritorio Socavación LL."""
import sys
import argparse
import os

from PySide6.QtWidgets import QApplication

from socavacion_ll.presentacion.ventana import VentanaPrincipal


def principal():
    argumentos = argparse.ArgumentParser(description="Socavación LL para Windows")
    argumentos.add_argument("--comprobar-instalacion", metavar="DIRECTORIO",
                            help="Verificar el paquete y guardar evidencia en una subcarpeta nueva.")
    opciones = argumentos.parse_args()
    if opciones.comprobar_instalacion:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from socavacion_ll.infraestructura.autocomprobacion import comprobar_instalacion
        try:
            informe = comprobar_instalacion(opciones.comprobar_instalacion)
        except (OSError, ValueError, RuntimeError) as error:
            if sys.stderr is not None:
                print(f"Comprobación fallida: {error}", file=sys.stderr)
            return 1
        if sys.stdout is not None:
            print(informe)
        return 0
    aplicacion = QApplication(sys.argv)
    aplicacion.setApplicationName("Socavación LL")
    aplicacion.setOrganizationName("SOCAVACION_LL")
    ventana = VentanaPrincipal()
    ventana.show()
    return aplicacion.exec()


if __name__ == "__main__":
    raise SystemExit(principal())
