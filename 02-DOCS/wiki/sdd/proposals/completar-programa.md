---
type: proposal
title: Completar Socavación LL por fases
date: 2026-10-09
status: ruta-aprobada-ejecucion-automatica
---

# Completar el programa

## Problem

El usuario solicita completar el producto tras encontrar confuso el ingreso de luz
libre. v0.1 calcula solamente sección rectangular, material homogéneo y agua clara;
no cubre todavía una sección topográfica real ni valores entre celdas tabuladas.
Los proyectos y memorias existen, pero falta distribución independiente y controles
de calidad documentados en la verificación inicial.

## Intent

Completar las cuatro fases solicitadas, manteniendo exclusivamente LL y suelos
no cohesivos. No confundir completar funciones con eliminar restricciones científicas.

## Contexto

- Actor: ingeniero que necesita evaluar secciones de ríos, torrenteras y puentes.
- Situación actual: usa v0.1 o resuelve fuera del programa los casos no admitidos.
- Resultado buscado: ingresar datos representativos, calcular dentro del dominio
  sustentado, revisar perfiles y emitir memorias reproducibles desde un proyecto editable.
- Restricciones: MTC principal, coeficientes literales, SI, monolito modular,
  español, <=250 líneas/módulo, DRY/SOLID/KISS y aprobación previa de ecuaciones nuevas.
- Conocido: estructura y restricciones verificadas en modelos.py, motor.py e ingreso.py.
  No demostrado: que las fuentes actuales resuelvan interpolación, alpha irregular o mezcla.

## Scope / Non-scope

Propuesta de entregas separadas; cada una tendrá especificación, plan y pruebas.

| Entrega | Resultado esperado | Condición de habilitación |
| --- | --- | --- |
| A. Ingreso y trazabilidad | Obstáculos/luz libre claros, ayuda contextual, consulta de tablas y errores precisos; datum y origen de datos | No cambiar fórmulas ni aproximar datos |
| B. Granulometría y escenarios | Dm desde fracciones documentadas, muestras y varios escenarios editables | Verificar ecuación52 y validación de porcentajes; Dm no tabulado no habilita LL por sí solo |
| C. Sección real y coeficientes | Ingreso/importación de pares x/cota, puntos secos, perfiles variables; valores intermedios donde exista regla | Resolver alpha/Be, reparto de caudal, dominio de interpolación y mu antes de codificar |
| D. Resultados y memorias | Navegación gráfica, comparación de escenarios, trazabilidad de coeficientes, anexos de datos | Única evaluación vigente; distinguir resultados válidos de pendientes |
| E. Proyectos y distribución | Migración de v0.1, recuperación de trabajo, ayuda y ejecutable/instalador Windows | Prueba de recuperación y ejecución sin Python preinstalado en entorno limpio |
| F. Calidad | Análisis estático, tipos, cobertura, dependencias, regresiones y ejemplos manuales | Evidencia completa y revisión independiente; no certificación de ingeniería |

Estudio documental adicional: mezcla agua-sedimento/phi, unidades y discrepancias
de fuente. Solo incluir su implementación si se resuelve y aprueba el procedimiento.
Estratos y varios materiales no se asumen cubiertos por un solo Dm; requerirían
especificación científica separada. Continúan excluidos cohesivos, detritos,
otros métodos, socavación local y diseño automático de cimentaciones.
No incorporar un solucionador hidráulico: Q, velocidad y nivel vienen del estudio.

## Research input

- proposals/base-calculo-v01.md: fuentes, tablas literales y dos ejemplos manuales.
- proposals/proceso-calculo-normativa-local.md: antecedentes y discrepancias.
- verifications/primera-version-2026-10-09.md:53 pruebas históricas; controles pendientes.
- Código revisado: ingreso.py habilita L al desmarcar sin_obstaculos;
  motor.py usa un h único y repite Hs en puntos equidistantes; modelos.py solo guarda
  un escenario y un Dm. No hay soporte oculto para geometría irregular.

## Alternatives considered

1. **Recomendada:** completar por entregas verificables; investigar en paralelo lógico
   los pendientes científicos, sin desbloquearlos hasta tener aprobación.
2. Mejorar únicamente usabilidad y calidad de v0.1: menor alcance, pero no satisface
   el objetivo de perfiles reales del usuario.
3. No ampliar: conservar v0.1 y hacer los casos restantes manualmente. Evita nuevas
   hipótesis informáticas, pero mantiene las limitaciones que motivan esta solicitud.

## Tradeoffs

La selección literal impide usar muchos datos reales intermedios. Cambiar esa política
requiere una regla sustentada y aprobada; no basta con que una interpolación sea fácil.
La granulometría puede producir Dm válido y aun así no permitir LL si falta z documentado.
Un ejecutable probado en el equipo de desarrollo no demuestra instalación en Windows limpio.

## Risks

Duplicar mu en alpha, confundir ancho efectivo con luz libre, imponer caudal a ramas
mojadas sin criterio, cambiar valores por cercanía a una celda, usar unidades ambiguas,
perder proyectos anteriores o presentar una memoria con resultados obsoletos.
La búsqueda documental puede no resolver todos los casos: registrar el resultado
negativo y solicitar criterio técnico, nunca inventar una regla para declarar completitud.

## Rollback

Preservar v0.1 y sus ejemplos como regresión. Las migraciones no modificarán archivos
originales al abrirlos. Guardar versiones nuevas mediante acción explícita y conservar
respaldo antes de cualquier transformación incompatible.

## Success criteria

- El usuario comprende cuándo L participa en mu y puede consultar la tabla utilizada.
- Cada ampliación científica tiene fuente/página/unidad/dominio y ejemplo independiente aprobado.
- Un proyecto antiguo reabre sin pérdida y reproduce los ejemplos anteriores.
- Ediciones invalidan resultados; tablas, gráficos y memorias coinciden por escenario.
- Los casos nuevos tienen pruebas válidas, de borde y de fallo; no se ocultan pendientes.
- Se entrega distribución local y se documenta qué entorno de Windows fue realmente probado.
- No se etiqueta «completo» mientras falte algún criterio acordado o evidencia exigida.

## Recommendation

Aprobar la ruta1 y las reglas del borrador de constitution.md. Comenzar por A y
preparar el cierre documental de C/phi. La ejecución automática puede cubrir
especificaciones, planes, código y pruebas de funciones dentro del alcance acordado;
debe detenerse para aprobar ecuaciones/reglas nuevas, resolver ambigüedad material
o solicitar permisos de instalación/distribución que correspondan.

## Decisiones pendientes del usuario

- Aprobar esta ruta y el borrador de reglas de calidad, o ajustar alcance.
- Elegir ejecución automática con esas pausas técnicas o revisión en cada fase.

Actualización: el usuario respondió «SI» a la propuesta de aprobar la ruta y
ejecutarla automáticamente. Se registra aprobación global, no aprobación individual
de ecuaciones futuras. Las pausas técnicas descritas permanecen obligatorias.

No se ha modificado código de producción en esta etapa. La solicitud inicial de
completar el programa no se registra como aprobación de esta propuesta aún no mostrada.

```json result-envelope
{"status":"blocked","executive_summary":"Ampliación delimitada; pendiente de aprobación de alcance y modo de ejecución.","artifact":"02-DOCS/wiki/sdd/proposals/completar-programa.md","next_recommended":"specify","risk":"high","skill_resolution":{"used":["sdd","constitution","specify"],"missing":[],"fallback":[],"compact_rules":["No nuevas ecuaciones sin aprobación","Mantener fuentes y dominio explícitos"]},"evidence":["Código de ingreso y núcleo revisado","Pendientes documentales contrastados","Borrador de reglas completado"]}
```
