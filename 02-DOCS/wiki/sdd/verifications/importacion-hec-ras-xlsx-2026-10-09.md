---
type: verification
title: Verificación — importación HEC-RAS XLSX — 2026-10-09
description: Evidencia del lector, flujo Qt, archivo real y gate de v0.5.0.
tags: [sdd, verification, hec-ras, xlsx, seccion-irregular]
timestamp: 2026-10-09T17:20:00-05:00
topic: sdd
slug: importacion-hec-ras-xlsx
source_state: sin-git (workspace local no versionado)
---

# Verificación — importación HEC-RAS XLSX — 2026-10-09

## Archivo real

- Hoja detectada: `Hoja1`.
- `Ground`: 55 puntos, sin redondear ni reordenar.
- Extremos conservados: x `-2.1000000349769e-11` y `63.2999992370605`.
- Perfil: `WS PF 1 = 2511.00366210938` m.
- `Bank Sta`: `19.8999996185303` y `60.4000015258789` m.
- Tramo vertical conservado: x `23.3999996185303`, cotas
  `2511.32006835938` y `2511.28002929688`.
- La geometría con 20 divisiones produjo una rama mojada, 34 franjas y área
  `12.585511641055984 m²`. Esta comprobación valida el procesamiento geométrico;
  no valida hidráulicamente el archivo HEC-RAS.
- El lector abrió el libro en modo de solo lectura y no ejecutó operaciones de escritura.

## Done-checks

- [x] T001 — parser por etiquetas, dependencia fijada y errores seguros.
- [x] T002 — diálogo Qt, selección WS, confirmación SI y aplicación atómica.
- [x] T003 — procedencia en Notas y archivo real verificado.
- [x] T004 — regresión y gate completo.

## Stack gate

- `scripts/verificar.ps1` → **PASS** en sus nueve pasos.
- 119 pruebas → **PASS**.
- Cobertura total: 95 %; ramas de núcleo/dominio: `145/158 = 91.7722 %`.
- Ruff → **PASS**; mypy estricto → **PASS**; `pip check` → **PASS**.
- `pip-audit --local` → **PASS**: ninguna vulnerabilidad conocida.
- Módulo de producción mayor: `presentacion/ingreso.py`, 245 líneas.

## Veredicto

**PASS.** La versión 0.5.0 importa el formato XLSX suministrado sin cambiar las
ecuaciones ni coeficientes Lischtvan–Levediev y sin generar una versión portable.
