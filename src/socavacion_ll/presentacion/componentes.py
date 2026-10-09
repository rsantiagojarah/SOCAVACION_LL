"""Componentes reutilizables de la vista previa."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView, QFormLayout, QFrame, QHeaderView, QLabel, QLineEdit,
    QScrollArea, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)


def etiqueta(texto, nombre="subtitulo"):
    elemento = QLabel(texto)
    elemento.setObjectName(nombre)
    elemento.setWordWrap(True)
    elemento.setTextFormat(Qt.TextFormat.PlainText)
    return elemento


def crear_formulario(titulo, campos):
    tarjeta = QFrame()
    tarjeta.setObjectName("tarjeta")
    distribucion = QVBoxLayout(tarjeta)
    distribucion.setContentsMargins(14, 10, 14, 14)
    distribucion.addWidget(etiqueta(titulo, "grupo"))
    formulario = QFormLayout()
    formulario.setHorizontalSpacing(18)
    formulario.setVerticalSpacing(9)
    formulario.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
    for nombre, valor in campos:
        campo = QLineEdit(valor)
        campo.setReadOnly(True)
        campo.setAccessibleName(nombre)
        campo.setToolTip("Dato ilustrativo de solo lectura; no se guarda ni se calcula.")
        formulario.addRow(nombre, campo)
    distribucion.addLayout(formulario)
    return tarjeta


def crear_tabla(encabezados, filas):
    tabla = QTableWidget(len(filas), len(encabezados))
    tabla.setHorizontalHeaderLabels(encabezados)
    tabla.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    tabla.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    tabla.setAlternatingRowColors(True)
    tabla.verticalHeader().setVisible(False)
    tabla.verticalHeader().setDefaultSectionSize(28)
    tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    tabla.setMinimumHeight(175)
    for fila, valores in enumerate(filas):
        for columna, valor in enumerate(valores):
            celda = QTableWidgetItem(str(valor))
            celda.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            celda.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            tabla.setItem(fila, columna, celda)
    return tabla


class PaginaBase(QScrollArea):
    """El desplazamiento evita recortar formularios al reducir la ventana."""

    def __init__(self, titulo, descripcion):
        super().__init__()
        self.setWidgetResizable(True)
        contenido = QWidget()
        contenido.setObjectName("contenidoPagina")
        self.distribucion = QVBoxLayout(contenido)
        self.distribucion.setContentsMargins(20, 16, 20, 16)
        self.distribucion.setSpacing(12)
        self.distribucion.addWidget(etiqueta(titulo, "titulo"))
        self.distribucion.addWidget(etiqueta(descripcion))
        self.setWidget(contenido)

    def agregar_estado(self, titulo, detalle):
        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta")
        distribucion = QVBoxLayout(tarjeta)
        estado = etiqueta(titulo, "estadoVacio")
        estado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        distribucion.addWidget(estado)
        texto = etiqueta(detalle)
        texto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        distribucion.addWidget(texto)
        distribucion.setContentsMargins(20, 24, 20, 30)
        self.distribucion.addWidget(tarjeta)
        return estado
