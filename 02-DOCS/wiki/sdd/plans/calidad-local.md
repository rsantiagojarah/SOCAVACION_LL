---
type: plan
slug: calidad-local
status: approved in autopilot
---
# Plan de calidad local
## 0. Global Constraints
- No cambiar tablas, ecuaciones ni dominio científico. Módulos de producción <=250 líneas.
- Identificadores propios en español; Python/PySide6 y unittest existentes.
- No suprimir hallazgos para obtener verde ni atribuir certificación a estas herramientas.
## 1. Context & constraints
Spec calidad-local AC1–5; propuesta F autorizada. Ningún cambio en UI durante esta tarea.
## 2. Architecture
Herramientas externas de desarrollo -> orquestador local -> código/pruebas existentes.
Se conserva unittest; no migrar de framework para medir cobertura.
## 3. Interfaces & contracts
Comando scripts/verificar.ps1 -> código0 solo cuando todas sus verificaciones obligatorias pasan.
Dependencias de desarrollo separadas en pyproject; salidas bajo tmp/calidad.
## 4. Data model & flow
Sin cambio de Proyecto/Resultado ni JSON. Solo anotaciones de tipos compatibles y configuración.
## 5. Testing strategy
AC1 suite real. AC2 herramientas sobre producción/núcleo. AC3 medición real de ramas.
AC4 consulta de avisos sin datos de proyectos. AC5 inyectar comando fallido en test del
orquestador o control temporal no destructivo y observar salida no cero; control bueno también.
## 6. Sequencing & dependencies
| ID | [P] | Task | Done-check | Depends-on | Trace |
| --- | --- | --- | --- | --- | --- |
| T001 | | Configurar herramientas | comandos ejecutables, sin errores o faltantes ocultos | — | AC2–4 |
| T002 | | Completar tipos/pruebas necesarias | suite verde, cobertura umbral y análisis limpio | T001 | AC1–3 |
| T003 | | Crear comando de verificación | positivo pasa y negativo falla | T002 | AC5 |
Tareas internas seriales. Disjuntas de ingreso-trazable salvo corrida de suite compartida.
Interfaces: firma pública calcular_proyecto(Proyecto)->Resultado y validaciones preservadas.
## 7. Risks & open decisions
Red/instalación requiere permiso si falla sandbox. No actualizar dependencias productivas
silenciosamente por un aviso; informar evidencia y proponer corrección acotada.
## Review Workload Forecast
Configuración, scripts, anotaciones y pruebas; riesgo mediano; revisar por herramienta.
