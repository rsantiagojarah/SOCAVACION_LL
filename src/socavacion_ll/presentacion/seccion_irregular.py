"""Editor modal de pares abscisa/cota para el terreno irregular."""
import math

from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QFileDialog, QHeaderView, QHBoxLayout, QMessageBox, QPushButton,
    QTableWidget, QTableWidgetItem, QVBoxLayout,
)

from socavacion_ll.dominio.ejemplo_irregular import PERFIL_EJEMPLO_IRREGULAR
from socavacion_ll.dominio.modelos import PuntoTerreno
from socavacion_ll.infraestructura.hec_ras_xlsx import leer_seccion_hec_ras
from .componentes import etiqueta
from .importacion_hec_ras import DialogoImportacionHecRas


class DialogoSeccionIrregular(QDialog):
    def __init__(self, puntos: tuple[PuntoTerreno, ...], notas="", padre=None):
        super().__init__(padre)
        self._notas_base = notas
        self._importacion = None
        self.setWindowTitle("Editar sección transversal irregular")
        self.resize(560, 520)
        vertical = QVBoxLayout(self)
        vertical.addWidget(etiqueta(
            "Ingrese abscisa x y cota del terreno en orden no decreciente. "
            "Se admiten tramos verticales; el terreno es lineal entre puntos. "
            "El perfil ejemplo asume la cota de agua 103 m: bermas secas y una rama mojada."
        ))
        self.tabla = QTableWidget(0, 2)
        self.tabla.setHorizontalHeaderLabels(("Abscisa x (m)", "Cota (m)"))
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        vertical.addWidget(self.tabla)
        acciones = QHBoxLayout()
        self.boton_importar = QPushButton("Importar HEC-RAS XLSX…")
        self.boton_importar.clicked.connect(self._importar)
        acciones.addWidget(self.boton_importar)
        for texto, funcion in (
            ("Agregar punto", self._agregar),
            ("Eliminar fila", self._eliminar),
            ("Cargar perfil ejemplo", self._ejemplo),
        ):
            boton = QPushButton(texto)
            boton.clicked.connect(funcion)
            acciones.addWidget(boton)
        vertical.addLayout(acciones)
        botones = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)
        vertical.addWidget(botones)
        self._cargar(puntos)

    def _importar(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Importar sección HEC-RAS", "", "Libro de Excel (*.xlsx)"
        )
        if not ruta:
            return
        try:
            seccion = leer_seccion_hec_ras(ruta)
        except ValueError as error:
            QMessageBox.warning(self, "No se pudo importar", str(error))
            return
        confirmacion = DialogoImportacionHecRas(seccion, self)
        if confirmacion.exec() == QDialog.DialogCode.Accepted:
            self._aplicar_importacion_confirmada(seccion, confirmacion)
        confirmacion.deleteLater()

    def _aplicar_importacion_confirmada(self, seccion, confirmacion):
        self._cargar(seccion.puntos_terreno)
        perfil = confirmacion.perfil_seleccionado()
        bloque = confirmacion.nota_procedencia()
        notas = self._notas_base.rstrip()
        self._importacion = (perfil.cota_m, f"{notas}\n\n{bloque}" if notas else bloque)

    def obtener_importacion(self):
        return self._importacion

    def _agregar(self, x="", cota=""):
        fila = self.tabla.rowCount()
        self.tabla.insertRow(fila)
        self.tabla.setItem(fila, 0, QTableWidgetItem(str(x)))
        self.tabla.setItem(fila, 1, QTableWidgetItem(str(cota)))

    def _eliminar(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            fila = self.tabla.rowCount() - 1
        if fila >= 0:
            self.tabla.removeRow(fila)

    def _ejemplo(self):
        self._cargar(PERFIL_EJEMPLO_IRREGULAR)

    def _cargar(self, puntos):
        self.tabla.setRowCount(0)
        for punto in puntos:
            self._agregar(punto.abscisa_m, punto.cota_m)
        while self.tabla.rowCount() < 2:
            self._agregar()

    def obtener_puntos(self) -> tuple[PuntoTerreno, ...]:
        if not 2 <= self.tabla.rowCount() <= 200:
            raise ValueError("Ingrese entre 2 y 200 puntos de terreno.")
        puntos = []
        for fila in range(self.tabla.rowCount()):
            valores = []
            for columna in range(2):
                elemento = self.tabla.item(fila, columna)
                texto = elemento.text().strip().replace(",", ".") if elemento else ""
                try:
                    valor = float(texto)
                except ValueError as error:
                    raise ValueError(f"Fila {fila + 1}: ingrese x y cota numéricos.") from error
                if not math.isfinite(valor):
                    raise ValueError(f"Fila {fila + 1}: x y cota deben ser finitos.")
                valores.append(valor)
            puntos.append(PuntoTerreno(*valores))
        if any(b.abscisa_m < a.abscisa_m for a, b in zip(puntos, puntos[1:])):
            raise ValueError("Las abscisas no pueden ser decrecientes.")
        if any(a == b for a, b in zip(puntos, puntos[1:])):
            raise ValueError("No repita dos puntos idénticos consecutivos.")
        return tuple(puntos)

    def accept(self):
        try:
            self.obtener_puntos()
        except ValueError as error:
            QMessageBox.warning(self, "Perfil no válido", str(error))
            return
        super().accept()
