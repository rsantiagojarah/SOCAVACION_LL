"""Formulario editable para proyectos rectangulares o irregulares."""
import math

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QFormLayout, QFrame, QHBoxLayout, QLineEdit,
    QPlainTextEdit, QPushButton, QSpinBox, QVBoxLayout,
)

from socavacion_ll import __version__
from socavacion_ll.calculo.coeficientes import TABLA_Z
from socavacion_ll.dominio.modelos import Proyecto
from .campos_ingreso import GRUPOS, TEXTOS
from .componentes import PaginaBase, etiqueta
from .consulta_tablas import ConsultaTablas
from .granulometria import DialogoGranulometria
from .seccion_irregular import DialogoSeccionIrregular

class PaginaIngreso(PaginaBase):
    cambiado = Signal()

    def __init__(self):
        super().__init__("Ingreso de datos", "Un proyecto por escenario. Unidades SI; Dm en mm.")
        self.campos = {}
        self._cargando = False
        self.puntos_terreno = ()
        self.sin_obstaculos = QCheckBox("Sin obstáculos en el cauce")
        self.ayuda_luz = etiqueta("")
        self.sin_obstaculos.toggled.connect(self._actualizar_luz)
        self.sin_obstaculos.toggled.connect(self._notificar)
        self.distribucion.addWidget(etiqueta(
            f"VERSIÓN {__version__} · Sección rectangular o irregular de una rama mojada. "
            "Suelo granular homogéneo, agua clara y método LL.", "aviso",
        ))
        for inicio in (0, 2):
            horizontal = QHBoxLayout()
            horizontal.setSpacing(14)
            for titulo, campos in GRUPOS[inicio:inicio + 2]:
                horizontal.addWidget(self._grupo(titulo, campos))
            self.distribucion.addLayout(horizontal)
        self.distribucion.addWidget(self._controles_seccion())
        self.no_cohesivo = QCheckBox(
            "Confirmo material homogéneo no cohesivo según estudio geotécnico"
        )
        self.agua_clara = QCheckBox("Agua clara (única condición habilitada)")
        for control in (self.no_cohesivo, self.agua_clara):
            control.toggled.connect(self._notificar)
            self.distribucion.addWidget(control)
        self.boton_tablas = QPushButton("Consultar tablas beta / z / mu y fuentes")
        self.boton_tablas.clicked.connect(self._consultar_tablas)
        self.distribucion.addWidget(self.boton_tablas)
        self.distribucion.addWidget(etiqueta(
            "T admitidos: 2, 5, 10, 20, 50, 100, 500, 1000 años. "
            "Dm debe corresponder a su tabla; mu interpola solo L. No confundir Dm con D50. "
            "El nivel del agua proviene del estudio hidráulico. Se admite coma o punto decimal."
        ))
        self.distribucion.addStretch()
        self.cargar(Proyecto())

    def _grupo(self, titulo, campos):
        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta")
        vertical = QVBoxLayout(tarjeta)
        vertical.setContentsMargins(14, 10, 14, 14)
        vertical.addWidget(etiqueta(titulo, "grupo"))
        formulario = QFormLayout()
        formulario.setHorizontalSpacing(12)
        formulario.setVerticalSpacing(9)
        for nombre, rotulo in campos:
            if nombre == "numero_puntos":
                control = QSpinBox()
                control.setRange(2, 201)
                control.valueChanged.connect(self._notificar)
            elif nombre == "notas":
                control = QPlainTextEdit()
                control.setPlaceholderText("Registrar datum vertical y origen de los datos.")
                control.setMinimumHeight(64)
                control.setMaximumHeight(90)
                control.textChanged.connect(self._notificar)
            else:
                control = QLineEdit()
                control.textChanged.connect(self._notificar)
            control.setAccessibleName(rotulo)
            self.campos[nombre] = control
            formulario.addRow(rotulo, control)
            if nombre == "diametro_medio_mm":
                self.boton_granulometria = QPushButton("Obtener Dm desde fracciones…")
                self.ayuda_granulometria = etiqueta("")
                self.boton_granulometria.clicked.connect(self._calcular_granulometria)
                formulario.addRow(self.boton_granulometria)
                formulario.addRow(self.ayuda_granulometria)
            if nombre == "luz_libre_m":
                formulario.addRow(self.sin_obstaculos)
                formulario.addRow(self.ayuda_luz)
        vertical.addLayout(formulario)
        return tarjeta

    def _controles_seccion(self):
        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta")
        horizontal = QHBoxLayout(tarjeta)
        self.tipo_seccion = QComboBox()
        self.tipo_seccion.addItem("Rectangular", "rectangular")
        self.tipo_seccion.addItem("Irregular por franjas", "irregular")
        self.tipo_seccion.currentIndexChanged.connect(self._actualizar_tipo)
        self.tipo_seccion.currentIndexChanged.connect(self._notificar)
        self.numero_franjas = QSpinBox()
        self.numero_franjas.setRange(2, 200)
        self.numero_franjas.valueChanged.connect(self._notificar)
        self.boton_seccion = QPushButton()
        self.boton_seccion.clicked.connect(self._editar_seccion)
        for texto, control in (("Tipo de sección", self.tipo_seccion),
                               ("Franjas base N", self.numero_franjas)):
            horizontal.addWidget(etiqueta(texto))
            horizontal.addWidget(control)
        horizontal.addWidget(self.boton_seccion)
        return tarjeta

    def _notificar(self, *_):
        if not self._cargando:
            self.cambiado.emit()

    def _actualizar_luz(self, sin_obstaculos):
        campo = self.campos["luz_libre_m"]
        restaurada = False
        if sin_obstaculos and not self._cargando:
            try:
                valor = float(campo.text().strip().replace(",", "."))
                restaurada = not math.isfinite(valor) or valor < 0
            except ValueError:
                restaurada = True
            if restaurada:
                self._cargando = True
                campo.setText("0")
                self._cargando = False
        campo.setEnabled(not sin_obstaculos)
        if sin_obstaculos:
            sufijo = (" L tenía un valor no válido; se restauró L a 0."
                      if restaurada else " Se conserva su valor.")
            self.ayuda_luz.setText("Sin obstáculos: mu = 1; L no se utiliza." + sufijo)
        else:
            self.ayuda_luz.setText(
                "Con obstáculos: interpolación lineal de mu respecto a L entre 10 y 200 m; "
                "la fila V es literal."
            )

    def _actualizar_ayuda_dm(self, valor):
        texto = "" if valor in TABLA_Z else "Dm no tabulado para z: calcular Dm no habilita LL."
        self.ayuda_granulometria.setText(texto)

    def _actualizar_tipo(self, *_):
        irregular = self.tipo_seccion.currentData() == "irregular"
        for nombre in ("ancho_m", "cota_fondo_m", "numero_puntos"):
            self.campos[nombre].setEnabled(not irregular)
        self.numero_franjas.setEnabled(irregular)
        self.boton_seccion.setEnabled(irregular)
        self.boton_seccion.setText(f"Editar perfil irregular · {len(self.puntos_terreno)} puntos")

    def establecer_puntos_terreno(self, puntos):
        self.puntos_terreno = tuple(puntos)
        self._actualizar_tipo()
        self._notificar()

    def establecer_importacion_hec_ras(self, puntos, cota_agua_m, notas):
        self._cargando = True
        self.campos["cota_agua_m"].setText(repr(cota_agua_m))
        self.campos["notas"].setPlainText(notas)
        self._cargando = False
        self.establecer_puntos_terreno(puntos)

    def _editar_seccion(self):
        dialogo = DialogoSeccionIrregular(
            self.puntos_terreno, self.campos["notas"].toPlainText(), self
        )
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            importacion = dialogo.obtener_importacion()
            if importacion:
                self.establecer_importacion_hec_ras(dialogo.obtener_puntos(), *importacion)
            else:
                self.establecer_puntos_terreno(dialogo.obtener_puntos())
        dialogo.deleteLater()

    def _consultar_tablas(self):
        dialogo = ConsultaTablas(self)
        dialogo.exec()
        dialogo.deleteLater()

    def _calcular_granulometria(self):
        dialogo = DialogoGranulometria(self.campos["notas"].toPlainText(), self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            self._cargando = True
            self.campos["diametro_medio_mm"].setText(repr(dialogo.diametro_medio_mm))
            self.campos["notas"].setPlainText(dialogo.notas_actualizadas)
            self._actualizar_ayuda_dm(dialogo.diametro_medio_mm)
            self._cargando = False
            self._notificar()
        dialogo.deleteLater()

    def cargar(self, proyecto):
        self._cargando = True
        try:
            for nombre, campo in self.campos.items():
                valor = getattr(proyecto, nombre)
                if nombre == "numero_puntos":
                    campo.setValue(valor)
                elif nombre == "notas":
                    campo.setPlainText(valor)
                else:
                    campo.setText(str(valor))
            for nombre in ("no_cohesivo", "agua_clara", "sin_obstaculos"):
                getattr(self, nombre).setChecked(getattr(proyecto, nombre))
            self.puntos_terreno = proyecto.puntos_terreno
            self.tipo_seccion.setCurrentIndex(self.tipo_seccion.findData(proyecto.tipo_seccion))
            self.numero_franjas.setValue(proyecto.numero_franjas)
            self._actualizar_ayuda_dm(proyecto.diametro_medio_mm)
            self._actualizar_luz(proyecto.sin_obstaculos)
            self._actualizar_tipo()
        finally:
            self._cargando = False

    def obtener_proyecto(self):
        valores = {}
        for nombre, campo in self.campos.items():
            if nombre == "numero_puntos":
                campo.interpretText()
                valores[nombre] = campo.value()
            elif nombre == "notas":
                valores[nombre] = campo.toPlainText()
            elif nombre in TEXTOS:
                valores[nombre] = campo.text()
            else:
                try:
                    valor = float(campo.text().strip().replace(",", "."))
                except ValueError as error:
                    raise ValueError(f"{campo.accessibleName()}: ingresa un número válido.") from error
                if not math.isfinite(valor):
                    raise ValueError(f"{campo.accessibleName()}: el número debe ser finito.")
                valores[nombre] = valor
        for nombre in ("no_cohesivo", "agua_clara", "sin_obstaculos"):
            valores[nombre] = getattr(self, nombre).isChecked()
        valores["tipo_seccion"] = self.tipo_seccion.currentData()
        valores["puntos_terreno"] = self.puntos_terreno
        self.numero_franjas.interpretText()
        valores["numero_franjas"] = self.numero_franjas.value()
        return Proyecto(**valores)
