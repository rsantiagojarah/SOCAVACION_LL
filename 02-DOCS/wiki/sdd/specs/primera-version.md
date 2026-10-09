---
type: spec
slug: primera-version
status: implemented-local-v01
approval: autorizacion-expresa-de-implementacion-del-alcance-propuesto-en-chat
timestamp: 2026-10-09
---
# Primera versión funcional de Socavación LL

## Problem & why

El usuario necesita pasar de la vista previa aprobada a cálculos reproducibles,
proyectos editables y memorias de ingeniería con fuentes identificadas.

## Cost of not building it

La interfaz actual no calcula ni conserva trabajo; cada evaluación debe repetirse manualmente.

## The cheapest alternative

Una memoria manual o una hoja de cálculo resuelve un caso, pero no ofrece el flujo
de escritorio y trazabilidad integrada pedidos. Se implementa la versión limitada
previamente propuesta, no un solucionador hidráulico general.

## Goals

- Editar, guardar, abrir y modificar un proyecto por escenario.
- Calcular LL para sección rectangular, lecho homogéneo no cohesivo y agua clara.
- Ver perfiles, coeficientes, sustituciones y resultados por puntos.
- Exportar la misma evaluación vigente a Word y PDF.

## Non-goals / out of scope

Secciones irregulares, estratos, mezcla agua-sedimento, suelos cohesivos, detritos,
socavación local, otros métodos, interpolación/extrapolación de coeficientes,
cálculo del nivel de agua y diseño automático de cimentaciones quedan fuera de v0.1.
No se declara validación profesional del modelo para una obra real.

## Users & context

El ingeniero responsable aporta hidráulica, granulometría, clasificación y referencia
vertical; comprueba la aplicabilidad del método. Se conserva el estilo aprobado de Metrados.

## Behaviour

Se inicia un proyecto editable. El usuario puede cargar el ejemplo identificado,
modificar parámetros, calcular y exportar. Editar cualquier dato invalida resultados
y deshabilita reportes. Abrir un archivo inválido no destruye el trabajo actual.
Cerrar, abrir otro proyecto o crear uno nuevo exige decidir sobre cambios sin guardar.
Los valores sin respaldo tabulado producen un mensaje preciso, nunca un valor inventado.
Las memorias identifican los dos MTC como principales y alpha/beta/z como complemento.

## Acceptance criteria

1. El ejemplo Q=120, B=20, h=3, Dm=1 mm, T=100, sin obstáculos, phi=1
   entrega Hs=4.736513861635 m y Sg=1.736513861635 m (tolerancia 1e-9 m).
2. Cohesivos, agua no clara, valores no finitos, h<=0 y coeficientes no tabulados se rechazan.
3. Los archivos guardados reabren con todos sus datos; una versión desconocida se rechaza.
4. Cambiar un dato elimina la evaluación visible y bloquea las exportaciones.
5. Word y PDF incluyen entradas, ecuaciones, sustituciones, tabla, gráfico, fuentes y límites.
6. El máximo es 250 líneas por módulo; el cálculo no importa Qt ni librerías de reportes.
7. Los perfiles diferencian Hs, Sg algebraica y cota; Sg negativa no se presenta como sedimentación.
8. El estilo aprobado y la navegación en español se conservan.

## Points to clarify

- **decisión diferida**: ampliación a secciones irregulares, mezcla y valores intermedios;
  fuera de esta entrega, con bloqueo explícito.
- **suposición tomada**: la instrucción «SI IMPLEMENTA LA PRIMERA VERSION» autoriza
  ejecutar el alcance v0.1 previamente presentado y la interfaz aprobada, no nuevos métodos.
- No se supone que todos los pendientes científicos estén resueltos.
