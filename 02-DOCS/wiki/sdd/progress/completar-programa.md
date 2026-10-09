---
type: progress
date: 2026-10-09
status: entrega-parcial-verificada-pausa-tecnica
---
# Avance de la ruta aprobada — v0.2.0

El «SI» autoriza ruta y ejecución automática. No autoriza nuevas ecuaciones.
Sin Git disponible; trabajo directo, sin ramas/commits. Se preservaron PDF y JSON v1.
Registro local de skills ausente: resolución por archivos locales, no se simularon gates.

## Tareas terminadas de las especificaciones acotadas

- [x] A/T001: pruebas rojas por ausencia de ayuda, tablas y notas multilínea.
- [x] A/T002: controles implementados; ocho pruebas focalizadas verdes.
- [x] A/T003: integración y capturas 1480x820/1000x640 revisadas.
- [x] B-parcial/T001: función Dm, referencias0.64/1mm y límites por TDD.
- [x] B-parcial/T002: diálogo y anexo atómicos; nueve pruebas Qt/JSON/contenido verdes.
- [x] B-parcial/T003: integración y captura revisadas; no redondeo de Dm para obtener z.
- [x] E-parcial/T001: autocomprobación con archivos reales y regresión sin modales.
- [x] E-parcial/T002: PyInstaller genera EXE; destino existente rechazado sin borrado.
- [x] E-parcial/T003: EXE desde ruta con espacios devuelve0; JSON/DOCX/PDF/captura presentes.
- [x] F/T001: herramientas instaladas y comandos reproducibles.
- [x] F/T002: tipos, ramas y análisis verificados; 86 pruebas pasan.
- [x] F/T003: controles buenos/malos del verificador; auditoría completa sin avisos conocidos.

Corrección separada de defecto de transcripción: mu(V>4,L25)=0.94 y
mu(V>4,L30)=0.95, tras revisar tabla13 original y observar regresión roja->verde.
No cambia las ecuaciones. Recalcular memorias anteriores afectadas por esas celdas.

## Estado de la ruta completa

- A: ingreso aclarado; datum/origen en notas, no campos estructurados nuevos.
- B: Dm implementado; muestras estructuradas y varios escenarios pendientes.
- C: evidencia y propuesta por franjas preparada; pendiente aprobación técnica específica.
- D: memorias existentes conservadas; comparación de escenarios pendiente.
- E: portable local terminado; recuperación, instalador y Windows limpio pendientes.
- F: controles locales terminados; no certificación científica ni garantía de seguridad.

No se declara el programa completo. La siguiente decisión es aprobar
[el esquema irregular](../proposals/seccion-irregular-verificada.md), manteniendo
el bloqueo de interpolación y mezclas. B/D/E restantes conservan autorización de ruta,
pero no se presentan como entregados en esta iteración.

Ver [evidencia final](../verifications/ampliacion-2026-10-09.md).
