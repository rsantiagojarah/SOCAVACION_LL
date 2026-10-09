---
type: verification
title: Verificación de ampliación parcial v0.2.0
timestamp: 2026-10-09
topic: sdd
source_state: sin-Git; manifiesto-src-SHA256 f13f24862872c50efce93e73420a6f4c4c6c89f17fc2544863449cc36ef1571a
---
# Verificación — 2026-10-09

## Alcance del dictamen

PASS para specs ingreso-trazable, granulometria-documentada, calidad-local y
distribucion-portable (las dos últimas entregas funcionales B/E son parciales).
NO COMPLETO para la ruta global. No equivale a validación de ingeniería para obra.
Manifiesto: rutas relativas de src ordenadas por FullName, separador /, dos puntos,
SHA256 de bytes en minúsculas, filas unidas con LF sin LF final; SHA256 del UTF-8.

## Gate real, después de la última edición productiva

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/verificar.ps1`
finalizó con código0; resultado.json completo=true y nueve pasos código0.
La excepción de política aplica solo al proceso, no cambia la configuración permanente.

- 86 pruebas unittest OK.
- Ramas núcleo/dominio68/70=97.1429%, umbral90% sin redondear; cobertura combinada99%.
- Ruff E4/E7/E9/F sobre src: sin errores.
- mypy estricto núcleo/dominio: siete módulos sin errores; no abarca GUI.
- pip check: sin incompatibilidades.
- pip-audit:59 paquetes, cero avisos conocidos y cero omitidos en esta consulta.
- Máximo productivo195 líneas (ingreso.py), menor que250.

Logs completos: tmp/calidad/01–09-*.log; resultado.json, cobertura.json y auditoria.json.
Intento previo sin acceso a red falló correctamente, no se contabiliza como auditoría limpia.
Auditoría previa identificó avisos de pip25.0.1: conservada como auditoria-antes-pip.json.
Se actualizó el gestor de desarrollo a26.2.1; dependencias productivas no cambiaron.

## Criterios y tareas con evidencia

| Spec / AC | Evidencia observable |
| --- | --- |
| A1/2 | test_ingreso_trazable: casilla/L, preservación válida y restauración inválida con aviso |
| A3 | diálogo solo lectura, valores exactos y fuentes; capturas consulta_beta/z/mu revisadas |
| A4/5 | notas multilínea/JSON; señales e invalidación; consulta no cambia proyecto |
| A6 | suite86, test_calculo/test_proyectos y control de250 líneas |
| B1/2 | test_granulometria:0.64 y1mm; inválidos/tolerancia sin normalizar |
| B3/4 | Qt real: aplicar/cancelar, anexo, JSON y contenido común de memorias |
| B5/6 | Dm0.64 bloqueado por z; notas largas rechazadas sin cambio parcial |
| F1/2/3 | logs02/03/05/06/07;86 pruebas, análisis/tipos y ramas97.1429% |
| F4/5 | logs08/09; controles positivos/negativos en test_calidad y revisión independiente |
| E1/2/3 | EXE real sin invocar .venv; salida0 y ejemplo coincidente en ruta con espacios |
| E4/5 | test_distribucion/test_recursos, docs empaquetados, LEEME con límite Windows limpio |

T001–T003 de cada plan se relacionan con esos AC; lista comprobada en
progress/completar-programa.md. TDD observado por los implementadores; revisión independiente
ejecutó además26 pruebas focalizadas y editó una celda Qt real antes de Aplicar (Dm0.66).
No hallazgos bloqueantes pendientes en el alcance revisado.

Verificador propio: acepta exactamente90%, rechaza89.9%, módulos ausentes/adicionales,
contadores inválidos, falta de herramienta; propaga primer fallo (control7) y éxito0.
No demuestra detección de todas las violaciones posibles; no es un verificador formal.

## Distribución y apariencia

dist/Socavacion_LL/Socavacion_LL.exe, PyInstaller6.22.3 onedir/windowed.
SHA256 EXE: f1346df1ba5229f1a7036e9813c63f3922db1c5b64e09c1ac764df6e22f604c4.
Se copió la carpeta generada a tmp/portable con espacios y se ejecutó allí, oculto,
con --comprobar-instalacion. Salida0; evidencia en
tmp/comprobacion portable/comprobacion-rfh938fh/:

- Hs=4.736513861635207m; Sg=1.7365138616352072m.
- proyecto_recuperado=true, estado=correcto.
- JSON603bytes, Word80144bytes, PDF103985bytes, captura81976bytes.

La carpeta temporal creada fuera del sandbox exige permiso para leerla desde este;
lectura autorizada y copias de QA en tmp/memoria-portable.* e interfaz-portable.png.
Word exportado mediante instancia COM oculta propia, cerrada al terminar.
Word/PDF: cuatro páginas cada uno, render Poppler y revisión visual de las ocho páginas;
ecuaciones, tablas, gráfico y referencias legibles, sin recortes. Interfaz y diálogos
revisados con imágenes reales Qt. Advertencias de fuentes/offscreen del test no se
confundieron con prueba visual; captura EXE correcta.
LEEME del bundle sincronizado tras QA; binario no modificado.

## Integridad de fuentes

PDF originales conservados, SHA256 idénticos:

- HHD2011:0a1bdcd7c94016760642de91baf4d6e317e4cc85c529dfefae9a6bf76c8dcd88.
- Puentes2018:46d37849141b3acef44bdae112496dafbb5d6813dc008d5495c2f2bb760936b1.

Tabla13 filaV>4 revisada visualmente; se corrigió transcripción previa L25/L30,
no la normativa. Prueba independiente de toda la fila y ejemplos previos verdes.

## Capas no ejecutadas y límites

- HERRAMIENTA-AUSENTE: Windows limpio/VM independiente, firma e instalador no disponibles;
  no forman parte de AC de la entrega portable acotada y siguen pendientes de ruta E.
- SUSTITUIDA: render_docx/LibreOffice por Word COM y Poppler en Windows; no demuestra
  igualdad de maquetación en otros procesadores de texto.
- SUSTITUIDA: sin Git ni diff-cover, cobertura global de núcleo y tests explícitos;
  no demuestra100% de líneas modificadas ni independencia de orden de toda la suite.
- NO-APLICA: servicios de red/servidor/bases de datos, inexistentes en este monolito.
- Auditoría de avisos no demuestra ausencia de vulnerabilidades no publicadas.

No se implementaron irregularidad, interpolación ni mezcla. Propuesta científica
pendiente: proposals/seccion-irregular-verificada.md. Pausa técnica conforme SDD
y exigencia de aprobación previa del usuario; no retirar bloqueos por completar software.

```json result-envelope
{"status":"complete","executive_summary":"PASS de cuatro especificaciones acotadas; ruta completa pendiente.","artifact":"02-DOCS/wiki/sdd/verifications/ampliacion-2026-10-09.md","next_recommended":"clarify","risk":"high","skill_resolution":{"used":["sdd","implement","verify"],"missing":[],"fallback":["Registro local ausente: lectura de skills locales","Word COM para QA documental"]},"evidence":["Gate9 pasos exit0","EXE real exit0","Revisión visual","Revisión independiente"]}
```
