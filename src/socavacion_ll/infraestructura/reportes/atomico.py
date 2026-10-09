"""Publicación local: solo reemplazar destino después de finalizar la memoria."""
import os
from pathlib import Path
from tempfile import NamedTemporaryFile


def guardar_atomico(ruta, escribir):
    destino = Path(ruta)
    temporal = None
    try:
        with NamedTemporaryFile(dir=destino.parent, suffix=destino.suffix,
                                prefix=".socavacion_", delete=False) as archivo:
            temporal = Path(archivo.name)
        escribir(temporal)
        os.replace(temporal, destino)
    finally:
        if temporal is not None:
            temporal.unlink(missing_ok=True)
