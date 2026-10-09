"""Fracciones documentadas con aceptación explícita y anexo compatible con JSON v1."""
import math

from PySide6.QtWidgets import (
    QCheckBox, QDialog, QDialogButtonBox, QHBoxLayout, QHeaderView, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout,
)

from socavacion_ll.calculo.coeficientes import TABLA_Z
from socavacion_ll.calculo.granulometria import calcular_diametro_medio, MAXIMO_FRACCIONES
from socavacion_ll.dominio.modelos import Proyecto
from socavacion_ll.dominio.validacion import validar_estructura
from .componentes import etiqueta


class DialogoGranulometria(QDialog):
    def __init__(self, notas, padre=None):
        super().__init__(padre)
        self.setWindowTitle("Diámetro medio desde fracciones")
        self.resize(700, 580)
        self.notas_previas = notas
        self.diametro_medio_mm = None
        self.notas_actualizadas = None
        vertical = QVBoxLayout(self)
        vertical.addWidget(etiqueta(
            "MTC · docs/MAN_11 HHD-2011.pdf, p. 92, ecuación 52: "
            "Dm = Σ(Di × porcentaje por intervalo) / 100. "
            "Ingrese Di representativo documentado en mm; no se infiere desde tamices."
        ))
        vertical.addWidget(etiqueta("Fuente del ensayo y muestra (1 a 500 caracteres)"))
        self.fuente = QLineEdit()
        self.fuente.setAccessibleName("Fuente del ensayo y muestra")
        vertical.addWidget(self.fuente)
        self.tabla = QTableWidget(3, 2)
        self.tabla.setHorizontalHeaderLabels(("Di representativo (mm)", "Porcentaje del intervalo (%)"))
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.setAccessibleName("Fracciones granulométricas")
        for fila in range(3):
            for columna in range(2):
                self.tabla.setItem(fila, columna, QTableWidgetItem(""))
        vertical.addWidget(self.tabla)
        botones_filas = QHBoxLayout()
        self.agregar = QPushButton("Agregar fracción")
        self.quitar = QPushButton("Quitar fracción seleccionada")
        self.agregar.clicked.connect(self._agregar_fila)
        self.quitar.clicked.connect(self._quitar_fila)
        botones_filas.addWidget(self.agregar)
        botones_filas.addWidget(self.quitar)
        vertical.addLayout(botones_filas)
        self.intervalos = QCheckBox("Confirmo porcentajes por intervalo, no acumulados")
        vertical.addWidget(self.intervalos)
        vertical.addWidget(etiqueta(
            "De 1 a 100 fracciones (límite informático). Suma 100 %, tolerancia absoluta "
            "1e-8 puntos porcentuales; no se normaliza. Aplicar anexa el detalle a Notas. "
            "El anexo se conserva al reabrir, pero no repuebla esta tabla."
        ))
        self.estado = etiqueta("Complete la fuente y las fracciones para calcular Dm.")
        vertical.addWidget(self.estado)
        botones = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        botones.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")
        self.previsualizar = botones.addButton("Calcular Dm", QDialogButtonBox.ButtonRole.ActionRole)
        self.aplicar = botones.addButton("Aplicar Dm y anexo", QDialogButtonBox.ButtonRole.AcceptRole)
        self.previsualizar.clicked.connect(self._previsualizar)
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)
        vertical.addWidget(botones)
        self.fuente.textChanged.connect(self._invalidar)
        self.tabla.itemChanged.connect(self._invalidar)
        self.intervalos.toggled.connect(self._invalidar)

    def _invalidar(self, *_):
        self.estado.setText("Datos editados: calcule Dm o aplique para revisar los valores actuales.")

    def _agregar_fila(self):
        if self.tabla.rowCount() < MAXIMO_FRACCIONES:
            fila = self.tabla.rowCount()
            self.tabla.insertRow(fila)
            for columna in range(2):
                self.tabla.setItem(fila, columna, QTableWidgetItem(""))
            self._invalidar()

    def _quitar_fila(self):
        fila = self.tabla.currentRow()
        if self.tabla.rowCount() > 1 and fila >= 0:
            self.tabla.removeRow(fila)
            self._invalidar()

    def _preparar(self):
        fuente = self.fuente.text().strip()
        if not 1 <= len(fuente) <= 500:
            raise ValueError("La fuente del ensayo requiere de 1 a 500 caracteres.")
        validar_estructura(Proyecto(notas=fuente))
        if not self.intervalos.isChecked():
            raise ValueError("Confirme que los porcentajes corresponden a intervalos, no acumulados.")
        fracciones = []
        for fila in range(self.tabla.rowCount()):
            valores = []
            for columna in range(2):
                celda = self.tabla.item(fila, columna)
                try:
                    valores.append(float(celda.text().strip().replace(",", ".") if celda else ""))
                except ValueError as error:
                    raise ValueError(f"Fracción {fila + 1}: complete Di y porcentaje numéricos.") from error
            fracciones.append((valores[0], valores[1]))
        diametro = calcular_diametro_medio(fracciones)
        lineas = ["GRANULOMETRÍA DOCUMENTADA", f"Fuente y muestra: {fuente}",
                  "MTC · docs/MAN_11 HHD-2011.pdf, p. 92, ecuación 52.",
                  "Di representativo ingresado en mm; porcentajes por intervalo, no acumulados."]
        for indice, (di, porcentaje) in enumerate(fracciones, 1):
            lineas.append(f"Fracción {indice}: Di={di!r} mm; porcentaje={porcentaje!r} %; "
                          f"Di × porcentaje={di * porcentaje!r} mm·%.")
        suma = math.fsum(di * porcentaje for di, porcentaje in fracciones)
        suma_porcentajes = math.fsum(porcentaje for _, porcentaje in fracciones)
        lineas.extend((f"Suma porcentajes={suma_porcentajes!r} %; sin normalización.",
                       f"Dm = Σ(Di × porcentaje) / 100 = {suma!r} / 100 = {diametro!r} mm."))
        notas = self.notas_previas + ("\n\n" if self.notas_previas else "") + "\n".join(lineas)
        validar_estructura(Proyecto(notas=notas))
        mensaje = f"Dm = {diametro!r} mm. "
        mensaje += ("Dm tiene celda z; las demás condiciones LL deben validarse."
                    if diametro in TABLA_Z else
                    "Dm no tabulado para z: calcular Dm no habilita LL. No se redondea ni interpola.")
        return diametro, notas, mensaje

    def _previsualizar(self):
        try:
            _, _, mensaje = self._preparar()
            self.estado.setText(mensaje)
        except ValueError as error:
            self.estado.setText(str(error))

    def accept(self):
        try:
            diametro, notas, mensaje = self._preparar()
        except ValueError as error:
            self.estado.setText(str(error))
            return
        self.diametro_medio_mm = diametro
        self.notas_actualizadas = notas
        self.estado.setText(mensaje)
        super().accept()
