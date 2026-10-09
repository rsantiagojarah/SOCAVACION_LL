---
type: plan
title: Plan — Importación HEC-RAS XLSX
description: Parser seguro, selección de perfil WS, aplicación atómica y verificación.
tags: [sdd, plan, hec-ras, xlsx]
timestamp: 2026-10-09T00:00:00-05:00
topic: sdd
slug: importacion-hec-ras-xlsx
status: approved
---

# Plan — Importación HEC-RAS XLSX

> Aprobado expresamente por el usuario el 2026-10-09.

> Spec: [../specs/importacion-hec-ras-xlsx.md](../specs/importacion-hec-ras-xlsx.md)  
> Propuesta: [../proposals/importacion-hec-ras-xlsx.md](../proposals/importacion-hec-ras-xlsx.md)

## 0. Restricciones globales

- No cambiar ecuaciones, coeficientes ni alcance LL.
- El parser no importa Qt ni modifica proyectos; devuelve datos inmutables.
- El diálogo aplica todos los cambios juntos o ninguno.
- No corregir, ordenar, redondear, convertir ni remuestrear los datos HEC-RAS.
- Identificadores propios en español, DRY/SOLID/KISS y máximo 250 líneas por módulo.
- El archivo fuente se abre en solo lectura y nunca se sobrescribe.

## Arquitectura

```text
[Editor irregular]
       |
       v
[Diálogo importar/confirmar] --> [lector XLSX seguro]
       |                                  |
       v                                  v
[puntos + cota WS + procedencia]    [archivo intacto]
       |
       v
[Proyecto irregular] --> [geometría irregular] --> [motor LL sin cambios de ecuación]
```

### Módulos

- `infraestructura/hec_ras_xlsx.py`: lectura y validación de series.
- `presentacion/importacion_hec_ras.py`: selección de archivo/WS, confirmación SI y resumen.
- `presentacion/seccion_irregular.py`: botón de importación y entrega atómica al formulario.
- `pruebas/test_importacion_hec_ras.py`: fixtures XLSX temporales, parser y flujo Qt.

## Contratos

```text
leer_seccion_hec_ras(ruta: Path) -> SeccionHecRas
  puntos: tuple[PuntoTerreno, ...]
  perfiles_agua: tuple[PerfilAguaHecRas, ...]
  estaciones_margen: tuple[float, ...]
  hoja: str
```

El lector busca un par de columnas donde la fila de etiqueta sea `Ground` y la fila
siguiente sea `x/y`. Para cada etiqueta que empiece por `WS ` forma un perfil horizontal.
Rechaza valores de fórmula y pares parciales.

## Flujo de datos

1. Seleccionar `.xlsx`.
2. Validar tamaño y estructura; no tocar el formulario.
3. Elegir WS y confirmar metros.
4. Mostrar puntos, extremos, cota de agua y Bank Sta.
5. Aceptar: sustituir la tabla del editor, devolver cota de agua y procedencia.
6. Aceptar editor: actualizar el formulario una vez y emitir un solo cambio.

## Estrategia de pruebas

- Fixture mínimo que reproduce encabezados HEC-RAS sin copiar el archivo del usuario.
- Prueba local adicional contra el archivo suministrado: 55 puntos y cota observada.
- Mutantes: columnas desplazadas, varios WS, Ground ausente, fórmula, x decreciente,
  tramo vertical conservado,
  WS variable, archivo grande y cancelación del diálogo.
- Regresión: importación invalida resultado; cálculo irregular posterior cierra Q.
- Gate final: `scripts/verificar.ps1`.

## Tareas

| ID | Tarea | Done-check | Depende de |
| --- | --- | --- | --- |
| T001 | Añadir lector XLSX puro y dependencia | pruebas del parser pasan con columnas desplazadas y errores seguros | — |
| T002 | Integrar diálogo en editor irregular | prueba Qt importa, confirma, aplica una vez y cancela sin mutar | T001 |
| T003 | Conservar procedencia y verificar archivo real | prueba de integración obtiene 55 puntos/WS y Notas trazables | T002 |
| T004 | Regresión y gate completo | 109+ pruebas, ramas >=90%, Ruff, mypy, dependencias y auditoría PASS | T001–T003 |

## Riesgos

| Riesgo | Mitigación |
| --- | --- |
| Exportaciones HEC-RAS con otro encabezado | error explícito; no adivinar columnas |
| Libro en pies | confirmación obligatoria; no conversión silenciosa |
| Varios WS | selección humana antes de aplicar |
| Perfil demasiado grande | bloquear >200; no perder puntos por remuestreo |
| Dependencia XLSX vulnerable | versión fijada y `pip-audit` en gate |
