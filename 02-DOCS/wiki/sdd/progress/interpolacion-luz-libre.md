---
type: progress
slug: interpolacion-luz-libre
status: complete
---
# Progreso — interpolación de luz libre

## T001 — 2026-10-09

- status: complete
- red: L=27m produjo `AssertionError: 'luz bloqueada' != 0.974`.
- green: selección devuelve0.974; pruebas de límites y104 celdas publicadas pasan.
- decision: interpolación lineal solo L; filas V permanecen literales.
- blocker: none.

## T002 — 2026-10-09

- status: complete
- red: Resultado no tenía selección interpolada ni detalle trazable.
- green: selector inmutable entrega valor/detalle; motor lo transporta sin cambiar JSON.
- files: calculo/coeficientes.py, calculo/motor.py, dominio/modelos.py.
- blocker: none.

## T003 — 2026-10-09

- status: complete
- red: ayuda seguía exigiendo celdas exactas y reportes omitían L1/mu1/L2/mu2.
- green: interfaz y Word/PDF muestran regla, extremos, sustitución y advertencia.
- files: presentacion/*, infraestructura/reportes/contenido.py.
- blocker: none.

## Debug visual durante T004 — 2026-10-09

- repro: el EXE calculó dos veces antes de mostrarse; captura con dos lienzos superpuestos.
- red: el lienzo anterior conservaba padre después de `mostrar_resultado` consecutivo.
- causa: borrado Qt diferido sin ocultar/desvincular primero.
- green: prueba focalizada y autocomprobación pasan tras `hide` + `setParent(None)`.
- estado: paquete final y gate completo por repetir después de la corrección.

## Skill resolution

- used: sdd, specify, plan, implement, debug, verify, pdf.
- missing: registro `.rsc/skill-registry.json`; fallback: skills locales leídas directamente.
- compact rules: prueba roja antes de código; no atribuir interpolación al MTC;
  una sola evaluación; verificar salida real y PDF renderizado.

## T004 — 2026-10-09

- status: complete
- build: `dist/Socavacion_LL_0.3.0/Socavacion_LL_0.3.0.exe`.
- EXE: salida0 desde ruta con espacios; mu=0.974 y Hs=4.8264852831637715m.
- visual: captura sin superposición; PDF final de4 páginas renderizado y legible.
- gate:91 pruebas;72/74 ramas; Ruff/mypy/pip check/pip-audit verdes.
- evidence: ver `../verifications/interpolacion-luz-libre-2026-10-09.md`.
