"""Composición del escritorio; los comandos se delegan al controlador."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QSplitter, QStatusBar, QVBoxLayout, QWidget,
)

from .barras import AccionPlana, crear_barra_acciones
from socavacion_ll.aplicacion.sesion import SesionProyecto
from socavacion_ll import __version__
from .controlador import ControladorVentana
from .ingreso import PaginaIngreso
from .evaluacion import PaginaNucleo, PaginaResultados
from .tema import aplicar_tema


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        aplicar_tema(QApplication.instance())
        self.sesion = SesionProyecto()
        self.setWindowTitle(f"Socavación LL {__version__}")
        self.resize(1480, 860)
        self.setMinimumSize(1360, 720)
        self.barra_acciones = crear_barra_acciones(self)
        self.acciones = {}
        self._crear_contenido()
        self.controlador = ControladorVentana(self)
        self._crear_acciones()
        estado = QStatusBar(self)
        estado.setFixedHeight(24)
        self.setStatusBar(estado)
        self.controlador.actualizar_titulo()
        self.controlador.mostrar_resultado()

    def _crear_contenido(self):
        contenido = QWidget()
        distribucion = QVBoxLayout(contenido)
        distribucion.setContentsMargins(0, 0, 0, 0)
        distribucion.setSpacing(0)
        self.divisor = QSplitter(Qt.Orientation.Horizontal)
        self.divisor.setChildrenCollapsible(False)
        self.divisor.setHandleWidth(4)
        self.pagina_ingreso = PaginaIngreso()
        self.pagina_ingreso.setMinimumWidth(760)
        self.pagina_resultados = PaginaResultados()
        self.pagina_resultados.setMinimumWidth(560)
        self.pagina_nucleo = PaginaNucleo()
        self.panel_datos = QSplitter(Qt.Orientation.Vertical)
        self.panel_datos.setChildrenCollapsible(False)
        self.panel_datos.setHandleWidth(4)
        self.panel_datos.addWidget(self.pagina_ingreso)
        self.panel_datos.addWidget(self.pagina_nucleo)
        self.panel_datos.setStretchFactor(0, 0)
        self.panel_datos.setStretchFactor(1, 1)
        self.panel_datos.setSizes([430, 280])
        self.divisor.addWidget(self.panel_datos)
        self.divisor.addWidget(self.pagina_resultados)
        self.divisor.setStretchFactor(0, 0)
        self.divisor.setStretchFactor(1, 1)
        self.divisor.setSizes([780, 680])
        distribucion.addWidget(self.divisor, 1)
        self.setCentralWidget(contenido)

    def _crear_acciones(self):
        for nombre, simbolo, funcion, atajo in (
            ("Nuevo", "+", self.controlador.nuevo, "Ctrl+N"),
            ("Abrir", "▱", self.controlador.abrir, "Ctrl+O"),
            ("Guardar", "↓", self.controlador.guardar, "Ctrl+S"),
            ("Guardar como", "↧", lambda: self.controlador.guardar(como=True), "Ctrl+Shift+S"),
            ("Ejemplo", "≡", self.controlador.cargar_ejemplo, None),
            ("Variable", "~", self.controlador.cargar_ejemplo_irregular, None),
            ("Calcular", "=", self.controlador.calcular, "F5"),
            ("Word", "W", lambda: self.controlador.exportar("Word"), None),
            ("PDF", "P", lambda: self.controlador.exportar("PDF"), None),
        ):
            accion = self._agregar_accion(nombre, simbolo)
            accion.setToolTip(nombre + (f" ({atajo})" if atajo else ""))
            if atajo:
                accion.setShortcut(atajo)
            accion.triggered.connect(lambda marcado=False, ejecutar=funcion: ejecutar())

    def _agregar_accion(self, nombre, simbolo):
        accion = QAction(nombre, self)
        self.acciones[nombre] = accion
        self.addAction(accion)
        self.barra_acciones.addAction(AccionPlana(accion, simbolo, self.barra_acciones))
        return accion

    def closeEvent(self, evento):
        if self.controlador.puede_cerrar():
            evento.accept()
        else:
            evento.ignore()
