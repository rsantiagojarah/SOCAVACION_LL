---
type: analysis
title: Análisis — Importación HEC-RAS XLSX
description: Gate de consistencia entre constitución, especificación, plan y tareas.
tags: [sdd, analysis, hec-ras, xlsx]
timestamp: 2026-10-09T00:00:00-05:00
topic: sdd
slug: importacion-hec-ras-xlsx
status: pass
---

# Análisis — Importación HEC-RAS XLSX

## Gate

**PASS.** No hay contradicciones bloqueantes.

- La importación solo reemplaza geometría y nivel de agua; el núcleo LL queda intacto.
- El parser se separa de Qt y el diálogo no interpreta coeficientes.
- No hay conversión, remuestreo ni corrección silenciosa de datos externos.
- Cada criterio de aceptación tiene un done-check en T001–T004.
- El límite de 200 puntos coincide con el dominio actual; excederlo se bloquea.
- La dependencia propuesta es de lectura y queda sometida a `pip-audit`.

## Riesgo residual

El formato proviene de la exportación gráfica observada. Variantes de HEC-RAS con otros
encabezados se rechazarán en vez de inferirse. Esta limitación es visible y comprobable.

