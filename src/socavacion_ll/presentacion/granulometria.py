"""Fracciones documentadas con aceptación explícita y anexo compatible con JSON v1."""
import math
from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox, QDialog, QDialogButtonBox, QFileDialog, QHBoxLayout, QHeaderView, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout,
)

from socavacion_ll.calculo.coeficientes import TABLA_Z, dm_en_tramo_z
from socavacion_ll.calculo.granulometria import (
    calcular_diametro_medio, calcular_diametro_medio_por_tamices, MAXIMO_FRACCIONES,
)
from socavacion_ll.dominio.modelos import Proyecto
from socavacion_ll.dominio.validacion import validar_estructura
from socavacion_ll.infraestructura.aberturas_xlsx import leer_aberturas_retenido
from .componentes import etiqueta
from .tabla_dm import llenar_tabla, texto_anexo, texto_cierre


class DialogoGranulometria(QDialog):
    def __init__(self, notas, padre=None):
        super().__init__(padre)
        self.setWindowTitle("Diámetro medio desde fracciones")
        self.resize(980, 760)
        self.notas_previas = notas
        self.diametro_medio_mm = None
        self.texto_dm = None
        self.notas_actualizadas = None
        self.calculo_tamices = None
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
        self.importar = QPushButton("Importar aberturas XLSX…")
        self.agregar.clicked.connect(self._agregar_fila)
        self.quitar.clicked.connect(self._quitar_fila)
        self.importar.clicked.connect(self._importar)
        botones_filas.addWidget(self.agregar)
        botones_filas.addWidget(self.quitar)
        botones_filas.addWidget(self.importar)
        vertical.addLayout(botones_filas)
        vertical.addWidget(etiqueta(
            "Cálculo de Dm por aberturas: Di = (D superior + D inferior) / 2. "
            "Pi es el retenido parcial. El fondo no recibe Di."
        ))
        self.desarrollo = QTableWidget(0, 7)
        self.desarrollo.setAccessibleName("Tabla de cálculo de Dm")
        self.desarrollo.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.desarrollo.setMinimumHeight(220)
        vertical.addWidget(self.desarrollo)
        self.cierre = etiqueta("Importe el Excel o calcule para ver Σ Pi, Σ (Di × Pi) y Dm.")
        self.cierre.setAccessibleName("Cierre del cálculo de Dm")
        vertical.addWidget(self.cierre)
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
        self.fuente.textChanged.connect(self._avisar_edicion)
        self.tabla.itemChanged.connect(self._invalidar_manual)
        self.intervalos.toggled.connect(self._avisar_edicion)

    def _avisar_edicion(self, *_):
        if self.calculo_tamices is None:
            self.estado.setText("Datos editados: calcule Dm o aplique para revisar los valores actuales.")

    def _invalidar_manual(self, *_):
        self.calculo_tamices = None
        self.texto_dm = None
        self.desarrollo.setRowCount(0)
        self.cierre.setText("Importe el Excel o calcule para ver Σ Pi, Σ (Di × Pi) y Dm.")
        self.estado.setText("Datos editados: calcule Dm o aplique para revisar los valores actuales.")

    def _importar(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Importar aberturas", "", "Libro de Excel (*.xlsx)")
        if ruta:
            self.cargar_archivo(ruta)

    def cargar_archivo(self, ruta):
        try:
            lectura = leer_aberturas_retenido(ruta)
            calculo = calcular_diametro_medio_por_tamices(list(lectura.tamices), fondo=lectura.fondo)
        except ValueError as error:
            self.estado.setText(str(error))
            return
        self.fuente.blockSignals(True)
        self.intervalos.blockSignals(True)
        if not self.fuente.text().strip():
            self.fuente.setText(Path(ruta).name)
        self.intervalos.setChecked(True)
        self.fuente.blockSignals(False)
        self.intervalos.blockSignals(False)
        self.calculo_tamices = calculo
        llenar_tabla(self.desarrollo, calculo)
        self.cierre.setText(texto_cierre(calculo))
        self.estado.setText(self._mensaje(float(calculo.diametro_medio_mm), texto_cierre(calculo)))

    def _agregar_fila(self):
        if self.tabla.rowCount() < MAXIMO_FRACCIONES:
            fila = self.tabla.rowCount()
            self.tabla.insertRow(fila)
            for columna in range(2):
                self.tabla.setItem(fila, columna, QTableWidgetItem(""))
            self._invalidar_manual()

    def _quitar_fila(self):
        fila = self.tabla.currentRow()
        if self.tabla.rowCount() > 1 and fila >= 0:
            self.tabla.removeRow(fila)
            self._invalidar_manual()

    def _preparar(self):
        fuente = self.fuente.text().strip()
        if not 1 <= len(fuente) <= 500:
            raise ValueError("La fuente del ensayo requiere de 1 a 500 caracteres.")
        validar_estructura(Proyecto(notas=fuente))
        if not self.intervalos.isChecked():
            raise ValueError("Confirme que los porcentajes corresponden a intervalos, no acumulados.")
        if self.calculo_tamices is not None:
            return self._preparar_tamices(fuente)
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
        return diametro, notas, self._mensaje(diametro, f"Dm = {diametro!r} mm.")

    def _preparar_tamices(self, fuente):
        calculo = self.calculo_tamices
        diametro = float(calculo.diametro_medio_mm)
        notas = self.notas_previas + ("\n\n" if self.notas_previas else "") + texto_anexo(calculo, fuente)
        validar_estructura(Proyecto(notas=notas))
        self.texto_dm = format(calculo.diametro_medio_mm, "f")
        return diametro, notas, self._mensaje(diametro, texto_cierre(calculo))

    def _mensaje(self, diametro, cierre):
        if diametro in TABLA_Z:
            aviso = "Dm tiene celda z; las demás condiciones LL deben validarse."
        elif dm_en_tramo_z(diametro):
            aviso = ("Dm sin celda publicada: z usa la fórmula logarítmica aprobada. "
                     "No sustituye la tabla.")
        else:
            aviso = "Dm fuera de 0.05 a 750 mm: no se extrapola z. Calcular Dm no habilita LL."
        return f"{cierre} {aviso}"

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
