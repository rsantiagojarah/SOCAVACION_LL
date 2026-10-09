"""Contenido único de las memorias; consume resultados, nunca ejecuta el núcleo."""
from dataclasses import dataclass
from io import BytesIO
from socavacion_ll import __version__

from socavacion_ll.dominio.modelos import Resultado
from socavacion_ll.infraestructura.graficos import crear_figura


@dataclass(frozen=True)
class Bloque:
    tipo: str
    contenido: object


def numero(valor: float) -> str:
    return format(valor, ".12g")


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
    """Estructura común; cada exportador solo decide cómo maquetarla."""
    proyecto = resultado.proyecto
    n = numero
    primero = resultado.puntos[0]
    bloques = []

    def agregar(tipo, contenido):
        bloques.append(Bloque(tipo, contenido))

    agregar("titulo", "Memoria de cálculo de socavación general")
    agregar("parrafo", "Método de Lischtvan-Levediev para suelos no cohesivos. "
            f"Versión {__version__}. Se evalúa una sección rectangular de lecho homogéneo "
            "y agua clara, con nivel de agua conocido. El resultado requiere "
            "revisión del ingeniero responsable; no determina la cimentación del puente.")
    agregar("subtitulo", "Identificación del proyecto")
    for etiqueta, valor in (("Proyecto", proyecto.nombre), ("Ubicación", proyecto.ubicacion),
                            ("Responsable", proyecto.responsable), ("Notas", proyecto.notas)):
        agregar("parrafo", f"{etiqueta}: {valor or 'No consignado'}")
    agregar("subtitulo", "Datos de entrada y geometría")
    datos = [
        ("Caudal Qd", n(proyecto.caudal_m3s), "m³/s"),
        ("Período de retorno T", n(proyecto.periodo_retorno_anios), "años"),
        ("Ancho efectivo B de sección rectangular", n(proyecto.ancho_m), "m"),
        ("Cota del fondo natural", n(proyecto.cota_fondo_m), "m"),
        ("Cota del agua Zw", n(proyecto.cota_agua_m), "m"),
        ("Tirante inicial h", n(resultado.tirante_m), "m"),
        ("Área mojada A", n(resultado.area_m2), "m²"),
        ("Velocidad ingresada V", n(proyecto.velocidad_m_s), "m/s"),
        ("Velocidad de control Qd/A", n(resultado.velocidad_control_m_s), "m/s"),
        ("Pendiente del cauce", n(proyecto.pendiente_m_m), "m/m"),
        ("Diámetro medio Dm", n(proyecto.diametro_medio_mm), "mm"),
        ("Suelo no cohesivo declarado", "Sí" if proyecto.no_cohesivo else "No", ""),
        ("Agua clara declarada", "Sí" if proyecto.agua_clara else "No", ""),
        ("Sin obstáculos", "Sí" if proyecto.sin_obstaculos else "No", ""),
        ("Luz libre L", n(proyecto.luz_libre_m), "m"),
        ("Puntos equidistantes de evaluación", str(proyecto.numero_puntos), ""),
    ]
    agregar("tabla", (("Parámetro", "Valor", "Unidad"), datos, (10, 4, 3)))
    agregar("parrafo", "La pendiente se registra como antecedente; no resuelve el nivel "
            "de agua. Dm es el diámetro medio, no D50. Se usa Dm en mm en la ecuación "
            "empírica, conforme al desarrollo HHD p. 108; el resumen p. 158 discrepa.")
    agregar("subtitulo", "Coeficientes y procedencia")
    coeficientes = [
        ("alpha", n(resultado.alpha), "Qd / (B * h^(5/3)); sección rectangular. "
         "Schreider et al. 2001, ec. 1, p. 16. Unidad m^(1/3)/s."),
        ("beta", n(resultado.beta), f"T = {n(proyecto.periodo_retorno_anios)} años. "
         "DGA/MOP 2022, tabla 7-1, p. 69 / PDF 79."),
        ("mu", n(resultado.mu), resultado.detalle_mu),
        ("phi", n(resultado.phi), "Agua clara. HHD pp. 107-108."),
        ("z", n(resultado.z), f"Dm = {n(proyecto.diametro_medio_mm)} mm. "
         "DGA/MOP 2022, tabla 7-2, p. 69 / PDF 79; allí se denomina X."),
    ]
    agregar("tabla", (("Coeficiente", "Valor", "Selección y fuente"), coeficientes, (2.5, 3, 11.5)))
    agregar("parrafo", "Beta, mu, phi y z son adimensionales. Beta y z requieren celdas "
            "literales. Mu conserva celdas literales e interpola linealmente solo L dentro "
            "de 10–200 m por criterio aprobado por el usuario; no interpola V ni extrapola. "
            "Alpha no incluye mu: la corrección de contracción se aplica una sola vez.")
    agregar("subtitulo", "Ecuaciones y sustitución numérica")
    for ecuacion in (
        "h = Zw - Zfondo; A = B * h; Vcontrol = Qd / A",
        "alpha = Qd / (B * h^(5/3))",
        "Hs = [alpha * h^(5/3) / (0.68 * beta * mu * phi * Dm^0.28)]^(1/(1+z))",
        "Sg = Hs - h; Z_LL = Zw - Hs",
        "Zperfil = Zfondo - max(0, Sg)",
    ):
        agregar("ecuacion", ecuacion)
    agregar("parrafo", "Hs se mide desde la superficie del agua; Sg es el descenso "
            "algebraico respecto al fondo original. Zperfil es una convención de "
            "presentación que impide elevar el fondo; no es otra ecuación normativa.")
    agregar("parrafo", resultado.detalle_mu)
    for texto in (
        f"h = {n(proyecto.cota_agua_m)} - {n(proyecto.cota_fondo_m)} = {n(resultado.tirante_m)} m",
        f"A = {n(proyecto.ancho_m)} * {n(resultado.tirante_m)} = {n(resultado.area_m2)} m²",
        f"Vcontrol = {n(proyecto.caudal_m3s)} / {n(resultado.area_m2)} = {n(resultado.velocidad_control_m_s)} m/s",
        f"alpha = {n(proyecto.caudal_m3s)} / ({n(proyecto.ancho_m)} * {n(resultado.tirante_m)}^(5/3)) = {n(resultado.alpha)} m^(1/3)/s",
        f"Numerador = {n(resultado.alpha)} * {n(resultado.tirante_m)}^(5/3) = {n(resultado.numerador)}",
        f"Denominador = 0.68 * {n(resultado.beta)} * {n(resultado.mu)} * {n(resultado.phi)} * {n(proyecto.diametro_medio_mm)}^0.28 = {n(resultado.denominador)}",
        f"Exponente = 1 / (1 + {n(resultado.z)}) = {n(resultado.exponente)}",
        f"Hs = ({n(resultado.numerador)} / {n(resultado.denominador)})^{n(resultado.exponente)} = {n(primero.profundidad_hs_m)} m",
        f"Sg = {n(primero.profundidad_hs_m)} - {n(primero.tirante_m)} = {n(primero.socavacion_m)} m",
        f"Z_LL = {n(proyecto.cota_agua_m)} - {n(primero.profundidad_hs_m)} = {n(primero.cota_ll_m)} m",
    ):
        agregar("parrafo", texto)
    agregar("parrafo", "La sustitución anterior corresponde a todos los puntos: "
            "el tirante y el material son uniformes en esta sección rectangular. "
            "Los números mostrados se redondean solo para lectura; no se recalcula la memoria.")
    agregar("subtitulo", "Perfil transversal y resultados por punto")
    agregar("grafico", None)
    filas = [tuple(f"{valor:.6f}" for valor in (
        p.abscisa_m, p.cota_fondo_m, p.tirante_m, p.profundidad_hs_m,
        p.socavacion_m, p.cota_ll_m, p.cota_perfil_m)) for p in resultado.puntos]
    agregar("tabla", (("x (m)", "Fondo (m)", "h (m)", "Hs (m)", "Sg (m)",
                       "Z_LL (m)", "Zperfil (m)"), filas, (2.3, 2.5, 2.1, 2.5, 2.4, 2.6, 2.6)))
    agregar("subtitulo", "Advertencias y límites de aplicación")
    for texto in resultado.advertencias:
        agregar("parrafo", texto)
    agregar("parrafo", "Si Sg < 0, se conserva el resultado algebraico y se identifica "
            "sin profundización predicha; no implica sedimentación. El perfil limitado "
            "se distingue del algebraico en el gráfico cuando difieren.")
    agregar("parrafo", "Se excluyen suelos cohesivos, estratos, secciones irregulares, "
            "mezclas agua-sedimento y flujos de detritos. El cálculo LL incluye la "
            "corrección de contracción cuando mu corresponde a obstáculos; no debe "
            "sumarse otra contracción. No incluye socavación local ni representa "
            "socavación total de un puente. El usuario debe justificar el escenario hidrológico.")
    agregar("subtitulo", "Referencias técnicas")
    agregar("parrafo", "Fuentes principales peruanas: MAN_11 HHD-2011.pdf, ecuación 59 "
            "p. 108, tabla 13 p. 107; Manual de Puentes MTC 2018 (PGA).pdf, "
            "§1.2.3a p. impresa 47 / PDF 51. Originales conservados en docs/.")
    agregar("parrafo", "Complementarias: Schreider et al. (2001), Aplicación del método "
            "de Lischtvan y Lebediev al cálculo de la erosión general, Ingeniería "
            "Hidráulica en México XVI(1), pp. 15-26, ec. 1 p. 16; DGA/MOP Chile "
            "(2022), Diseño y Mejoras Estación Fluviométrica Río Cachapoal en Puente "
            "Arqueado, SIT 527, tablas 7-1 y 7-2, p. 69 / PDF 79, atribuidas a "
            "Mery (2013). No son normativa peruana. Ver documentos y registro "
            "bibliográfico en docs/complementarias/.")
    for fuente in resultado.fuentes:
        agregar("parrafo", fuente)
    return tuple(bloques)
