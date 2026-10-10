"""Tema Qt: misma paleta y densidad visual que Metrados, sin depender de él."""
from PySide6.QtGui import QColor, QFont, QPalette

from . import colores as c


ESTILO = f"""
QWidget {{ font-family: '{c.FUENTE}'; font-size: 11px; color: {c.TEXTO}; }}
QMainWindow, QDialog {{ background: {c.FONDO}; }}
QLabel {{ background: transparent; }}
QLabel#marca {{ color: #f0f2f5; font-size: 14px; font-weight: 600; }}
QLabel#metadato {{ color: #788493; font-size: 8px; }}
QLabel#titulo {{ font-size: 16px; font-weight: 600; color: #edf2f7; }}
QLabel#subtitulo {{ color: {c.SECUNDARIO}; }}
QLabel#aviso {{ color: {c.ADVERTENCIA}; padding: 4px 6px; background: #342624;
    border: 1px solid #594439; border-radius: 3px; }}
QLabel#etiquetaFase {{ color: {c.ACENTO}; font-weight: 600; }}
QLabel#grupo {{ color: {c.SECUNDARIO}; font-weight: 600; padding: 0; }}
QLabel#estadoVacio {{ color: {c.SECUNDARIO}; font-size: 13px; padding: 20px; }}
QToolBar {{ background: {c.PANEL}; border: 0; border-bottom: 1px solid #29313b; }}
QToolBar#cabecera {{ background: #10141a; padding: 0; spacing: 0; }}
QToolBar#acciones {{ padding: 0 7px; spacing: 1px; }}
QToolBar::separator {{ background: {c.BORDE}; width: 1px; margin: 4px 5px; }}
QLineEdit, QComboBox, QSpinBox, QPlainTextEdit {{
    background: {c.ENTRADA}; color: #edf2f7; border: 1px solid {c.BORDE};
    border-radius: 3px; padding: 2px 6px; selection-background-color: #365266; }}
QLineEdit:focus {{ border-color: {c.ACENTO}; }}
QLabel#pestanaProyecto {{ color: #edf2f7; font-weight: 600; padding: 0 8px; }}
QWidget#banda {{ background: #14181e; border-bottom: 1px solid #252d37; }}
QWidget#lateral {{ background: {c.SUPERFICIE}; }}
QFrame#tarjeta {{ background: {c.SUPERFICIE}; border: 1px solid {c.BORDE}; }}
QSplitter::handle {{ background: {c.BORDE}; }}
QSplitter::handle:hover {{ background: {c.ACENTO}; }}
QListWidget {{ background: {c.SUPERFICIE}; border: 0; outline: 0; }}
QListWidget::item {{ min-height: 34px; padding: 4px 9px; }}
QListWidget::item:selected {{ background: {c.SELECCION}; color: #edf2f7;
    border-left: 2px solid {c.ACENTO}; }}
QListWidget::item:hover {{ background: #202d3a; }}
QListWidget::item:focus {{ border: 1px solid {c.ACENTO}; }}
QTableWidget {{ background: {c.SUPERFICIE}; alternate-background-color: {c.PANEL};
    color: {c.TEXTO}; gridline-color: #29313b; border: 1px solid {c.BORDE};
    selection-background-color: {c.SELECCION}; selection-color: #edf2f7; }}
QHeaderView::section {{ background: {c.CABECERA}; color: {c.SECUNDARIO};
    padding: 3px 6px; border: 0; border-bottom: 1px solid {c.BORDE}; }}
QTableCornerButton::section {{ background: {c.CABECERA}; border: 0; }}
QScrollArea {{ border: 0; background: {c.FONDO}; }}
QWidget#contenidoPagina {{ background: {c.FONDO}; }}
QStatusBar {{ background: #15171c; color: {c.SECUNDARIO};
    border-top: 1px solid #30343d; }}
QStatusBar::item {{ border: 0; }}
QToolTip {{ color: #edf2f7; background: #202d3a; border: 1px solid #42566b; padding: 5px; }}
QToolButton {{ border: 0; background: transparent; }}
QScrollBar:vertical {{ background: {c.FONDO}; width: 12px; margin: 0; }}
QScrollBar:horizontal {{ background: {c.FONDO}; height: 12px; margin: 0; }}
QScrollBar::handle {{ background: #384554; border-radius: 4px; }}
QScrollBar::handle:hover {{ background: #526575; }}
QScrollBar::handle:vertical {{ min-height: 24px; margin: 2px; }}
QScrollBar::handle:horizontal {{ min-width: 24px; margin: 2px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}
"""


def aplicar_tema(aplicacion):
    """Centraliza colores y tipografía para toda la aplicación."""
    aplicacion.setStyle("Fusion")
    paleta = QPalette()
    rol = QPalette.ColorRole
    for propiedad, color in (
        (rol.Window, c.FONDO), (rol.WindowText, c.TEXTO),
        (rol.Base, c.ENTRADA), (rol.AlternateBase, c.CABECERA),
        (rol.Text, c.TEXTO), (rol.Button, c.PANEL),
        (rol.ButtonText, c.TEXTO), (rol.Highlight, c.SELECCION),
        (rol.HighlightedText, "#edf2f7"), (rol.ToolTipBase, c.PANEL),
        (rol.ToolTipText, c.TEXTO), (rol.PlaceholderText, c.SECUNDARIO),
        (rol.Light, c.BORDE), (rol.Midlight, c.BORDE),
        (rol.Mid, c.BORDE), (rol.Dark, c.FONDO),
        (rol.Shadow, "#090c10"), (rol.Link, c.ACENTO),
    ):
        paleta.setColor(propiedad, QColor(color))
    for propiedad in (rol.Text, rol.ButtonText):
        paleta.setColor(QPalette.ColorGroup.Disabled, propiedad, QColor(c.DESHABILITADO))
    aplicacion.setPalette(paleta)
    fuente = QFont(c.FUENTE)
    fuente.setPixelSize(11)
    aplicacion.setFont(fuente)
    aplicacion.setStyleSheet(ESTILO)
