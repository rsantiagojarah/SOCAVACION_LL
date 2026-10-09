"""Pantallas alimentadas por una única evaluación vigente del núcleo."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem
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
        super().__init__("Núcleo de cálculo", "Ecuación 59 MTC HHD 2011 y fuentes trazables.")
        self.estado = etiqueta("Sin cálculo vigente", "aviso")
        self.distribucion.addWidget(self.estado)
        self.tabla = crear_tabla(("Parámetro", "Valor", "Procedencia"), ())
        self.distribucion.addWidget(self.tabla)
        self.desarrollo = etiqueta("")
        self.desarrollo.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.distribucion.addWidget(self.desarrollo)
        self.fuentes = etiqueta("")
        self.distribucion.addWidget(self.fuentes)
        self.distribucion.addStretch()

    def mostrar(self, resultado):
        if resultado is None:
            self.tabla.setRowCount(0)
            self.estado.setText("Sin cálculo vigente · calcula después de completar los datos")
            self.desarrollo.clear()
            self.fuentes.clear()
            return
        self.estado.setText("\n".join(resultado.advertencias) or "Evaluación completada")
        fuente_alpha = ("DGA 2022 · pp. 68-69 · derivación por cierre"
                        if resultado.tipo_seccion == "irregular"
                        else "Schreider et al. 2001 · p. 16 · ec. 1")
        llenar_tabla(self.tabla, (
            ("alpha", f"{resultado.alpha:.12g}", fuente_alpha),
            ("beta", f"{resultado.beta:g}", "DGA 2022 · p. 69 · tabla 7-1"),
            ("mu", f"{resultado.mu:g}", resultado.detalle_mu),
            ("phi", f"{resultado.phi:g}", "MTC HHD 2011 · pp. 107-108 · agua clara"),
            ("z", f"{resultado.z:g}", "DGA 2022 · p. 69 · tabla 7-2"),
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
        self.desarrollo.setText(texto + "\nDm se evalúa en mm; no hay redondeo interno.")
        self.fuentes.setText("\n".join(resultado.fuentes))


class PaginaResultados(PaginaBase):
    RECTANGULAR = ("x (m)", "h (m)", "Hs (m)", "Sg (m)", "Cota LL (m)", "Perfil (m)")
    IRREGULAR = ("x (m)", "b (m)", "h (m)", "q (m²/s)", "Qj (m³/s)",
                 "Hs (m)", "Sg (m)", "Cota LL (m)")

    def __init__(self):
        super().__init__("Presentación de resultados", "Hs desde el agua; Sg respecto del lecho.")
        self.estado = etiqueta("Sin resultados", "aviso")
        self.distribucion.addWidget(self.estado)
        self.lienzo = None
        self.tabla = crear_tabla(self.RECTANGULAR, ())
        self.tabla.setMinimumHeight(230)
        self.distribucion.addWidget(self.tabla)
        self.distribucion.addWidget(etiqueta(
            "Perfil = fondo - max(0,Sg), solo para presentación. Sg negativa no implica "
            "sedimentación. No representa socavación total ni cota de cimentación."
        ))

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
        self.estado.setText("\n".join(resultado.advertencias) or "Resultado listo")
        self.lienzo = FigureCanvasQTAgg(crear_figura(resultado, oscuro=True))
        self.lienzo.setMinimumHeight(300)
        self.distribucion.insertWidget(3, self.lienzo)
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
        llenar_tabla(self.tabla, tuple(tuple(f"{v:.6f}" for v in fila) for fila in datos))


class PaginaReportes(PaginaBase):
    def __init__(self):
        super().__init__("Generación de reportes", "Usa Word o PDF para exportar el cálculo vigente.")
        self.estado = etiqueta("Calcula un proyecto para habilitar la exportación.", "aviso")
        self.distribucion.addWidget(self.estado)
        self.distribucion.addWidget(etiqueta(
            "La memoria incluye parámetros, coeficientes, ecuaciones, sustitución, tabla, "
            "perfil, advertencias y referencias principales/complementarias."
        ))
        self.distribucion.addStretch()

    def mostrar(self, resultado):
        self.estado.setText("Evaluación vigente lista para exportar." if resultado else
                            "Sin evaluación vigente. Calcula un proyecto para exportar.")
