"""Cabecera y acciones compactas adaptadas de Metrados/chrome.py."""
from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QLabel, QToolBar, QToolButton, QWidgetAction,
)

from .colores import ACENTO, FUENTE


class BotonAccion(QToolButton):
    """Comportamiento nativo QAction y presentación plana con símbolo y rótulo."""

    def __init__(self, accion, simbolo, padre=None):
        super().__init__(padre)
        self.simbolo = simbolo
        self.setDefaultAction(accion)
        self.setAccessibleName(accion.text())
        self.setFixedSize(64, 36)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAutoRaise(True)
        self.setMouseTracking(True)

    def paintEvent(self, evento):
        """Nombre de extensión impuesto por Qt; no contiene lógica de dominio."""
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.RenderHint.Antialiasing)
        resaltado = self.underMouse() and self.isEnabled()
        if self.isDown() or resaltado:
            pintor.setPen(Qt.PenStyle.NoPen)
            pintor.setBrush(QColor("#33404d" if self.isDown() else "#29313b"))
            pintor.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 2, 2)
        for texto, tamano, region in (
            (self.simbolo, 14, QRect(0, 1, self.width(), 18)),
            (self.text(), 9, QRect(0, 19, self.width(), 15)),
        ):
            fuente = QFont(FUENTE)
            fuente.setPixelSize(tamano)
            pintor.setFont(fuente)
            color = "#ffffff" if resaltado else "#b4bbc5" if self.isEnabled() else "#5f6b79"
            pintor.setPen(QColor(color))
            pintor.drawText(region, Qt.AlignmentFlag.AlignCenter, texto)
        if self.hasFocus():
            pintor.setPen(QPen(QColor(ACENTO), 1))
            pintor.drawLine(6, self.height() - 2, self.width() - 6, self.height() - 2)

    def enterEvent(self, evento):
        super().enterEvent(evento)
        self.update()

    def leaveEvent(self, evento):
        super().leaveEvent(evento)
        self.update()


class AccionPlana(QWidgetAction):
    """Conserva la acción en el menú de desbordamiento de Qt."""

    def __init__(self, accion, simbolo, padre):
        super().__init__(padre)
        self.accion = accion
        self.simbolo = simbolo
        accion.changed.connect(self.sincronizar)
        self.triggered.connect(accion.trigger)
        self.sincronizar()

    def sincronizar(self):
        self.setText(self.accion.text())
        self.setToolTip(self.accion.toolTip())
        self.setEnabled(self.accion.isEnabled())

    def createWidget(self, padre):
        if isinstance(padre, QToolBar):
            return BotonAccion(self.accion, self.simbolo, padre)
        return None


def crear_barra_acciones(ventana):
    barra = QToolBar("Acciones", ventana)
    barra.setObjectName("acciones")
    barra.setMovable(False)
    barra.setFixedHeight(38)
    titulo = QLabel("Nuevo proyecto")
    titulo.setObjectName("pestanaProyecto")
    titulo.setAccessibleName("Proyecto actual")
    titulo.setMinimumWidth(140)
    ventana.titulo_proyecto = titulo
    barra.addWidget(titulo)
    barra.addSeparator()
    ventana.addToolBar(barra)
    return barra
