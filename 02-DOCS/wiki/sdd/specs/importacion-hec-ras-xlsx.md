---
type: spec
title: Spec — Importación HEC-RAS XLSX
description: WHAT y WHY para cargar terreno y nivel de agua desde la exportación gráfica HEC-RAS.
tags: [sdd, spec, hec-ras, xlsx]
timestamp: 2026-10-09T00:00:00-05:00
topic: sdd
slug: importacion-hec-ras-xlsx
status: approved
---

# Spec — Importación HEC-RAS XLSX

> Aprobada expresamente por el usuario el 2026-10-09.

## Problema y objetivo

Transcribir manualmente decenas de estaciones y cotas desde HEC-RAS introduce errores y
rompe la trazabilidad. El usuario necesita seleccionar un `.xlsx` exportado por cada
sección y cargar su serie `Ground` y un perfil `WS` en el proyecto irregular vigente.

## Alcance

- Detectar las series por sus encabezados HEC-RAS `Ground`, `Bank Sta` y `WS ...`.
- Importar pares de terreno y la cota horizontal del perfil de agua seleccionado.
- Confirmar unidades en metros antes de aplicar.
- Mostrar resumen previo y aplicar el cambio de forma atómica.
- Conservar Q, V, pendiente, T, Dm, luz libre, material y demás datos existentes.
- Registrar archivo, hoja, perfil WS y márgenes en Notas.
- Mantener el archivo fuente intacto.

## Fuera de alcance

- Ejecutar HEC-RAS, leer `.prj/.gxx/.hdf`, convertir pies a metros o importar caudales.
- Usar `EG`, `WS Fill` o `Bank Sta` para cambiar el reparto LL.
- Remuestrear perfiles con más de 200 puntos.
- Importar varias secciones desde un mismo libro en esta versión.

## Criterios de aceptación

1. Dado el formato observado, el importador obtiene 55 puntos `Ground`, conserva el
   primer x `-2.1000000349769e-11`, el último x `63.2999992370605` y obtiene
   `WS PF 1 = 2511.00366210938`, sin modificar el libro.
2. La detección usa las etiquetas `Ground`/`WS ...` y las subcolumnas `x`/`y`; no depende
   de que siempre sean C–D y G–H.
3. Si hay varios perfiles `WS`, el usuario elige uno; si no existe ninguno, se bloquea.
4. La importación solo se aplica tras confirmar metros y aceptar el resumen.
5. Al aplicar, el proyecto queda como irregular, cambia puntos y cota de agua, invalida
   cualquier resultado anterior y conserva sin cambios los demás parámetros.
6. Archivos excesivos, fórmulas, series incompletas, coordenadas no finitas, x
   decrecientes, puntos idénticos o WS no horizontal producen un error en español
   y no mutan el proyecto. Dos x iguales con cotas distintas conservan un tramo vertical.
7. La procedencia y `Bank Sta` detectadas se conservan en Notas; no participan en LL.
8. La suite, cobertura, tipos y auditoría configurados continúan en PASS; ningún módulo
   de producción supera 250 líneas.

## Aclaraciones propuestas

- El libro representa una sección. Si hay más de una hoja con `Ground`, se bloquea para
  evitar seleccionar silenciosamente una geometría equivocada.
- La horizontalidad de WS se comprobará con tolerancia informática absoluta de `1e-9`
  en las unidades del archivo; no es un criterio MTC ni modifica valores.
- Se añadirá `openpyxl==3.1.5` como dependencia de lectura XLSX.
- Evidencia sobrevenida durante la implementación: los puntos 8 y 9 del `Ground` real
  comparten x `23.3999996185303` y tienen cotas distintas. El programa conserva ese
  tramo vertical exactamente; no constituye interpolación ni corrección del archivo.
