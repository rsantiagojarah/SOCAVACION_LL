---
type: plan
slug: interpolacion-luz-libre
status: approved
---
# Plan técnico — interpolación de luz libre

## 0. Global constraints

Exclusivamente LL y no cohesivos. MTC sigue siendo fuente de las celdas de mu.
La interpolación lineal es criterio aprobado por el usuario, no regla atribuida al MTC.
No interpolar V/beta/z ni extrapolar L. SI, español, DRY/SOLID/KISS y <=250 líneas/módulo.
Preservar PDF originales, JSON v1 y valores literales de tabla13.

## 1. Context & constraints

Spec AC1–7. La fila de velocidad ya se selecciona literalmente. El Resultado inmutable
alimenta interfaz y reportes; debe transportar la procedencia sin que estos recalculen mu.
No hay repositorio Git: trabajo directo en el directorio autorizado.

## 2. Architecture

```text
Proyecto -> selector puro mu -> Resultado(valor + detalle) -> UI y memorias
                         \-> tabla13 inmutable
```

Decisión principal: mantener un solo selector puro que produzca valor y trazabilidad.
`obtener_mu` conserva su contrato numérico para compatibilidad y delega en ese selector.

## 3. Interfaces & contracts

- `seleccionar_mu(sin_obstaculos,V,L) -> SeleccionMu` inmutable.
- `SeleccionMu.valor` es el único mu usado por el motor.
- `SeleccionMu.detalle` identifica fila, extremos, fórmula y carácter no normativo.
- `Resultado.detalle_mu` lleva esa explicación; proyecto/JSON no cambia.

## 4. Data model & flow

La tabla sigue siendo tupla de constantes. Para L intermedia se localizan vecinos
contiguos y se evalúa `mu1+(mu2-mu1)*(L-L1)/(L2-L1)` sin redondeos intermedios.
Pantalla y contenido común de reportes consumen `detalle_mu`; no consultan la tabla otra vez.

## 5. Testing strategy

- AC1–5: pruebas unitarias independientes de selección, límites y bloqueos.
- AC6: prueba del Resultado, contenido común y extracción de PDF/Word.
- AC7: regresión completa, roundtrip JSON y ejemplos manuales existentes.
- Gate: unittest+cobertura de ramas, Ruff, mypy, pip check y pip-audit.

## 6. Sequencing & dependencies

| ID | Task | Done-check | Depends | Trace |
| --- | --- | --- | --- | --- |
| T001 | Escribir pruebas rojas del selector | L27 espera0.974; límites/filas prueban fallo | — | AC1–5 |
| T002 | Implementar selección y motor | pruebas del núcleo verdes; detalle viaja en Resultado | T001 | AC1–5/7 |
| T003 | Actualizar UI y memorias | prueba observable contiene extremos, fórmula y advertencia | T002 | AC6 |
| T004 | Documentar, construir y verificar | gate completo, EXE nuevo y memoria revisada | T003 | AC1–7 |

## 7. Risks & open decisions

Riesgo alto: presentar interpolación como norma MTC. Mitigación: rótulo explícito en cada salida.
Riesgo medio: interpolar accidentalmente V. Mitigación: seleccionar fila antes de L y probar huecos.
Riesgo medio: alterar celdas exactas. Mitigación: regresión exhaustiva de toda la tabla.
No hay decisiones abiertas: alcance confirmado por el usuario.

## Analysis

Spec, plan y tareas son consistentes. No modifica proyecto persistido ni ecuación59.
GATE PASS para implementar; autorización expresa del usuario y autopilot vigente.

