"""Composición del escritorio; los comandos se delegan al controlador."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QListWidget, QMainWindow, QSplitter,
    QStackedWidget, QStatusBar, QVBoxLayout, QWidget,
)

from .barras import AccionPlana, crear_barra_acciones, crear_cabecera
from .componentes import etiqueta
from socavacion_ll.aplicacion.sesion import SesionProyecto
from socavacion_ll import __version__
from .controlador import ControladorVentana
from .ingreso import PaginaIngreso
from .evaluacion import PaginaNucleo, PaginaReportes, PaginaResultados
from .tema import aplicar_tema

FASES = (
    "01  Ingreso de datos",
    "02  Núcleo de cálculo",
    "03  Presentación de resultados",
    "04  Generación de reportes",
)


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        aplicar_tema(QApplication.instance())
        self.sesion = SesionProyecto()
        self.setWindowTitle(f"Socavación LL {__version__}")
        self.resize(1480, 820)
        self.setMinimumSize(1000, 640)
        self.cabecera = crear_cabecera(self)
        self.barra_acciones = crear_barra_acciones(self)
        self.acciones = {}
        self._crear_contenido()
        self.controlador = ControladorVentana(self)
        self._crear_acciones()
        estado = QStatusBar(self)
        estado.setFixedHeight(24)
        self.setStatusBar(estado)
        self.navegacion.currentRowChanged.connect(self.cambiar_fase)
        self.navegacion.setCurrentRow(0)
        self.controlador.actualizar_titulo()
        self.controlador.mostrar_resultado()

    def _crear_contenido(self):
        contenido = QWidget()
        distribucion = QVBoxLayout(contenido)
        distribucion.setContentsMargins(0, 0, 0, 0)
        distribucion.setSpacing(0)
        banda = QWidget()
        banda.setObjectName("banda")
        banda.setFixedHeight(30)
        horizontal = QHBoxLayout(banda)
        horizontal.setContentsMargins(12, 0, 12, 0)
        alcance = etiqueta("SOCAVACIÓN GENERAL  /  SUELOS NO COHESIVOS", "metadato")
        alcance.setWordWrap(False)
        horizontal.addWidget(alcance)
        horizontal.addStretch()
        self.etiqueta_fase = etiqueta("", "etiquetaFase")
        self.etiqueta_fase.setWordWrap(False)
        horizontal.addWidget(self.etiqueta_fase)
        distribucion.addWidget(banda)
        self.divisor = QSplitter(Qt.Orientation.Horizontal)
        self.divisor.setChildrenCollapsible(False)
        self.divisor.setHandleWidth(4)
        self.divisor.addWidget(self._crear_lateral())
        self.paginas = QStackedWidget()
        self.paginas.setMinimumWidth(610)
        self.pagina_ingreso = PaginaIngreso()
        self.pagina_resultados = PaginaResultados()
        self.pagina_nucleo = PaginaNucleo()
        self.pagina_reportes = PaginaReportes()
        for pagina in (self.pagina_ingreso, self.pagina_nucleo, self.pagina_resultados, self.pagina_reportes):
            self.paginas.addWidget(pagina)
        self.divisor.addWidget(self.paginas)
        self.divisor.setStretchFactor(0, 0)
        self.divisor.setStretchFactor(1, 1)
        self.divisor.setSizes([250, 1200])
        distribucion.addWidget(self.divisor, 1)
        self.setCentralWidget(contenido)

    def _crear_lateral(self):
        lateral = QWidget()
        lateral.setObjectName("lateral")
        lateral.setMinimumWidth(235)
        distribucion = QVBoxLayout(lateral)
        distribucion.setContentsMargins(10, 12, 10, 14)
        distribucion.addWidget(etiqueta("FLUJO DE TRABAJO", "grupo"))
        self.navegacion = QListWidget()
        self.navegacion.setAccessibleName("Fases del programa")
        self.navegacion.addItems(FASES)
        for indice, fase in enumerate(FASES):
            self.navegacion.item(indice).setToolTip(fase)
        distribucion.addWidget(self.navegacion, 1)
        distribucion.addWidget(etiqueta("FUENTES PRINCIPALES", "grupo"))
        distribucion.addWidget(etiqueta("MTC · Hidrología, Hidráulica y Drenaje · 2011"))
        distribucion.addWidget(etiqueta("MTC · Manual de Puentes · 2018"))
        distribucion.addSpacing(10)
        distribucion.addWidget(etiqueta(f"VERSIÓN {__version__}", "etiquetaFase"))
        distribucion.addWidget(etiqueta(
            "Sección rectangular · lecho homogéneo\nAgua clara · mu interpola solo L"))
        return lateral

    def _crear_acciones(self):
        for indice, (nombre, simbolo) in enumerate((
            ("Datos", "≡"), ("Núcleo", "ƒ"), ("Resultados", "∿"), ("Reportes", "▤"),
        )):
            accion = self._agregar_accion(nombre, simbolo)
            accion.setShortcut(f"Alt+{indice + 1}")
            accion.setToolTip(f"Ver {FASES[indice][4:]} (Alt+{indice + 1})")
            accion.triggered.connect(
                lambda marcado=False, destino=indice: self.navegacion.setCurrentRow(destino)
            )
        self.barra_acciones.addSeparator()
        for nombre, simbolo, funcion, atajo in (
            ("Nuevo", "+", self.controlador.nuevo, "Ctrl+N"),
            ("Abrir", "▱", self.controlador.abrir, "Ctrl+O"),
            ("Guardar", "↓", self.controlador.guardar, "Ctrl+S"),
            ("Guardar como", "↧", lambda: self.controlador.guardar(como=True), "Ctrl+Shift+S"),
            ("Ejemplo", "≡", self.controlador.cargar_ejemplo, None),
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

    def cambiar_fase(self, indice):
        if not 0 <= indice < self.paginas.count():
            return
        self.paginas.setCurrentIndex(indice)
        self.etiqueta_fase.setText(FASES[indice][4:].upper())
        self.statusBar().showMessage(
            f"Proyecto · {FASES[indice][4:]} · LL rectangular / no cohesivos · Alt+1…4: cambiar fase"
        )

    def closeEvent(self, evento):
        if self.controlador.puede_cerrar():
            evento.accept()
        else:
            evento.ignore()
