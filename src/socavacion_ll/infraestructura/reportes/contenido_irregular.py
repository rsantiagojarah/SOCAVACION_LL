"""Bloques específicos de la memoria para una sección irregular por franjas."""
from dataclasses import dataclass

from socavacion_ll.dominio.modelos import Resultado

from .desarrollo import identificacion, indice, n, paso, portada


@dataclass(frozen=True)
class BloqueIrregular:
    tipo: str
    contenido: object


def preparar_contenido_irregular(resultado: Resultado) -> tuple[BloqueIrregular, ...]:
    proyecto = resultado.proyecto
    bloques = []

    def agregar(tipo, contenido):
        bloques.append(BloqueIrregular(tipo, contenido))

    portada(agregar, resultado, "Sección irregular, una rama mojada, K=1",
            "Terreno · reparto por franjas · ecuación 59 · perfil · referencias")
    indice(agregar, (
        ("1", "Identificación del proyecto"),
        ("2", "Datos hidráulicos y terreno"),
        ("3", "Reparto de caudal y coeficiente alpha"),
        ("4", "Coeficientes beta, mu, phi y z"),
        ("5", "Profundidad Hs de la franja gobernante"),
        ("6", "Cierre de caudal y control N/2N"),
        ("7", "Perfil y resultados por franja"),
        ("8", "Advertencias, límites y referencias"),
    ))
    identificacion(agregar, proyecto)
    _datos(agregar, resultado)
    _reparto(agregar, resultado)
    _coeficientes(agregar, resultado)
    _franja(agregar, resultado)
    _controles(agregar, resultado)
    _perfil(agregar, resultado)
    _cierres(agregar, resultado)
    return tuple(bloques)


def _datos(agregar, resultado):
    proyecto = resultado.proyecto
    agregar("subtitulo", "2. Datos de entrada y geometría")
    datos = (
        ("Caudal Q", n(proyecto.caudal_m3s), "m³/s"),
        ("Período de retorno T", n(proyecto.periodo_retorno_anios), "años"),
        ("Cota del agua Zw", n(proyecto.cota_agua_m), "m"),
        ("Área mojada A", n(resultado.area_m2), "m²"),
        ("Ancho mojado B", n(resultado.ancho_mojado_m), "m"),
        ("Tirante medio potencial hm", n(resultado.tirante_m), "m"),
        ("Velocidad ingresada V", n(proyecto.velocidad_m_s), "m/s"),
        ("Velocidad de control Q/A", n(resultado.velocidad_control_m_s), "m/s"),
        ("Pendiente del cauce", n(proyecto.pendiente_m_m), "m/m"),
        ("Diámetro medio Dm", n(proyecto.diametro_medio_mm), "mm"),
        ("Divisiones base N", str(proyecto.numero_franjas), ""),
        ("Franjas finales", str(resultado.numero_franjas), ""),
    )
    agregar("tabla", (("Parámetro", "Valor", "Unidad"), datos, (8.5, 4.5, 4)))
    terreno = [(n(p.abscisa_m), n(p.cota_m)) for p in proyecto.puntos_terreno]
    agregar("tabla", (("Abscisa x (m)", "Cota terreno (m)"), terreno, (8.5, 8.5)))
    agregar("parrafo", "El terreno se interpola linealmente. Los puntos secos se conservan "
            "en el gráfico y se excluyen de LL. Cada franja usa área trapezoidal exacta y "
            "h_j = Área_j / ancho_j. Dm se evalúa en mm conforme al desarrollo HHD p. 108.")


def _reparto(agregar, resultado):
    proyecto = resultado.proyecto
    paso(agregar, "3. Reparto por franjas y alpha",
         ("h_j = Área_j / ancho_j", "SUMA = Σ(h_j^(5/3) · ancho_j)", "alpha = Q / SUMA",
          "q_j = alpha · h_j^(5/3)", "Q_j = q_j · ancho_j", "h_m = (SUMA / B)^(3/5)"),
         ("h_j: tirante de la franja, en m", "ancho_j: ancho de la franja, en m",
          "SUMA: suma de reparto, en m^(8/3)", "Q: caudal de diseño, en m³/s",
          "alpha: coeficiente de gasto, en m^(1/3)/s",
          "q_j: caudal unitario, en m²/s", "Q_j: caudal de la franja, en m³/s",
          "hm: tirante medio potencial, en m", "B: ancho mojado, en m", "K: factor de forma, igual a 1"),
         (f"SUMA = {n(resultado.suma_reparto)}",
          f"alpha = {n(proyecto.caudal_m3s)} / {n(resultado.suma_reparto)} = {n(resultado.alpha)} m^(1/3)/s",
          f"hm = ({n(resultado.suma_reparto)} / {n(resultado.ancho_mojado_m)})^(3/5) = {n(resultado.tirante_m)} m"),
         f"alpha = {resultado.alpha:.6f} m^(1/3)/s; hm = {resultado.tirante_m:.6f} m.",
         "La relación por franjas y hm se documenta en DGA/MOP 2022, impresas 68-69/PDF 78-79, "
         "fuente complementaria que no es norma MTC. K=1. Mu no entra en alpha.",
         "DGA/MOP 2022, impresas 68-69/PDF 78-79. No es norma MTC.")


def _coeficientes(agregar, resultado):
    proyecto = resultado.proyecto
    agregar("subtitulo", "4. Coeficientes beta, mu, phi y z")
    filas = (
        ("beta", n(resultado.beta), resultado.detalle_beta
         or "DGA/MOP 2022, tabla 7-1, impresa 69/PDF 79."),
        ("mu", n(resultado.mu), resultado.detalle_mu or "Sin detalle de selección."),
        ("phi", n(resultado.phi), "Agua clara; HHD 2011, pp. 107-108. phi = 1."),
        ("z", n(resultado.z), resultado.detalle_z
         or "DGA/MOP 2022, tabla 7-2, impresa 69/PDF 79."),
    )
    agregar("tabla", (("Coeficiente", "Valor", "Selección y fuente"), filas, (2.5, 3.2, 11.3)))
    if resultado.detalle_mu:
        agregar("parrafo", resultado.detalle_mu)
    agregar("parrafo", "Mu se aplica una sola vez y no entra en alpha. Solo mu puede "
            "interpolarse respecto a L por criterio aprobado. Beta y z usan la celda "
            "publicada; entre los extremos, un valor sin celda usa la fórmula logarítmica "
            "aprobada por el usuario. V no se interpola. Esa fórmula no es norma MTC.")


def _franja(agregar, resultado):
    proyecto = resultado.proyecto
    franja = max(resultado.puntos, key=lambda punto: punto.profundidad_hs_m)
    paso(agregar, "5. Profundidad Hs de la franja de mayor Hs",
         ("H_sj = (q_j / (0.68 · beta · mu · phi · D_m^0.28))^(1/(1+z))",
          "S_gj = H_sj − h_j", "Z_LLj = Z_w − H_sj"),
         ("q_j: caudal unitario de la franja, en m²/s",
          "0.68 y 0.28: coeficiente y exponente empíricos de la ecuación 59",
          "phi: 1 en agua clara; el producto coincide con el denominador evaluado",
          "Hs_j: profundidad desde el agua, en m", "Sg_j: descenso algebraico, en m",
          "Z_LL,j: cota del lecho según Hs, en m"),
         (f"Franja gobernante, centro x = {n(franja.abscisa_m)} m",
          f"h_j = {n(franja.area_franja_m2)} / {n(franja.ancho_franja_m)} = {n(franja.tirante_m)} m",
          f"q_j = {n(resultado.alpha)} * {n(franja.tirante_m)}^(5/3) = {n(franja.caudal_unitario_m2s)} m²/s",
          f"Q_j = {n(franja.caudal_unitario_m2s)} * {n(franja.ancho_franja_m)} = {n(franja.caudal_franja_m3s)} m³/s",
          f"Denominador = 0.68 * {n(resultado.beta)} * {n(resultado.mu)} * {n(resultado.phi)} * "
          f"{n(proyecto.diametro_medio_mm)}^0.28 = {n(resultado.denominador)}",
          f"Exponente = 1 / (1 + {n(resultado.z)}) = {n(resultado.exponente)}",
          f"Hs_j = ({n(franja.caudal_unitario_m2s)} / {n(resultado.denominador)})^{n(resultado.exponente)} "
          f"= {n(franja.profundidad_hs_m)} m",
          f"Sg_j = {n(franja.profundidad_hs_m)} - {n(franja.tirante_m)} = {n(franja.socavacion_m)} m",
          f"Z_LL,j = {n(proyecto.cota_agua_m)} - {n(franja.profundidad_hs_m)} = {n(franja.cota_ll_m)} m"),
         (f"En x = {franja.abscisa_m:.6f} m, Hs_j = {franja.profundidad_hs_m:.6f} m y "
          f"Sg_j = {franja.socavacion_m:.6f} m."),
         "La misma sustitución se repite en cada franja. La tabla siguiente lista todas "
         "con seis decimales. Sg negativa no es sedimentación.",
         "MTC HHD 2011, ecuación 59, p. 108. El reparto q_j proviene de la fuente complementaria.")


def _controles(agregar, resultado):
    paso(agregar, "6. Cierre de caudal y refinamiento",
         ("cierre = ΣQ_j - Q", "error = |SUMA(N) - SUMA(2N)| / SUMA(2N)"),
         ("cierre: diferencia entre la suma de caudales de franja y el caudal de diseño, en m³/s",
          "error: diferencia relativa al duplicar las divisiones base",
          "N: número de divisiones pedido por el usuario"),
         (f"Cierre de caudal: ΣQ_j - Q = {n(resultado.cierre_caudal_m3s)} m³/s "
          "(tolerancia relativa 1e-12).",
          f"Error relativo N/2N = {n(resultado.error_refinamiento_relativo)}; "
          "tolerancia de diagnóstico 0.001. No es una regla MTC."),
         (f"Cierre de caudal = {resultado.cierre_caudal_m3s:.3g} m³/s; "
          f"error relativo N/2N = {resultado.error_refinamiento_relativo:.6g}."),
         "El control numérico no modifica Hs ni sustituye una regla del HHD.",
         "Tolerancias del programa. No son norma MTC.")


def _perfil(agregar, resultado):
    agregar("subtitulo", "7. Perfil transversal y resultados por franja")
    agregar("grafico", None)
    filas = [tuple(f"{valor:.6f}" for valor in (
        p.abscisa_m, p.ancho_franja_m, p.tirante_m, p.caudal_unitario_m2s,
        p.caudal_franja_m3s, p.profundidad_hs_m, p.socavacion_m, p.cota_ll_m,
    )) for p in resultado.puntos]
    agregar("tabla", (("x centro (m)", "Ancho (m)", "h_j (m)", "q_j (m²/s)",
                       "Caudal Q_j (m³/s)", "Hs_j (m)", "Sg_j (m)", "Z_LL,j (m)"),
                      filas, (1.8, 1.8, 1.8, 2.1, 2.3, 2.2, 2.2, 2.8)))


def _cierres(agregar, resultado):
    agregar("subtitulo", "8. Advertencias, límites y referencias")
    for aviso in resultado.advertencias:
        agregar("parrafo", aviso)
    agregar("parrafo_entero", "Se excluyen suelos cohesivos, estratos, varias ramas mojadas, "
            "rugosidades distribuidas, zonas sin erosión, K distinto de 1, mezclas, "
            "socavación local y diseño de cimentaciones. Sg negativa no es sedimentación.")
    agregar("parrafo", "Fuentes principales: MAN_11 HHD-2011.pdf, ecuación 59 p. 108 "
            "y tabla 13 p. 107; Manual de Puentes MTC 2018, §1.2.3a, impresa 47/PDF 51.")
    agregar("parrafo", "Fuente complementaria para el reparto: DGA/MOP Chile 2022, "
            "SIT 527, impresas 68-69/PDF 78-79. No es norma peruana MTC.")
    for fuente in resultado.fuentes:
        agregar("parrafo", fuente)
