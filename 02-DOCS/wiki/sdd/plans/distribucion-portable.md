---
type: plan
slug: distribucion-portable
status: approved in autopilot
---
# Plan portable
## 0. Global Constraints
No cambiar LL, JSON ni bibliografía. Español, <=250líneas por módulo, no borrados de carpetas.
## 1. Context & constraints
Spec distribución AC1–5; EXE local, sin instalación en el sistema ni publicación externa.
## 2. Architecture
PyInstaller (externo, desarrollo) empaqueta entrypoint interno + bibliotecas + docs.
Autocomprobación interna consume servicios existentes, no segundo motor.
Decisión: onedir frente a onefile para recursos explícitos y diagnóstico reproducible.
## 3. Interfaces & contracts
comprobar_instalacion(directorio)->Path: crea subcarpeta única y archivos del ejemplo; devuelve informe.
CLI --comprobar-instalacion DIRECTORIO: éxito0/error no0; sin interfaz visible.
scripts/empaquetar.py: genera dist/Socavacion_LL solo si no existe; subprocess sin shell.
## 4. Data model & flow
Modelo intacto. Directorio temporal único para pruebas, no sobrescribir archivos existentes.
Recursos congelados localizados bajo bundle; documentos protegidos en diálogo de destino.
## 5. Testing strategy
Tests reales autocomprobación y ruta congelada simulada; prueba negativa destinoexistente.
Ejecutar EXE real y leer salidas; comparar cifras con constantes del ejemplo manual.
## 6. Sequencing & dependencies
| ID | [P] | Task | Done-check | Depends-on | Trace |
| --- | --- | --- | --- | --- | --- |
| T001 | | Autocomprobación TDD | test_distribucion pasa con archivos reales y valor manual | — | AC2/3 |
| T002 | | Configurar empaquetado | script rechaza destinoexistente; build produce EXE | T001 | AC1/4 |
| T003 | | Ejecutar y documentar | EXE check sale0 y artefactos presentes; límites declarados | T002 | AC1/2/5 |
## 7. Risks & open decisions
Plugins Qt/fuentes omitidas: comprobar EXE completo. Entorno limpio no disponible:
registrar pendiente, no falsificar evidencia. Build se hace al integrar UI y calidad.
## Review Workload Forecast
Tres módulos pequeños, tests y script;300–450 líneas. Revisión separada de UI/núcleo.
## Analysis
AC1->T002/T003; AC2/3->T001/T003; AC4->T002; AC5->T003.
Sin cambio de datos/algoritmos. GATE PASS para build local; no certificación de distribución.
## Fuente de herramienta
[Documentación oficial PyInstaller](https://www.pyinstaller.org/en/stable/usage.html):
modo onedir/windowed y recursos add-data; verificada antes de elegir opciones de construcción.
