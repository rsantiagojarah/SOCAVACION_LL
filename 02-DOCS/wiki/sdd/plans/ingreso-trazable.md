---
type: plan
slug: ingreso-trazable
status: approved in autopilot
---
# Plan de ingreso trazable
## 0. Global Constraints
- Exclusivamente LL y no cohesivos; no cambiar fórmulas ni tablas.
- Máximo250 líneas por módulo de producción; identificadores propios en español.
- Preservar PDFs originales, Metrados y proyectos JSON v1.
- No ramas/commits: no existe repositorio Git; trabajo directo autorizado.
## 1. Context & constraints
Spec ingreso-trazable AC1–6. Tema Metrados existente y contrato Proyecto sin cambios.
## 2. Architecture
Todo interno: formulario -> diálogo de tablas -> constantes del núcleo (solo lectura).
Notas -> Proyecto.notas -> almacenamiento y reportes existentes.
Decisión: usar constantes existentes para evitar transcripciones divergentes en interfaz.
## 3. Interfaces & contracts
PaginaIngreso.cargar(Proyecto), obtener_proyecto()->Proyecto, cambiado Signal se conservan.
Nuevo diálogo consulta coeficientes existentes; no emite cambiado ni modifica valores.
## 4. Data model & flow
Modelo sin cambios. L válida preservada al alternar casilla. Excepción de la spec:
L inválida al marcar sin obstáculos se restablece a0 con aviso visible, nunca al calcular.
Notas usa editor multilínea; lectores/escritores del formulario reconocen ese editor.
## 5. Testing strategy
AC1/2/5: interacción Qt real; AC3: comparar filas/tablas con constantes, solo lectura;
AC4: ida/vuelta de formulario y archivo real; AC6: suite completa y conteo.
Mock únicamente diálogo modal si bloquea prueba; no simular formulario ni motor.
## 6. Sequencing & dependencies
| ID | [P] | Task | Done-check | Depends-on | Trace |
| --- | --- | --- | --- | --- | --- |
| T001 | | Pruebas rojas de ayuda/tablas/notas | unittest test_ingreso_trazable falla por comportamiento ausente | — | AC1–5 |
| T002 | | Implementar controles y consulta | mismas pruebas verdes; núcleo intacto | T001 | AC1–5 |
| T003 | | Revisar integración y aspecto | suite completa verde y capturas en dos tamaños | T002 | AC6 |
T002 consume Proyecto y constantes TABLA_BETA/TABLA_Z/TABLA_MU/LUCES_M; produce contratos de formulario intactos.
## 7. Risks & open decisions
Notas cambia tipo de control: no llamar text() indiscriminadamente. Tabla mu debe
conservar filas abiertas (<1, >4), sin convertirlas en intervalos nuevos. Actualización v0.3:
la selección lineal entre columnas L pertenece al selector puro del núcleo, no a la GUI.
## Review Workload Forecast
200–400 líneas en UI y pruebas; revisión mediana por compatibilidad de formulario.
Revisión independiente antes de integrar. Sin instalador en esta entrega.
