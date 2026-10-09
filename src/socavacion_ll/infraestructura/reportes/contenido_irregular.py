"""Bloques específicos de la memoria para una sección irregular por franjas."""
from dataclasses import dataclass

from socavacion_ll import __version__
from socavacion_ll.dominio.modelos import Resultado


@dataclass(frozen=True)
class BloqueIrregular:
    tipo: str
    contenido: object


def _n(valor: float) -> str:
    return format(valor, ".12g")


def preparar_contenido_irregular(resultado: Resultado) -> tuple[BloqueIrregular, ...]:
    proyecto = resultado.proyecto
    bloques = []

    def agregar(tipo, contenido):
        bloques.append(BloqueIrregular(tipo, contenido))

    agregar("titulo", "Memoria de cálculo de socavación general")
    agregar("parrafo", "Método de Lischtvan-Levediev para suelo no cohesivo. "
            f"Versión {__version__}. Sección irregular de una rama mojada, K=1, lecho "
            "homogéneo, agua clara y nivel de agua conocido. Requiere revisión profesional.")
    agregar("subtitulo", "Identificación del proyecto")
    for rotulo, valor in (("Proyecto", proyecto.nombre), ("Ubicación", proyecto.ubicacion),
                          ("Responsable", proyecto.responsable), ("Notas", proyecto.notas)):
        agregar("parrafo", f"{rotulo}: {valor or 'No consignado'}")
    agregar("subtitulo", "Datos de entrada y geometría")
    datos = [
        ("Caudal Q", _n(proyecto.caudal_m3s), "m³/s"),
        ("Período de retorno T", _n(proyecto.periodo_retorno_anios), "años"),
        ("Cota del agua Zw", _n(proyecto.cota_agua_m), "m"),
        ("Área mojada A", _n(resultado.area_m2), "m²"),
        ("Ancho mojado B", _n(resultado.ancho_mojado_m), "m"),
        ("Tirante medio potencial hm", _n(resultado.tirante_m), "m"),
        ("Velocidad ingresada V", _n(proyecto.velocidad_m_s), "m/s"),
        ("Velocidad de control Q/A", _n(resultado.velocidad_control_m_s), "m/s"),
        ("Pendiente", _n(proyecto.pendiente_m_m), "m/m"),
        ("Diámetro medio Dm", _n(proyecto.diametro_medio_mm), "mm"),
        ("Divisiones base N", str(proyecto.numero_franjas), ""),
        ("Franjas finales", str(resultado.numero_franjas), ""),
    ]
    agregar("tabla", (("Parámetro", "Valor", "Unidad"), datos, (10, 4, 3)))
    terreno = [(_n(p.abscisa_m), _n(p.cota_m)) for p in proyecto.puntos_terreno]
    agregar("tabla", (("Abscisa x (m)", "Cota terreno (m)"), terreno, (8.5, 8.5)))
    agregar("parrafo", "El terreno se interpola linealmente. Los puntos secos se conservan "
            "en el gráfico y se excluyen de LL. Cada franja usa área trapezoidal exacta y "
            "h_j=Área_j/ancho_j. Dm se evalúa en mm conforme al desarrollo HHD p. 108.")
    agregar("subtitulo", "Coeficientes y procedencia")
    coeficientes = [
        ("alpha", _n(resultado.alpha), "Derivación del cierre por franjas; no ecuación MTC."),
        ("beta", _n(resultado.beta), "DGA/MOP 2022, tabla 7-1, impresa 69/PDF 79."),
        ("mu", _n(resultado.mu), resultado.detalle_mu),
        ("phi", _n(resultado.phi), "Agua clara; HHD 2011, pp. 107-108."),
        ("z", _n(resultado.z), "DGA/MOP 2022, tabla 7-2, impresa 69/PDF 79."),
    ]
    agregar("tabla", (("Coeficiente", "Valor", "Selección y fuente"),
                       coeficientes, (2.5, 3, 11.5)))
    agregar("parrafo", "Mu se aplica una sola vez y no entra en alpha. Solo mu puede "
            "interpolarse respecto a L por criterio aprobado; beta, z y V usan celdas literales.")
    agregar("subtitulo", "Ecuaciones y sustitución numérica")
    for ecuacion in (
        "h_j = Área_j / ancho_j",
        "SUMA = Σ[h_j^(5/3) * ancho_j]",
        "alpha = Q / SUMA",
        "q_j = alpha * h_j^(5/3); Q_j = q_j * ancho_j",
        "hm = (SUMA / B)^(3/5)",
        "Hs_j = [q_j/(0.68*beta*mu*phi*Dm^0.28)]^(1/(1+z))",
        "Sg_j = Hs_j - h_j; Z_LL,j = Zw - Hs_j",
    ):
        agregar("ecuacion", ecuacion)
    agregar("parrafo", "La relación por franjas y hm se documenta en DGA/MOP 2022, "
            "impresas 68-69/PDF 78-79, fuente complementaria que no es norma MTC. "
            "La ecuación de Hs conserva la ecuación 59 principal del HHD 2011.")
    agregar("parrafo", f"SUMA = {_n(resultado.suma_reparto)}; "
            f"alpha = {_n(proyecto.caudal_m3s)} / {_n(resultado.suma_reparto)} "
            f"= {_n(resultado.alpha)} m^(1/3)/s")
    agregar("parrafo", f"Cierre de caudal: ΣQ_j - Q = "
            f"{_n(resultado.cierre_caudal_m3s)} m³/s (tolerancia relativa 1e-12).")
    agregar("parrafo", f"Error relativo N/2N = {_n(resultado.error_refinamiento_relativo)}; "
            "tolerancia de diagnóstico 0.001. No es una regla MTC.")
    agregar("subtitulo", "Perfil transversal y resultados por franja")
    agregar("grafico", None)
    filas = [tuple(f"{valor:.6f}" for valor in (
        p.abscisa_m, p.ancho_franja_m, p.tirante_m, p.caudal_unitario_m2s,
        p.caudal_franja_m3s, p.profundidad_hs_m, p.socavacion_m, p.cota_ll_m,
    )) for p in resultado.puntos]
    agregar("tabla", (("x centro (m)", "Ancho (m)", "h_j (m)", "q_j (m²/s)",
                       "Caudal Q_j (m³/s)", "Hs_j (m)", "Sg_j (m)", "Z_LL,j (m)"),
                      filas, (1.8, 1.8, 1.8, 2.1, 2.3, 2.2, 2.2, 2.8)))
    agregar("subtitulo", "Advertencias y límites de aplicación")
    for aviso in resultado.advertencias:
        agregar("parrafo", aviso)
    agregar("parrafo_entero", "Se excluyen suelos cohesivos, estratos, varias ramas mojadas, "
            "rugosidades distribuidas, zonas sin erosión, K distinto de 1, mezclas, "
            "socavación local y diseño de cimentaciones. Sg negativa no es sedimentación.")
    agregar("subtitulo", "Referencias técnicas")
    agregar("parrafo", "Fuentes principales: MAN_11 HHD-2011.pdf, ecuación 59 p. 108 "
            "y tabla 13 p. 107; Manual de Puentes MTC 2018, §1.2.3a, impresa 47/PDF 51.")
    agregar("parrafo", "Fuente complementaria para el reparto: DGA/MOP Chile 2022, "
            "SIT 527, impresas 68-69/PDF 78-79. No es norma peruana MTC.")
    for fuente in resultado.fuentes:
        agregar("parrafo", fuente)
    return tuple(bloques)
