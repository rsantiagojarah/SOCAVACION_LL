"""Verificación local reproducible; cualquier comprobación incompleta falla."""
import json
import os
from pathlib import Path
import subprocess
import sys


def comprobar_cobertura(ruta: Path, archivos_esperados: set[str]) -> float:
    """Exigir evidencia de todos los módulos y >=90% de ramas, sin redondear."""
    informe = json.loads(ruta.read_text(encoding="utf-8"))
    if informe.get("meta", {}).get("branch_coverage") is not True:
        raise ValueError("Falta medición de ramas; verificar con coverage branch=true.")
    archivos = {nombre.replace("\\", "/"): datos for nombre, datos in informe["files"].items()}
    if set(archivos) != archivos_esperados:
        raise ValueError("La cobertura no corresponde a todos los módulos del núcleo/dominio.")
    cubiertas = total = 0
    for datos in archivos.values():
        resumen = datos["summary"]
        cantidad, ejecutadas = resumen["num_branches"], resumen["covered_branches"]
        if (type(cantidad) is not int or type(ejecutadas) is not int
                or not 0 <= ejecutadas <= cantidad):
            raise ValueError("Contadores de ramas inválidos.")
        cubiertas += ejecutadas
        total += cantidad
    if not total:
        raise ValueError("Sin evidencia de ramas del núcleo/dominio.")
    porcentaje = 100 * cubiertas / total
    if porcentaje < 90:
        raise ValueError(f"Cobertura de ramas insuficiente: {cubiertas}/{total} = {porcentaje:.4f}%.")
    print(f"Ramas núcleo/dominio: {cubiertas}/{total} = {porcentaje:.4f}% (mínimo 90%).")
    return porcentaje


def ejecutar_comprobaciones(comandos: list[tuple[str, list[str]]], raiz: Path) -> int:
    """Conservar salidas y propagar el primer fallo sin continuar con evidencia parcial."""
    destino = raiz / "tmp/calidad"
    destino.mkdir(parents=True, exist_ok=True)
    entorno = dict(os.environ, QT_QPA_PLATFORM="offscreen", PYTHONUTF8="1")
    resultados = []
    for indice, (nombre, comando) in enumerate(comandos, start=1):
        print(f"[{indice}/{len(comandos)}] {nombre}", flush=True)
        try:
            proceso = subprocess.run(comando, cwd=raiz, env=entorno, capture_output=True,
                                     text=True, encoding="utf-8", errors="replace", check=False)
            codigo, salida = proceso.returncode, proceso.stdout + proceso.stderr
        except OSError as error:
            codigo, salida = 1, f"No se pudo ejecutar {nombre}: {error}\n"
        (destino / f"{indice:02d}-{nombre}.log").write_text(salida, encoding="utf-8")
        print(salida, end="", flush=True)
        resultados.append({"paso": nombre, "codigo": codigo, "comando": comando})
        (destino / "resultado.json").write_text(json.dumps(
            {"completo": codigo == 0 and indice == len(comandos), "pasos": resultados},
            ensure_ascii=False, indent=2), encoding="utf-8")
        if codigo:
            print(f"Verificación incompleta o fallida: {nombre} (código {codigo}).", flush=True)
            return codigo
    return 0


def principal() -> int:
    raiz = Path(__file__).resolve().parents[1]
    if sys.argv[1:] == ["--cobertura"]:
        esperados = {ruta.relative_to(raiz).as_posix() for carpeta in ("calculo", "dominio")
                     for ruta in (raiz / "src/socavacion_ll" / carpeta).rglob("*.py")}
        try:
            comprobar_cobertura(raiz / "tmp/calidad/cobertura.json", esperados)
        except (OSError, ValueError, KeyError, TypeError) as error:
            print(f"Cobertura incompleta o insuficiente: {error}")
            return 1
        return 0
    if sys.argv[1:]:
        print("Uso: calidad.py [--cobertura]")
        return 2
    python = sys.executable
    comandos = [
        ("borrar_medicion", [python, "-m", "coverage", "erase"]),
        ("pruebas", [python, "-m", "coverage", "run", "-m", "unittest", "discover", "-s", "pruebas", "-v"]),
        ("cobertura_informe", [python, "-m", "coverage", "report"]),
        ("cobertura_json", [python, "-m", "coverage", "json"]),
        ("cobertura_ramas", [python, str(Path(__file__).resolve()), "--cobertura"]),
        ("analisis", [python, "-m", "ruff", "check", "src"]),
        ("tipos", [python, "-m", "mypy"]),
        ("dependencias", [python, "-m", "pip", "check"]),
        ("auditoria", [python, "-m", "pip_audit", "--local", "--format=json",
                       "--output", "tmp/calidad/auditoria.json", "--timeout", "30",
                       "--cache-dir", "tmp/calidad/cache-auditoria"]),
    ]
    return ejecutar_comprobaciones(comandos, raiz)


if __name__ == "__main__":
    raise SystemExit(principal())
