"""Consulta de las constantes del cálculo, sin selección ni edición de entradas."""
from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QHeaderView, QTabWidget, QVBoxLayout, QWidget,
)

from socavacion_ll.calculo.coeficientes import LUCES_M, TABLA_BETA, TABLA_MU, TABLA_Z
from .componentes import crear_tabla, etiqueta


class ConsultaTablas(QDialog):
    def __init__(self, padre=None):
        super().__init__(padre)
        self.setWindowTitle("Tablas y fuentes · Socavación LL")
        self.resize(880, 560)
        self.setMinimumSize(600, 400)
        self.tablas = {}
        self.fuentes = {}
        vertical = QVBoxLayout(self)
        vertical.addWidget(etiqueta(
            "Consulta de solo lectura. No aplica valores al proyecto. "
            "Beta/z requieren celda exacta. Mu interpola linealmente solo L, sin extrapolar."
        ))
        self.pestanas = QTabWidget()
        vertical.addWidget(self.pestanas)
        complemento = (
            "Fuente complementaria, no tabla MTC: "
            "docs/complementarias/DGA_2022_Cachapoal_SIT527.pdf, "
            "p. impresa 69 / PDF 79, atribuida a Mery (2013). "
        )
        self._agregar(
            "beta", "beta · Frecuencia", ("T (años)", "beta"),
            [(f"{periodo:g}", f"{valor:.2f}") for periodo, valor in TABLA_BETA.items()],
            complemento + "Tabla 7-1. Se requiere T exacto.",
        )
        self._agregar(
            "z", "z · Diámetro", ("Dm (mm)", "z (X en la fuente)"),
            [(f"{diametro:g}", f"{valor:.2f}") for diametro, valor in TABLA_Z.items()],
            complemento + "Tabla 7-2. Se requiere Dm exacto; Dm no equivale a D50. "
            "z es el exponente tabulado, no 1/(1+z).",
        )
        self._agregar(
            "mu", "mu · Contracción", ("V (m/s) / L (m)", *map(str, LUCES_M)),
            [(str(velocidad), *(self._decimal_mu(valor) for valor in valores))
             for velocidad, valores in TABLA_MU.items()],
            "Fuente principal: docs/MAN_11 HHD-2011.pdf, p. 107, tabla 13. "
            "Sin obstáculos: mu = 1. Con obstáculos: L entre 10 y 200 m se interpola "
            "linealmente entre columnas contiguas por criterio aprobado por el usuario; "
            "la tabla MTC no publica esa regla. Categorías <1 y >4 literales. "
            "3.5 < V ≤ 4 m/s no tiene fila publicada y se bloquea. "
            "Las columnas corresponden a L, no al ancho efectivo B.",
        )
        botones = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        botones.button(QDialogButtonBox.StandardButton.Close).setText("Cerrar")
        botones.rejected.connect(self.reject)
        vertical.addWidget(botones)

    @staticmethod
    def _decimal_mu(valor):
        # Mostrar al menos dos decimales; preservar más si una constante los contiene.
        texto = str(valor)
        return texto if len(texto.partition(".")[2]) > 2 else f"{valor:.2f}"

    def _agregar(self, clave, titulo, encabezados, filas, fuente):
        pagina = QWidget()
        vertical = QVBoxLayout(pagina)
        self.fuentes[clave] = etiqueta(fuente)
        vertical.addWidget(self.fuentes[clave])
        tabla = crear_tabla(encabezados, filas)
        if clave == "mu":
            tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        tabla.setAccessibleName(titulo)
        self.tablas[clave] = tabla
        vertical.addWidget(tabla)
        self.pestanas.addTab(pagina, titulo)
