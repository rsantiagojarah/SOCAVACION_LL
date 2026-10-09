"""Confirmación explícita de datos HEC-RAS antes de aplicarlos al proyecto."""
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QVBoxLayout,
)

from .componentes import etiqueta


class DialogoImportacionHecRas(QDialog):
    def __init__(self, seccion, padre=None):
        super().__init__(padre)
        self.seccion = seccion
        self.setWindowTitle("Confirmar importación HEC-RAS")
        self.setMinimumWidth(520)
        vertical = QVBoxLayout(self)
        vertical.addWidget(etiqueta(
            "Revise el resumen. La importación reemplazará el terreno irregular "
            "y la cota de agua; los demás parámetros se conservarán.", "aviso",
        ))
        margenes = "; ".join(format(valor, ".15g")
                              for valor in seccion.estaciones_margen_m) or "No disponibles"
        self.resumen = etiqueta(
            f"Archivo: {seccion.archivo}\nHoja: {seccion.hoja}\n"
            f"Terreno Ground: {len(seccion.puntos_terreno)} puntos\n"
            f"Bank Sta: {margenes} m"
        )
        vertical.addWidget(self.resumen)
        formulario = QFormLayout()
        self.perfiles = QComboBox()
        for perfil in seccion.perfiles_agua:
            self.perfiles.addItem(f"{perfil.nombre} · {perfil.cota_m:.15g} m", perfil)
        formulario.addRow("Perfil de agua", self.perfiles)
        vertical.addLayout(formulario)
        self.confirmar_metros = QCheckBox(
            "Confirmo que abscisas, cotas, nivel de agua y Bank Sta están en metros"
        )
        vertical.addWidget(self.confirmar_metros)
        botones = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.boton_aceptar = botones.button(QDialogButtonBox.StandardButton.Ok)
        self.boton_aceptar.setText("Importar")
        self.boton_aceptar.setEnabled(False)
        self.confirmar_metros.toggled.connect(self.boton_aceptar.setEnabled)
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)
        vertical.addWidget(botones)

    def perfil_seleccionado(self):
        return self.perfiles.currentData()

    def nota_procedencia(self) -> str:
        perfil = self.perfil_seleccionado()
        margenes = "; ".join(format(valor, ".15g")
                              for valor in self.seccion.estaciones_margen_m) or "No disponibles"
        return (
            "[Importación HEC-RAS XLSX]\n"
            f"Archivo: {self.seccion.archivo}\n"
            f"Hoja: {self.seccion.hoja}\n"
            f"Perfil de agua: {perfil.nombre}\n"
            f"Cota de agua: {perfil.cota_m:.15g} m\n"
            f"Bank Sta: {margenes} m\n"
            "Unidades confirmadas por el usuario: m"
        )
