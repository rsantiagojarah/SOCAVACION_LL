"""Contenido único de las memorias; consume resultados, nunca ejecuta el núcleo."""
from dataclasses import dataclass
from io import BytesIO

from socavacion_ll.dominio.modelos import Resultado
from socavacion_ll.infraestructura.graficos import crear_figura

from .desarrollo import identificacion, indice, n, paso, portada


@dataclass(frozen=True)
class Bloque:
    tipo: str
    contenido: object


def numero(valor: float) -> str:
    return n(valor)


def grafico_png(resultado: Resultado) -> BytesIO:
    memoria = BytesIO()
    figura = crear_figura(resultado)
    figura.savefig(memoria, format="png", dpi=180)
    figura.clear()
    memoria.seek(0)
    return memoria


def preparar_contenido(resultado: Resultado) -> tuple[Bloque, ...]:
    if resultado.tipo_seccion == "irregular":
        from .contenido_irregular import preparar_contenido_irregular
        return preparar_contenido_irregular(resultado)
    proyecto = resultado.proyecto
    primero = resultado.puntos[0]
    bloques = []

    def agregar(tipo, contenido):
        bloques.append(Bloque(tipo, contenido))

    portada(agregar, resultado, "Rectangular, lecho homogéneo, una evaluación",
            "Datos · coeficientes · ecuación 59 · sustitución · perfil · referencias")
    indice(agregar, (
        ("1", "Identificación del proyecto"),
        ("2", "Datos hidráulicos, tirante y geometría"),
        ("3", "Coeficiente alpha de Schreider"),
        ("4", "Coeficientes beta, mu, phi y z"),
        ("5", "Profundidad Hs, ecuación 59"),
        ("6", "Socavación Sg y cotas del lecho"),
        ("7", "Perfil transversal y resultados"),
        ("8", "Advertencias y límites de aplicación"),
        ("9", "Referencias técnicas"),
    ))
    identificacion(agregar, proyecto)
    _datos(agregar, resultado)
    _alpha(agregar, resultado)
    _coeficientes(agregar, resultado)
    _profundidad(agregar, resultado, primero)
    _socavacion(agregar, resultado, primero)
    _perfil(agregar, resultado)
    _cierres(agregar, resultado)
    return tuple(bloques)


def _datos(agregar, resultado):
    proyecto = resultado.proyecto
    agregar("subtitulo", "2. Datos de entrada y geometría")
    datos = (
        ("Caudal Qd", n(proyecto.caudal_m3s), "m³/s"),
        ("Período de retorno T", n(proyecto.periodo_retorno_anios), "años"),
        ("Ancho efectivo B", n(proyecto.ancho_m), "m"),
        ("Cota del fondo Zfondo", n(proyecto.cota_fondo_m), "m"),
        ("Cota del agua Zw", n(proyecto.cota_agua_m), "m"),
        ("Velocidad ingresada V", n(proyecto.velocidad_m_s), "m/s"),
        ("Pendiente del cauce", n(proyecto.pendiente_m_m), "m/m"),
        ("Diámetro medio Dm", n(proyecto.diametro_medio_mm), "mm"),
        ("Suelo no cohesivo", "Sí" if proyecto.no_cohesivo else "No", ""),
        ("Agua clara", "Sí" if proyecto.agua_clara else "No", ""),
        ("Sin obstáculos", "Sí" if proyecto.sin_obstaculos else "No", ""),
        ("Luz libre L", n(proyecto.luz_libre_m), "m"),
        ("Puntos de evaluación", str(proyecto.numero_puntos), ""),
    )
    agregar("tabla", (("Parámetro", "Valor", "Unidad"), datos, (8.5, 4.5, 4)))
    paso(agregar, "2.1 Tirante, área y velocidad de control",
         ("h = Z_w − Z_fondo", "A = B · h", "V_control = Q_d / A"),
         ("h: tirante inicial, en m", "Zw: cota del agua, en m",
          "Zfondo: cota del fondo, en m", "A: área mojada, en m²",
          "B: ancho de la sección rectangular, en m",
          "Qd: caudal de diseño, en m³/s", "Vcontrol: caudal dividido por el área, en m/s"),
         (f"h = {n(proyecto.cota_agua_m)} - {n(proyecto.cota_fondo_m)} = {n(resultado.tirante_m)} m",
          f"A = {n(proyecto.ancho_m)} * {n(resultado.tirante_m)} = {n(resultado.area_m2)} m²",
          f"Vcontrol = {n(proyecto.caudal_m3s)} / {n(resultado.area_m2)} = {n(resultado.velocidad_control_m_s)} m/s"),
         (f"h = {resultado.tirante_m:.6f} m; A = {resultado.area_m2:.6f} m²; "
          f"Vcontrol = {resultado.velocidad_control_m_s:.6f} m/s."),
         "La pendiente se registra como antecedente; no resuelve el nivel de agua. "
         "Dm es el diámetro medio, no D50, y entra en mm.",
         "Nivel de agua conocido, impuesto por el usuario. HHD 2011, desarrollo p. 108.")


def _alpha(agregar, resultado):
    proyecto = resultado.proyecto
    paso(agregar, "3. Coeficiente alpha",
         ("alpha = Q_d / (B · h^(5/3))",),
         ("alpha: coeficiente de gasto, en m^(1/3)/s",
          "Qd: caudal de diseño, en m³/s", "B: ancho efectivo, en m",
          "h: tirante inicial, en m",
          "La corrección mu no entra en alpha; se aplica una sola vez en Hs"),
         (f"alpha = {n(proyecto.caudal_m3s)} / ({n(proyecto.ancho_m)} * "
          f"{n(resultado.tirante_m)}^(5/3)) = {n(resultado.alpha)} m^(1/3)/s",),
         f"alpha = {resultado.alpha:.6f} m^(1/3)/s.",
         "Alpha no incluye mu. La contracción, cuando corresponde, corrige solo Hs.",
         "Schreider et al. 2001, ecuación 1, p. 16. No es una ecuación del HHD.")


def _coeficientes(agregar, resultado):
    proyecto = resultado.proyecto
    agregar("subtitulo", "4. Coeficientes beta, mu, phi y z")
    filas = (
        ("beta", n(resultado.beta), resultado.detalle_beta or (
            f"T = {n(proyecto.periodo_retorno_anios)} años. "
            "DGA/MOP 2022, tabla 7-1, p. 69 / PDF 79.")),
        ("mu", n(resultado.mu), resultado.detalle_mu or "Sin detalle de selección."),
        ("phi", n(resultado.phi), "Agua clara. HHD pp. 107-108. phi = 1."),
        ("z", n(resultado.z), resultado.detalle_z or (
            f"Dm = {n(proyecto.diametro_medio_mm)} mm. "
            "DGA/MOP 2022, tabla 7-2, p. 69 / PDF 79; allí se denomina X.")),
    )
    agregar("tabla", (("Coeficiente", "Valor", "Selección y fuente"), filas, (2.5, 3.2, 11.3)))
    if resultado.detalle_mu:
        agregar("parrafo", resultado.detalle_mu)
    agregar("parrafo", (
        "Beta, mu, phi y z son adimensionales. Una celda publicada de beta o z se usa "
        "tal cual. Si T o Dm caen entre los extremos de su tabla y no coinciden con una "
        "celda, se aplica la fórmula logarítmica aprobada por el usuario; no es norma MTC "
        "ni DGA y no se extrapola. Mu interpola linealmente solo L dentro de 10–200 m; "
        "no interpola V."))
    agregar("referencia", "DGA/MOP 2022, tablas 7-1 y 7-2, p. 69 / PDF 79, fuente complementaria. "
            "Mu: MTC HHD 2011, tabla 13, p. 107. Phi: HHD pp. 107-108.")


def _profundidad(agregar, resultado, primero):
    proyecto = resultado.proyecto
    paso(agregar, "5. Profundidad de socavación Hs",
         ("H_s = (alpha · h^(5/3) / (0.68 · beta · mu · phi · D_m^0.28))^(1/(1+z))",),
         ("Hs: profundidad desde la superficie del agua hasta el lecho socavado, en m",
          "0.68: coeficiente empírico de la ecuación 59",
          "0.28: exponente empírico de Dm",
          "beta, mu, phi, z: coeficientes adimensionales ya seleccionados",
          "Dm: diámetro medio del lecho, en mm"),
         (f"Numerador = {n(resultado.alpha)} * {n(resultado.tirante_m)}^(5/3) = {n(resultado.numerador)}",
          f"Denominador = 0.68 * {n(resultado.beta)} * {n(resultado.mu)} * {n(resultado.phi)} * "
          f"{n(proyecto.diametro_medio_mm)}^0.28 = {n(resultado.denominador)}",
          f"Exponente = 1 / (1 + {n(resultado.z)}) = {n(resultado.exponente)}",
          f"Hs = ({n(resultado.numerador)} / {n(resultado.denominador)})^{n(resultado.exponente)} "
          f"= {n(primero.profundidad_hs_m)} m"),
         f"Hs = {primero.profundidad_hs_m:.6f} m.",
         "El tirante y el material son uniformes: la sustitución vale para todos los puntos. "
         "Los valores intermedios son los del cálculo; no se recalcula la memoria. "
         "phi = 1 en agua clara, así el producto coincide con el denominador evaluado.",
         "MTC HHD 2011, ecuación 59, p. 108. Dm en mm conforme a ese desarrollo; el resumen p. 158 discrepa.")


def _socavacion(agregar, resultado, primero):
    proyecto = resultado.proyecto
    paso(agregar, "6. Socavación y cotas del lecho",
         ("S_g = H_s − h", "Z_LL = Z_w − H_s", "Z_perfil = Z_fondo − max(0, S_g)"),
         ("Sg: descenso algebraico del fondo, en m; negativo no es sedimentación",
          "Z_LL: cota del lecho según Hs, en m",
          "Zperfil: convención de presentación que no eleva el fondo, en m"),
         (f"Sg = {n(primero.profundidad_hs_m)} - {n(primero.tirante_m)} = {n(primero.socavacion_m)} m",
          f"Z_LL = {n(proyecto.cota_agua_m)} - {n(primero.profundidad_hs_m)} = {n(primero.cota_ll_m)} m",
          f"Zperfil = {n(proyecto.cota_fondo_m)} - max(0, {n(primero.socavacion_m)}) = {n(primero.cota_perfil_m)} m"),
         (f"Sg = {primero.socavacion_m:.6f} m; Z_LL = {primero.cota_ll_m:.6f} m; "
          f"Zperfil = {primero.cota_perfil_m:.6f} m."),
         "Si Sg < 0, se conserva el resultado algebraico y se identifica sin profundización "
         "predicha; no implica sedimentación. Zperfil es una convención de presentación.",
         "Definiciones de presentación del resultado. Zperfil no es otra ecuación normativa.")


def _perfil(agregar, resultado):
    agregar("subtitulo", "7. Perfil transversal y resultados por punto")
    agregar("grafico", None)
    filas = [tuple(f"{valor:.6f}" for valor in (
        p.abscisa_m, p.cota_fondo_m, p.tirante_m, p.profundidad_hs_m,
        p.socavacion_m, p.cota_ll_m, p.cota_perfil_m)) for p in resultado.puntos]
    agregar("tabla", (("x (m)", "Fondo (m)", "h (m)", "Hs (m)", "Sg (m)",
                       "Z_LL (m)", "Zperfil (m)"), filas, (2.3, 2.5, 2.1, 2.5, 2.4, 2.6, 2.6)))
    agregar("parrafo", "La tabla muestra seis decimales solo para lectura. "
            "La sustitución anterior usa el valor completo del cálculo.")


def _cierres(agregar, resultado):
    agregar("subtitulo", "8. Advertencias y límites de aplicación")
    for texto in resultado.advertencias:
        agregar("parrafo", texto)
    agregar("parrafo", (
        "Se excluyen suelos cohesivos, estratos, secciones irregulares en este capítulo, "
        "mezclas agua-sedimento y flujos de detritos. No incluye socavación local ni "
        "representa la socavación total de un puente."))
    agregar("subtitulo", "9. Referencias técnicas")
    agregar("parrafo", "Fuentes principales peruanas: MAN_11 HHD-2011.pdf, ecuación 59 "
            "p. 108, tabla 13 p. 107; Manual de Puentes MTC 2018 (PGA).pdf, "
            "§1.2.3a p. impresa 47 / PDF 51.")
    agregar("parrafo", "Complementarias: Schreider et al. (2001), ecuación 1, p. 16; "
            "DGA/MOP Chile (2022), SIT 527, tablas 7-1 y 7-2, p. 69 / PDF 79. "
            "No son normativa peruana.")
    for fuente in resultado.fuentes:
        agregar("parrafo", fuente)
