---
type: verification
title: Verificación — interpolación de luz libre — 2026-10-09
timestamp: 2026-10-09
topic: sdd
slug: interpolacion-luz-libre
source_state: sin-Git; manifiesto-src-SHA256 4ecf741180a5e3d3b081ef82916aa6200928a6b8fe39d7746039879e3bfd9940
---
# Verificación — interpolación de luz libre

## Stack gate

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/verificar.ps1`
terminó con código0 después de la última edición productiva:

- 91 pruebas unittest aprobadas.
- Cobertura combinada99%; ramas núcleo/dominio72/74=97.2973% (mínimo90%).
- Ruff sin errores; mypy estricto sin errores en siete módulos.
- pip check sin dependencias rotas; pip-audit sin vulnerabilidades conocidas reportadas.
- Módulo productivo mayor: ingreso.py,196 líneas, menor que250.

El intento previo sin red falló cerrado en auditoría. La ejecución final tuvo acceso y
`tmp/calidad/resultado.json` registra nueve pasos con código0 y `completo=true`.

## Tasks y criterios de aceptación

| Evidencia | Resultado |
| --- | --- |
| AC1 / T001 | V=2,L=27 -> mu=0.974; prueba roja previa registró luz bloqueada |
| AC2 | Regresión recorre las104 celdas de tabla13 y conserva igualdad exacta |
| AC3 | L=10/200 aceptadas;9.999/200.001/no finitos rechazados |
| AC4 | V=4,3.75,2.1 siguen bloqueadas; filas válidas conservadas |
| AC5 | Pruebas beta/z intermedias continúan rechazándolos |
| AC6 / T003 | contenido, Word y PDF incluyen L1,mu1,L2,mu2, fórmula y aviso no MTC |
| AC7 | JSON v1 intacto; ejemplos literales anteriores y suite completa verdes |

## Ejecutable y revisión visual

EXE final: `dist/Socavacion_LL_0.3.0/Socavacion_LL_0.3.0.exe`.
SHA256: `c90e93baf2168f4bb5633207ff1880e388952d4591549e46d62aff0b7efa5b91`.

Copiado a `tmp/portable v030 final` y ejecutado desde allí con autocomprobación:

- código de salida0;
- mu interpolado=0.974;
- Hs interpolado=4.8264852831637715m;
- proyecto reabierto íntegro;
- JSON, dos proyectos, DOCX, PDF y captura presentes.

La primera captura reprodujo dos lienzos superpuestos tras calcular dos veces. Causa
confirmada: el widget anterior seguía emparentado durante `deleteLater`. Prueba roja/verde,
ocultamiento y desvinculación antes del borrado. Captura final sin superposición.

PDF final:4 páginas A4, renderizadas con Poppler e inspeccionadas completas. Fórmula,
tabla, gráfico, resultados y referencias legibles, sin recortes ni solapamientos.

## Integridad y límites

PDF MTC originales conservan sus SHA256:

- HHD: `0a1bdcd7c94016760642de91baf4d6e317e4cc85c529dfefae9a6bf76c8dcd88`.
- Puentes: `46d37849141b3acef44bdae112496dafbb5d6813dc008d5495c2f2bb760936b1`.

La interpolación lineal solo en L es decisión aprobada por el usuario; no se atribuye
al MTC. Continúan bloqueadas interpolación de V/beta/z, extrapolación de L, mezcla y
sección irregular. No se probó Windows limpio ni se certifica uso en obra.

## Verdict

PASS para la spec `interpolacion-luz-libre`. No cambia el estado pendiente de la ruta
global ni autoriza las ampliaciones científicas restantes.

```json result-envelope
{"status":"complete","executive_summary":"Interpolación de mu respecto a L verificada en núcleo, UI, reportes y EXE.","artifact":"02-DOCS/wiki/sdd/verifications/interpolacion-luz-libre-2026-10-09.md","next_recommended":"review","risk":"medium","skill_resolution":{"used":["sdd","implement","debug","verify","pdf"],"missing":[],"fallback":["Registro local ausente; skills locales"]},"evidence":["Gate9 pasos","91 pruebas","EXE salida0","PDF renderizado"]}
```
