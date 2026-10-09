"""Construcción portable Windows sin borrar distribuciones existentes."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile

RAIZ = Path(__file__).resolve().parents[1]


def preparar_comando(destino):
    destino = Path(destino).resolve()
    if destino.exists():
        raise FileExistsError(f"El destino ya existe; elige otro para conservarlo: {destino}")
    temporales = RAIZ / "tmp" / "empaquetado"
    temporales.mkdir(parents=True, exist_ok=True)
    trabajo = Path(tempfile.mkdtemp(prefix="build-", dir=temporales))
    return [sys.executable, "-m", "PyInstaller", "--onedir", "--windowed", "--noupx",
            "--name", destino.name, "--distpath", str(destino.parent),
            "--workpath", str(trabajo / "trabajo"), "--specpath", str(trabajo),
            "--paths", str(RAIZ / "src"),
            "--add-data", f"{RAIZ / 'docs'}:docs",
            "--add-data", f"{RAIZ / 'LEEME.md'}:.",
            str(RAIZ / "iniciar_interfaz.py")]


def principal():
    argumentos = argparse.ArgumentParser(description=__doc__)
    argumentos.add_argument("--destino", type=Path, default=RAIZ / "dist" / "Socavacion_LL")
    opciones = argumentos.parse_args()
    try:
        comando = preparar_comando(opciones.destino)
        entorno = dict(os.environ)
        entorno["PYINSTALLER_CONFIG_DIR"] = str(RAIZ / "tmp" / "empaquetado" / "cache")
        subprocess.run(comando, cwd=RAIZ, env=entorno, check=True)
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"No se pudo empaquetar: {error}", file=sys.stderr)
        return 1
    print(opciones.destino.resolve() / (opciones.destino.name + ".exe"))
    return 0


if __name__ == "__main__":
    raise SystemExit(principal())
