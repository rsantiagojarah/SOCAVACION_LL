"""Pantallas alimentadas por una única evaluación vigente del núcleo."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSizePolicy, QTableWidgetItem
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from socavacion_ll.infraestructura.graficos import crear_figura
from .componentes import PaginaBase, crear_tabla, etiqueta


def llenar_tabla(tabla, filas):
    tabla.setRowCount(len(filas))
    for fila, valores in enumerate(filas):
        for columna, valor in enumerate(valores):
            elemento = QTableWidgetItem(str(valor))
            elemento.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            elemento.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            tabla.setItem(fila, columna, elemento)
    tabla.resizeRowsToContents()


class PaginaNucleo(PaginaBase):
    def __init__(self):
        super().__init__(compacto=True)
        self.estado = etiqueta("Sin coeficientes", "aviso")
        self.distribucion.addWidget(self.estado)
        self.tabla = crear_tabla(("Parámetro", "Valor", "Procedencia"), ())
        self.tabla.setMinimumHeight(96)
        self.tabla.verticalHeader().setDefaultSectionSize(22)
        self.tabla.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.distribucion.addWidget(self.tabla, 1)
        self.desarrollo = etiqueta("")
        self.fuentes = etiqueta("")
        self.desarrollo.hide()
        self.fuentes.hide()

    def mostrar(self, resultado):
        if resultado is None:
            self.tabla.setRowCount(0)
            self.estado.setText("Sin coeficientes")
            self.tabla.setToolTip("")
            self.desarrollo.clear()
            self.fuentes.clear()
            return
        self.estado.setText("Coeficientes de la evaluación vigente")
        fuente_alpha = ("DGA 2022 · pp. 68-69 · derivación por cierre"
                        if resultado.tipo_seccion == "irregular"
                        else "Schreider et al. 2001 · p. 16 · ec. 1")
        llenar_tabla(self.tabla, (
            ("alpha", f"{resultado.alpha:.2f}", fuente_alpha),
            ("beta", f"{resultado.beta:.2f}", resultado.detalle_beta or "DGA 2022 · p. 69 · tabla 7-1"),
            ("mu", f"{resultado.mu:.2f}", resultado.detalle_mu),
            ("phi", f"{resultado.phi:.2f}", "MTC HHD 2011 · pp. 107-108 · agua clara"),
            ("z", f"{resultado.z:.2f}", resultado.detalle_z or "DGA 2022 · p. 69 · tabla 7-2"),
        ))
        punto = resultado.puntos[0]
        if resultado.tipo_seccion == "irregular":
            texto = (
                "alpha = Q/SUMA[h_j^(5/3)*ancho_j]; q_j = alpha*h_j^(5/3)\n"
                "Hs_j = [q_j/(0.68*beta*mu*phi*Dm^0.28)]^(1/(1+z))\n"
                f"A = {resultado.area_m2:.12g} m²; B = {resultado.ancho_mojado_m:.12g} m; "
                f"hm = {resultado.tirante_m:.12g} m; Q/A = {resultado.velocidad_control_m_s:.12g} m/s\n"
                f"SUMA = {resultado.suma_reparto:.12g}; alpha = {resultado.alpha:.12g}; "
                f"franjas = {resultado.numero_franjas}\n"
                f"Cierre ΣQ_j-Q = {resultado.cierre_caudal_m3s:.12g} m³/s; "
                f"error N/2N = {resultado.error_refinamiento_relativo:.12g}\n"
                f"Primera franja: q={punto.caudal_unitario_m2s:.12g} m²/s; "
                f"Hs={punto.profundidad_hs_m:.12g} m; Sg={punto.socavacion_m:.12g} m"
            )
        else:
            texto = (
                "Hs = [alpha*h^(5/3)/(0.68*beta*mu*phi*Dm^0.28)]^(1/(1+z))\n"
                f"A = {resultado.area_m2:.12g} m²; h = {resultado.tirante_m:.12g} m; "
                f"Q/A = {resultado.velocidad_control_m_s:.12g} m/s\n{resultado.detalle_mu}\n"
                f"Hs = ({resultado.numerador:.12g}/{resultado.denominador:.12g})"
                f"^{resultado.exponente:.12g} = {punto.profundidad_hs_m:.12g} m\n"
                f"Sg = Hs-h = {punto.socavacion_m:.12g} m"
            )
        detalle = texto + "\nDm se evalúa en mm; no hay redondeo interno.\n" + "\n".join(resultado.fuentes)
        self.desarrollo.setText(detalle)
        self.fuentes.setText("\n".join(resultado.fuentes))
        self.tabla.setToolTip(detalle)


class PaginaResultados(PaginaBase):
    RECTANGULAR = ("x (m)", "h (m)", "Hs (m)", "Sg (m)", "Cota LL (m)", "Perfil (m)")
    IRREGULAR = ("x (m)", "b (m)", "h (m)", "q (m²/s)", "Qj (m³/s)",
                 "Hs (m)", "Sg (m)", "Cota LL (m)")

    def __init__(self):
        super().__init__(compacto=True)
        self.estado = etiqueta("Sin resultados", "aviso")
        self.estado.setMaximumHeight(52)
        self.distribucion.addWidget(self.estado)
        self.lienzo = None
        self.tabla = crear_tabla(self.RECTANGULAR, ())
        self.tabla.setMinimumHeight(120)
        self.tabla.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.tabla.setToolTip(
            "Perfil = fondo - max(0, Sg), solo para el dibujo. "
            "Sg negativa no es sedimentación ni cota de cimentación."
        )
        self.distribucion.addWidget(self.tabla)

    def mostrar(self, resultado):
        if self.lienzo is not None:
            self.distribucion.removeWidget(self.lienzo)
            self.lienzo.hide()
            self.lienzo.setParent(None)
            self.lienzo.figure.clear()
            self.lienzo.deleteLater()
            self.lienzo = None
        if resultado is None:
            self.estado.setText("Sin resultados vigentes · recalcula después de editar")
            self.tabla.setRowCount(0)
            return
        texto = "\n".join(resultado.advertencias) or "Resultado listo"
        self.estado.setText(texto)
        self.estado.setToolTip(texto)
        figura = crear_figura(resultado, oscuro=True)
        figura.set_dpi(96)
        figura.set_size_inches(6.2, 3.4)
        self.lienzo = FigureCanvasQTAgg(figura)
        self.lienzo.setMinimumHeight(220)
        self.lienzo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.distribucion.insertWidget(self.distribucion.indexOf(self.tabla), self.lienzo, 1)
        irregular = resultado.tipo_seccion == "irregular"
        cabecera = self.IRREGULAR if irregular else self.RECTANGULAR
        self.tabla.setColumnCount(len(cabecera))
        self.tabla.setHorizontalHeaderLabels(cabecera)
        if irregular:
            datos = ((p.abscisa_m, p.ancho_franja_m, p.tirante_m,
                      p.caudal_unitario_m2s, p.caudal_franja_m3s,
                      p.profundidad_hs_m, p.socavacion_m, p.cota_ll_m)
                     for p in resultado.puntos)
        else:
            datos = ((p.abscisa_m, p.tirante_m, p.profundidad_hs_m,
                      p.socavacion_m, p.cota_ll_m, p.cota_perfil_m)
                     for p in resultado.puntos)
        llenar_tabla(self.tabla, tuple(tuple(f"{v:.2f}" for v in fila) for fila in datos))
