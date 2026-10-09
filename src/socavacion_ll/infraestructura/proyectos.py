"""JSON estricto y versionado; guardado atómico sin resultados derivados."""
from dataclasses import asdict, fields
import json
import os
from pathlib import Path
import tempfile

from socavacion_ll.dominio.modelos import Proyecto, PuntoTerreno
from socavacion_ll.dominio.validacion import validar_estructura

LIMITE_ARCHIVO_BYTES = 1_048_576
FORMATO = "socavacion-ll"
VERSION = 2
CAMPOS_V1 = {
    "nombre", "ubicacion", "responsable", "notas", "caudal_m3s",
    "periodo_retorno_anios", "ancho_m", "cota_fondo_m", "cota_agua_m",
    "velocidad_m_s", "pendiente_m_m", "diametro_medio_mm", "no_cohesivo",
    "agua_clara", "sin_obstaculos", "luz_libre_m", "numero_puntos",
}


def _rechazar_constante(valor):
    raise ValueError(f"El proyecto contiene un número no finito: {valor}.")


def _objeto_sin_duplicados(pares):
    objeto = {}
    for clave, valor in pares:
        if clave in objeto:
            raise ValueError(f"El proyecto repite el campo '{clave}'.")
        objeto[clave] = valor
    return objeto


def guardar_proyecto(ruta, proyecto):
    """Guardar incluso borradores; conservar el original si falla la escritura."""
    validar_estructura(proyecto)
    documento = {"formato": FORMATO, "version": VERSION, "proyecto": asdict(proyecto)}
    contenido = (json.dumps(documento, ensure_ascii=False, allow_nan=False, indent=2) + "\n").encode()
    if len(contenido) > LIMITE_ARCHIVO_BYTES:
        raise ValueError("El proyecto supera el tamaño máximo de 1 MiB.")
    destino = Path(ruta)
    temporal = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", prefix=".socavacion-", suffix=".tmp",
            dir=destino.parent, delete=False,
        ) as archivo:
            temporal = Path(archivo.name)
            archivo.write(contenido)
            archivo.flush()
            os.fsync(archivo.fileno())
        os.replace(temporal, destino)
    finally:
        if temporal is not None:
            temporal.unlink(missing_ok=True)


def _leer_documento(ruta):
    with Path(ruta).open("rb") as archivo:
        contenido = archivo.read(LIMITE_ARCHIVO_BYTES + 1)
    if len(contenido) > LIMITE_ARCHIVO_BYTES:
        raise ValueError("El proyecto supera el tamaño máximo de 1 MiB.")
    try:
        return json.loads(
            contenido.decode("utf-8"), parse_constant=_rechazar_constante,
            object_pairs_hook=_objeto_sin_duplicados,
        )
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise ValueError("El archivo no contiene un proyecto JSON válido.") from error


def _convertir_puntos(datos):
    puntos = datos["puntos_terreno"]
    if type(puntos) is not list:
        raise ValueError("Los puntos del terreno deben estar en una lista JSON.")
    convertidos = []
    for punto in puntos:
        if type(punto) is not dict or set(punto) != {"abscisa_m", "cota_m"}:
            raise ValueError("Cada punto del terreno debe contener abscisa_m y cota_m.")
        convertidos.append(PuntoTerreno(**punto))
    return {**datos, "puntos_terreno": tuple(convertidos)}


def abrir_proyecto(ruta):
    """Aceptar v1/v2 estrictos; nunca cargar ni ejecutar resultados almacenados."""
    documento = _leer_documento(ruta)
    if type(documento) is not dict or set(documento) != {"formato", "version", "proyecto"}:
        raise ValueError("La estructura del archivo de proyecto no es válida.")
    if documento["formato"] != FORMATO:
        raise ValueError("El formato del archivo no corresponde a Socavación LL.")
    version = documento["version"]
    if type(version) is not int or version not in (1, VERSION):
        raise ValueError("La versión del archivo de proyecto no está soportada.")
    datos = documento["proyecto"]
    esperados = CAMPOS_V1 if version == 1 else {campo.name for campo in fields(Proyecto)}
    if type(datos) is not dict or set(datos) != esperados:
        raise ValueError("El proyecto contiene campos faltantes o desconocidos.")
    if version == 1:
        datos = {**datos, "tipo_seccion": "rectangular", "puntos_terreno": (),
                 "numero_franjas": 20}
    else:
        datos = _convertir_puntos(datos)
    proyecto = Proyecto(**datos)
    validar_estructura(proyecto)
    return proyecto
