---
type: proposal
title: Propuesta — Importación de secciones HEC-RAS desde XLSX
description: Mapeo verificado del Excel exportado por HEC-RAS al perfil irregular LL.
tags: [sdd, propuesta, hec-ras, xlsx, seccion-irregular]
timestamp: 2026-10-09T00:00:00-05:00
topic: sdd
slug: importacion-hec-ras-xlsx
status: approved
---

# Propuesta — Importación de secciones HEC-RAS desde XLSX

## Evidencia del archivo suministrado

Se inspeccionó en modo de solo lectura `seccion hec ras.xlsx`. Contiene una hoja visible,
`Hoja1`, con 58 filas y 10 columnas, sin fórmulas, tablas, gráficos, celdas combinadas,
hojas ocultas ni nombres definidos.

Las series se identifican por las filas de encabezado, no por una letra fija:

| Serie | Encabezado observado | Datos observados | Uso propuesto |
| --- | --- | --- | --- |
| Terreno | `Ground`, subcolumnas `x`/`y` | 55 pares; un tramo vertical | perfil irregular |
| Agua | `WS PF 1`, subcolumnas `x`/`y` | cota 2511.00366210938 | nivel de agua |
| Márgenes | `Bank Sta`, subcolumnas `x`/`y` | estaciones 19.8999996 y 60.4000015 | trazabilidad; no modifica LL |
| Energía | `EG PF 1` | serie adicional | no participa en LL |
| Relleno | `WS Fill` | polígono auxiliar | no participa en LL |

El archivo no declara si las coordenadas están en metros o pies. El programa trabaja
solo en SI, por lo que no convertirá ni supondrá unidades: exigirá confirmación de metros.

## Proceso propuesto

1. El usuario abre el editor de sección irregular y pulsa **Importar HEC-RAS (.xlsx)**.
2. El programa lee el archivo sin modificarlo y localiza `Ground` y las series `WS ...`.
3. Si existen varios perfiles de agua, el usuario elige uno.
4. El usuario confirma que estaciones y cotas están expresadas en metros.
5. Se muestra un resumen: hoja, cantidad de puntos, rango de estaciones, cota de agua
   y estaciones de margen detectadas.
6. Al aceptar, se reemplaza el perfil del editor y la cota de agua. Los demás datos del
   proyecto —Q, V, pendiente, T, Dm y coeficientes— permanecen sin cambios.

## Reglas de seguridad y alcance

- Solo `.xlsx`; no `.xls`, CSV ni archivos de proyecto HEC-RAS.
- Lectura con `openpyxl` en modo de solo lectura, sin vínculos externos ni macros.
- Tamaño máximo 10 MiB y hasta 200 puntos, límite vigente del modelo.
- Se conservan los `float` exportados; no se redondea, corrige, reordena ni remuestrea.
- Se admiten abscisas consecutivas iguales con cotas distintas, porque representan
  tramos verticales de HEC-RAS. Se bloquean abscisas decrecientes, puntos idénticos,
  celdas no numéricas, fórmulas,
  Ground incompleto, ausencia de WS, varias cotas dentro de un mismo WS o unidades
  no confirmadas.
- `Bank Sta`, `EG` y `WS Fill` no alteran el cálculo LL. Las márgenes se registran en
  Notas porque el método implementado no distribuye rugosidades ni zonas por margen.
- La importación no ejecuta un modelo hidráulico ni valida el resultado HEC-RAS.
