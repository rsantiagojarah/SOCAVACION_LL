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
