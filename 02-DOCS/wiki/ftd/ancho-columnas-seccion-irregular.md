---
author: rj
branch: sin-git/directo
status: in-progress
---
# Ancho de columnas de la sección irregular

## Intent

Distribuir el ancho disponible entre abscisa y cota para reducir el recorte visual de
coordenadas HEC-RAS largas.

## Scope

Incluye la configuración adaptable de ambas columnas y una prueba de regresión Qt.
No cambia valores, importación, persistencia, geometría ni cálculo LL.

## Checklist

- [x] Configurar ambas columnas en modo adaptable — prueba observa `Stretch` en ambas.
- [x] Comprobar la interfaz renderizada — captura muestra las columnas equilibradas.
- [x] Ejecutar la regresión relacionada — pruebas de importación e interfaz pasan.

## Evidence

- TDD rojo: la columna 0 devolvió `Interactive` en lugar de `Stretch`.
- TDD verde: la prueba específica pasó después de configurar la cabecera.
- Captura: `tmp/qa_hec_ras/02_editor_55_puntos.png`; ambos encabezados ocupan
  la mitad disponible y la primera abscisa se lee completa.
- Regresión: 19 pruebas relacionadas en PASS y Ruff en PASS.

## Next

Cerrar y volver a abrir la aplicación para cargar el cambio visual.
