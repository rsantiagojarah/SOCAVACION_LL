---
type: verification
title: Verificación — sección irregular — 2026-10-09
description: Evidencia del gate, criterios de aceptación, memorias y arranque local de v0.4.0.
tags: [sdd, verification, lischtvan-levediev, seccion-irregular]
timestamp: 2026-10-09T16:59:59-05:00
topic: sdd
slug: seccion-irregular
source_state: sin-git (workspace local no versionado)
---

# Verificación — sección irregular — 2026-10-09

## Stack gate

- `scripts/verificar.ps1` → **PASS**: 109 pruebas; cobertura total 95%; ramas de
  núcleo/dominio 141/154 = 91.5584% (piso 90%).
- Ruff → **PASS**; mypy estricto → **PASS** en 9 módulos; `pip check` → **PASS**.
- `pip-audit --local` → **PASS**: ninguna vulnerabilidad conocida.
- El gate propio demostró salida positiva, herramienta ausente y propagación de un
  código 7 mediante `PruebasCalidad`; su límite es que no sustituye los controles
  científicos independientes.

## Done-checks

- [x] T001 modelo/JSON v2 y lectura v1 — pruebas de proyecto y persistencia verdes.
- [x] T002 geometría — áreas trapezoidales, ramas y entradas inválidas verificadas.
- [x] T003 reparto LL — ejemplo manual y regresión rectangular verdes.
- [x] T004 editor/interfaz — invalidación y carga verificadas.
- [x] T005 resultados/reportes — pruebas verdes; PDF de 5 páginas y Word de 4
  páginas renderizados e inspeccionados sin recortes, solapes ni ecuación alpha espuria.
- [x] T006 cierre v0.4.0 — gate completo y autocomprobación del lanzador Python con
  código 0; módulo mayor: `presentacion/ingreso.py`, 248 líneas. No hay portable 0.4.0.

## Criterios de aceptación

- [x] AC1 — ejemplo manual de dos franjas coincide dentro de 1e-9.
- [x] AC2 — geometría exacta y cierre relativo 1e-12 verificados.
- [x] AC3 — dos ramas, ausencia de agua y abscisas inválidas se bloquean en español.
- [x] AC4 — ida/vuelta v2 y migración v1 verificadas.
- [x] AC5 — pantalla, gráfico, Word y PDF contienen reparto, control y fuentes.
- [x] AC6 — editar tipo o puntos invalida resultado y reportes.
- [x] AC7 — regresión rectangular incluida en las 109 pruebas.
- [x] AC8 — controles configurados pasan; autocomprobación desde el proyecto verificó
  rectangular, mu interpolado e irregular (A=22.5 m², B=15 m, 8 franjas, cierre=0).

## Integridad y capas

- PDF HHD SHA-256: `0A1BDCD7C94016760642DE91BAF4D6E317E4CC85C529DFEFAE9A6BF76C8DCD88`.
- PDF Puentes SHA-256: `46D37849141B3ACEF44BDAE112496DAFBB5D6813DC008D5495C2F2BB760936B1`.
- **NO-APLICA** — portable v0.4.0: rechazado expresamente por el usuario y eliminado.
- **NO-APLICA** — Git/commit: el workspace no está versionado con Git.
- **Capas no ejecutadas:** ninguna de las configuradas; todos los nueve pasos terminaron 0.

## Veredicto

**PASS.** La versión 0.4.0 queda verificada para ejecución desde el proyecto. Esta
evidencia no certifica el modelo hidráulico de una obra ni amplía el alcance científico.

