---
type: plan
slug: granulometria-documentada
status: approved in autopilot
---
# Plan de granulometría documentada
## 0. Global Constraints
Solo ecuación52 MTC, Di en mm, porcentajes por fracción. No cambiar motor LL ni tablas.
Módulos <=250 líneas y español. No nuevo formato JSON ni cambios a dataclass Proyecto.
## 1. Context & constraints
Spec granulometría AC1–6; fuenteprincipal HHDp92. Marcas de clase ingresadas explícitamente.
## 2. Architecture
Formulario -> diálogo Qt (interno) -> función pura calcular_diametro_medio (interna).
Aceptar -> Dm y anexo en Notas -> servicios existentes. Sin dependencias nuevas.
## 3. Interfaces & contracts
calcular_diametro_medio(fracciones: list[tuple[float,float]]) -> float o ValueError.
Aceptar valida simultáneamente Dm/anexo/límite y solo entonces actualiza ambos controles.
Entradas de1 a100 fracciones; límiteinformático explícito. Fuente de1 a500caracteres.
## 4. Data model & flow
Sin nuevos campos; anexo legible conserva Di,porcentaje,producto,sumatoria,Dm,fuente y p92.
Reabrir proyecto conserva anexo pero no repuebla editor de fracciones; declarado explícitamente.
## 5. Testing strategy
Núcleo: referencias manuales independientes y todos límites/tipos. Qt real: cancelar/aceptar,
invalidación, roundtripJSON real, rechazo atómico de anexo demasiado largo; cálculoLL.64 rechazado.
## 6. Sequencing & dependencies
| ID | [P] | Task | Done-check | Depends-on | Trace |
| --- | --- | --- | --- | --- | --- |
| T001 | | Implementar función pura por TDD | test_granulometria rojo->verde con referencias | — | AC1/2/5 |
| T002 | | Integrar diálogo y anexo | pruebas Qt/JSON verdes, cancelar sin mutación | T001 | AC3/4/6 |
| T003 | | Verificar integración | suite y captura revisadas; no cambios de fuente | T002 | AC1–6 |
## 7. Risks & open decisions
Datos acumulados se advierten pero su origen no puede inferirse de números solos;
usuario confirma porcentajes de intervalo. Nada se normaliza silenciosamente.
## Review Workload Forecast
400–600líneas código/pruebas en tres módulos, revisión separada de A.
## Analysis
Todos AC mapeados; función no duplica LL, guardar consume Proyecto intacto.
GATE PASS para herramienta Dm; no para gestor completo de muestras/escenarios.
