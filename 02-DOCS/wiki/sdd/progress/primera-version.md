---
type: progress
slug: primera-version
date: 2026-10-09
---

# Ejecución de v0.1

- T1: contratos inmutables y fuentes identificadas. PDF MTC preservados; DGA local y
  ficha verificable de Schreider. Dos ejemplos aritméticos documentados sin derivar
  valores esperados del núcleo. Ver `proposals/base-calculo-v01.md`.
- T2: núcleo puro, tablas literales y validación. Suite cubre caso manual, equilibrio
  de velocidades, contracción aplicada una vez, negativos y entradas fuera de dominio.
- T3: almacenamiento JSON estricto y sesión. Ida/vuelta, archivos dañados, tipos,
  límite de tamaño, escritura atómica, conservación ante error e invalidación probados.
- T4: gráfico único y memorias Word/PDF. Archivos reales inspeccionados por contenido
  y páginas renderizadas. Word contiene fracciones/potencias editables nativas.
- T5: formularios, acciones, sesión y resultados conectados conservando tema aprobado.
  Las tres pruebas nuevas de aceptación fallaron antes de conectar el controlador;
  después pasaron. No se afirma TDD estricto uniforme para toda la entrega.
- Revisión independiente de código: dos defectos reproducidos, ambos corregidos.
  Abrir el archivo actual tras Guardar: prueba roja Q=130 vuelto a120; verde al releer.
  Responsable de más de255 caracteres: prueba roja al exportar Word; verde limitando
  solo el metadato author y preservando todo el texto en el cuerpo.
- Casos adicionales revisados: cancelar cierre/nuevo, error de guardado, notas largas,
  conservación de texto, entradas numéricas extremas y prohibición de reportes obsoletos.
- T6: pruebas completas, compilación y capturas. El acta de verificación registra
  la corrida final y separa las comprobaciones ejecutadas de las capas no disponibles.

No se modifican originales MTC ni código de Metrados. Los temporales de revisión
están bajo `tmp/`; no son proyectos de producción ni entregables normativos.
