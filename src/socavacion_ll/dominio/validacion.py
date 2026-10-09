"""Separar borradores serializables de proyectos aptos para calcular."""
from dataclasses import fields
import math
from typing import cast

from .modelos import Proyecto, PuntoTerreno


def _es_numero_finito(valor: object) -> bool:
    if type(valor) not in (int, float):
        return False
    try:
        return math.isfinite(cast(int | float, valor))
    except OverflowError:
        return False


def _es_texto_xml_seguro(texto: str) -> bool:
    return all(
        caracter in "\t\n\r" or 0x20 <= ord(caracter) <= 0xD7FF
        or 0xE000 <= ord(caracter) <= 0xFFFD
        or 0x10000 <= ord(caracter) <= 0x10FFFF
        for caracter in texto
    )


def _validar_puntos(puntos: object) -> None:
    if type(puntos) is not tuple or len(puntos) > 200:
        raise ValueError("Los puntos del terreno deben ser una tupla de hasta 200 puntos.")
    anterior = None
    for punto in puntos:
        if type(punto) is not PuntoTerreno:
            raise ValueError("Cada punto del terreno debe contener abscisa y cota.")
        for coordenada in (punto.abscisa_m, punto.cota_m):
            if not _es_numero_finito(coordenada):
                raise ValueError("Las abscisas y cotas del terreno deben ser números finitos.")
        if anterior is not None and punto.abscisa_m < anterior.abscisa_m:
            raise ValueError("Las abscisas del terreno no pueden ser decrecientes.")
        if punto == anterior:
            raise ValueError("El terreno no admite puntos idénticos consecutivos.")
        anterior = punto


def validar_estructura(proyecto: Proyecto) -> None:
    """Validar tipos seguros, permitiendo un borrador físicamente incompleto."""
    if type(proyecto) is not Proyecto:
        raise ValueError("Se requiere un objeto Proyecto válido.")
    for campo in fields(Proyecto):
        valor = getattr(proyecto, campo.name)
        nombre = campo.name.replace("_", " ")
        if campo.name == "puntos_terreno":
            _validar_puntos(valor)
        elif campo.type is str:
            limite = 20000 if campo.name == "notas" else 500
            if not isinstance(valor, str) or len(valor) > limite or not _es_texto_xml_seguro(valor):
                raise ValueError(f"{nombre}: texto no válido o mayor de {limite} caracteres.")
        elif campo.type is bool:
            if type(valor) is not bool:
                raise ValueError(f"{nombre}: se requiere verdadero o falso.")
        elif campo.type is int:
            limite = 200 if campo.name == "numero_franjas" else 201
            if type(valor) is not int or not 2 <= valor <= limite:
                raise ValueError(f"{nombre}: debe ser entero entre 2 y {limite}.")
        elif campo.type is float:
            if not _es_numero_finito(valor):
                raise ValueError(f"{nombre}: se requiere un número finito, no texto ni booleano.")
    if proyecto.tipo_seccion not in {"rectangular", "irregular"}:
        raise ValueError("El tipo de sección debe ser rectangular o irregular.")


def validar_proyecto(proyecto: Proyecto) -> None:
    """Validar el alcance físico LL antes de tablas y operaciones."""
    validar_estructura(proyecto)
    if not proyecto.nombre.strip():
        raise ValueError("Indique el nombre del proyecto.")
    if not proyecto.no_cohesivo:
        raise ValueError("Confirme que el suelo es no cohesivo; LL cohesivo no está implementado.")
    if not proyecto.agua_clara:
        raise ValueError("Esta versión solo admite agua clara (phi=1).")
    comunes = ("caudal_m3s", "velocidad_m_s", "diametro_medio_mm", "periodo_retorno_anios")
    for nombre in comunes:
        if getattr(proyecto, nombre) <= 0:
            raise ValueError(f"{nombre.replace('_', ' ')} debe ser mayor que cero.")
    if proyecto.pendiente_m_m < 0:
        raise ValueError("La pendiente del cauce debe ser no negativa.")
    if proyecto.luz_libre_m < 0:
        raise ValueError("La luz libre no puede ser negativa.")
    if not proyecto.sin_obstaculos and proyecto.luz_libre_m <= 0:
        raise ValueError("Indique una luz libre positiva para seleccionar mu.")
    if proyecto.tipo_seccion == "rectangular":
        if proyecto.ancho_m <= 0:
            raise ValueError("ancho m debe ser mayor que cero.")
        tirante = proyecto.cota_agua_m - proyecto.cota_fondo_m
        if not math.isfinite(tirante) or tirante <= 0:
            raise ValueError("La cota de agua debe superar el fondo con un tirante positivo.")
    elif len(proyecto.puntos_terreno) < 2:
        raise ValueError("La sección irregular requiere al menos dos puntos de terreno.")
