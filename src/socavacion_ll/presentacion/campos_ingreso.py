"""Definición declarativa de campos del formulario de ingreso."""

GRUPOS = (
    ("PROYECTO", (("nombre", "Nombre"), ("ubicacion", "Ubicación"),
                  ("responsable", "Responsable"), ("notas", "Notas y origen de datos"))),
    ("HIDRÁULICA", (("caudal_m3s", "Caudal Q (m³/s)"),
                    ("periodo_retorno_anios", "Período T (años)"),
                    ("velocidad_m_s", "Velocidad V (m/s)"),
                    ("pendiente_m_m", "Pendiente (m/m)"))),
    ("SECCIÓN Y NIVEL", (("ancho_m", "Ancho efectivo B (m)"),
                         ("cota_fondo_m", "Cota del fondo (m)"),
                         ("cota_agua_m", "Cota del agua (m)"),
                         ("numero_puntos", "Puntos rectangulares"))),
    ("SUELO Y OBSTÁCULOS", (("diametro_medio_mm", "Diámetro medio Dm (mm)"),
                            ("luz_libre_m", "Luz libre L (m)"))),
)
TEXTOS = {"nombre", "ubicacion", "responsable", "notas"}


def texto_numero(nombre, valor):
    """Mostrar 2 decimales; la pendiente conserva hasta 8."""
    if nombre == "pendiente_m_m":
        texto = f"{valor:.8f}".rstrip("0").rstrip(".")
        return "0" if texto in ("", "-0") else texto
    if nombre == "diametro_medio_mm":
        return f"{valor:.3f}"
    return f"{valor:.2f}"
AYUDAS = {
    "periodo_retorno_anios": (
        "Celdas: 2, 5, 10, 20, 50, 100, 500 y 1000 años. "
        "Entre ellas se usa la fórmula logarítmica. Fuera de ese tramo no se extrapola."
    ),
    "diametro_medio_mm": (
        "Dm en mm, no D50. Celda publicada o fórmula entre 0.05 y 750 mm."
    ),
    "cota_agua_m": "Cota del estudio hidráulico, en el mismo datum que el terreno.",
    "velocidad_m_s": "Fila literal de mu. No se interpola V.",
}
