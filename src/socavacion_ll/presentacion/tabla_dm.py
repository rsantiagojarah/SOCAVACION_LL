"""Presenta la tabla técnica de Dm. No recalcula los aportes."""
from decimal import Decimal

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem

from socavacion_ll.calculo.granulometria import CalculoDmTamices

COLUMNAS = (
    "N°", "Tamiz / fracción", "D superior (mm)", "D inferior (mm)",
    "Di (mm)", "Pi retenido parcial (%)", "Di * Pi",
)


def llenar_tabla(tabla: QTableWidget, calculo: CalculoDmTamices) -> None:
    tabla.setColumnCount(len(COLUMNAS))
    tabla.setHorizontalHeaderLabels(COLUMNAS)
    tabla.setRowCount(len(calculo.filas))
    for indice, fila in enumerate(calculo.filas):
        valores = (
            str(indice + 1), fila.fraccion, _texto(fila.d_superior_mm), _texto(fila.d_inferior_mm),
            _texto(fila.di_mm), _texto(fila.porcentaje), _texto(fila.aporte),
        )
        for columna, valor in enumerate(valores):
            celda = QTableWidgetItem(valor)
            celda.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            tabla.setItem(indice, columna, celda)


def texto_cierre(calculo: CalculoDmTamices) -> str:
    return (
        f"Σ Pi = {_texto(calculo.suma_porcentajes)} %. "
        f"Σ (Di × Pi) = {_texto(calculo.suma_productos)}. "
        f"Dm = Σ(Di × Pi) / 100 = {format(calculo.diametro_medio_mm, 'f')} mm."
    )


def texto_anexo(calculo: CalculoDmTamices, fuente: str) -> str:
    lineas = [
        "GRANULOMETRÍA POR ABERTURAS",
        f"Fuente y muestra: {fuente}",
        "Di = (D superior + D inferior) / 2. Pi es el retenido parcial ingresado.",
        "El fondo no recibe Di. El denominador es 100. No se normaliza.",
        " | ".join(COLUMNAS),
    ]
    for indice, fila in enumerate(calculo.filas, start=1):
        lineas.append(" | ".join((
            str(indice), fila.fraccion, _texto(fila.d_superior_mm), _texto(fila.d_inferior_mm),
            _texto(fila.di_mm), _texto(fila.porcentaje), _texto(fila.aporte),
        )))
    lineas.append(texto_cierre(calculo))
    return "\n".join(lineas)


def _texto(valor: Decimal | None) -> str:
    if valor is None:
        return "--"
    texto = format(valor, "f")
    return texto.rstrip("0").rstrip(".") if "." in texto else texto
