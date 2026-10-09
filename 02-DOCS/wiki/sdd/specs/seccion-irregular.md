---
type: spec
title: Spec — Sección transversal irregular
description: WHAT y WHY para evaluar socavación general LL por franjas en una sección irregular.
tags: [sdd, spec, lischtvan-levediev, seccion-irregular]
timestamp: 2026-10-09T00:00:00-05:00
topic: sdd
slug: seccion-irregular
status: clarified — approved in autopilot
---

# Spec — Sección transversal irregular

> Slug: `seccion-irregular` · Estado: aclarada y aprobada en autopilot · Creada: 2026-10-09
> Hereda los requisitos expresos del usuario y las reglas aplicables del
> [borrador de constitución](../constitution.md).

## Problem & why

La versión actual representa el cauce como un rectángulo y entrega el mismo resultado
en todo el ancho. Una sección levantada en campo cambia el tirante y el caudal unitario
a lo largo del perfil; ignorar esa variación impide usar la aplicación en secciones
naturales dentro del alcance LL no cohesivo aprobado.

## Cost of not building it

El usuario debe transformar manualmente una topografía irregular en rectángulos o hacer
el reparto por franjas fuera del programa. Eso rompe la trazabilidad entre terreno,
cálculo, gráfico y memoria, y facilita errores de transcripción.

## The cheapest alternative

Mantener la versión rectangular y calcular cada franja en una hoja externa. Esa opción
permite una comprobación puntual, pero no verifica el cierre de caudal, no conserva la
geometría con el proyecto y no genera un perfil ni una memoria coherentes desde una sola
evaluación.

## Goals

- Permitir elegir entre sección rectangular y sección irregular en un mismo proyecto.
- Ingresar, revisar y modificar pares ordenados de abscisa y cota del terreno.
- Calcular LL no cohesivo por franjas, mostrando tirante, caudal unitario, caudal de
  franja, Hs, Sg y cota LL en cada franja.
- Conservar el terreno completo en el gráfico, incluidos los puntos secos.
- Mostrar el cierre de caudal y un indicador de estabilidad al refinar la discretización.
- Guardar y reabrir la geometría sin perder compatibilidad de lectura con proyectos v1.
- Incluir ecuaciones, sustitución, tabla por franja, límites y fuentes en Word y PDF.

## Non-goals / out of scope

- Suelos cohesivos, mezclas agua-sedimento, estratos o varios materiales en una sección.
- Más de una rama mojada, islas, cauces desconectados o agua no horizontal.
- Reparto por rugosidades, zonas sin erosión, factores K distintos de 1 o modelación
  hidráulica para obtener el nivel del agua.
- Interpolación de beta, z o filas de velocidad V; extrapolación de luz libre.
- Socavación local, otros métodos, socavación total o diseño de cimentaciones.
- Interpretar una Sg negativa como sedimentación.

## Users & context

El usuario es el profesional que dispone de caudal, velocidad, nivel de agua, perfil
topográfico y caracterización granulométrica. Necesita revisar el reparto y la memoria,
no sustituir el estudio hidráulico ni el juicio del ingeniero responsable.

## Behaviour

- Ruta principal: el usuario selecciona sección irregular, introduce al menos dos puntos
  ordenados, fija una resolución base y calcula. El programa identifica una rama mojada,
  reparte Q, evalúa LL por franja y presenta tabla, gráfico y memoria.
- Edición: cualquier cambio de tipo, geometría o datos invalida el resultado y bloquea
  los reportes hasta recalcular.
- Compatibilidad: un proyecto v1 rectangular se abre con su geometría y valores originales;
  al guardarlo se actualiza al formato vigente sin sobrescribir silenciosamente el archivo
  ante un fallo.
- Límites: los puntos secos se dibujan, pero no entran al cálculo. Dos ramas mojadas,
  abscisas repetidas o desordenadas y ausencia de área mojada bloquean el cálculo con un
  mensaje en español.
- Control: el programa informa número y ancho de franjas, diferencia relativa entre una
  malla base y otra refinada, y diferencia de cierre entre la suma de caudales de franja y Q.

## Acceptance criteria

1. Dado el ejemplo independiente de dos franjas de 10 m con h=2 m y h=4 m, Q=120 m³/s,
   Dm=1 mm, beta=mu=phi=1 y z=0.4, cuando se evalúa el reparto aprobado, entonces alpha,
   q, Q de franja, Hs y Sg coinciden con los valores documentados dentro de 1e-9.
2. Dado un terreno lineal con una sola rama mojada, cuando se discretiza, entonces el área
   de cada franja es trapezoidal exacta, `h_j=área/ancho` y la suma de caudales reproduce Q
   dentro de tolerancia relativa 1e-12.
3. Dado un perfil con dos ramas mojadas, abscisas no crecientes o ninguna área mojada,
   cuando se calcula, entonces no se genera resultado y se explica el límite en español.
4. Dado un proyecto irregular válido, cuando se guarda y vuelve a abrir, entonces se
   conservan tipo, puntos y resolución; dado un archivo v1, entonces abre como rectangular.
5. Dado un cálculo irregular vigente, cuando se muestran resultados o se exporta Word/PDF,
   entonces aparecen terreno natural, nivel de agua, perfil LL, reparto por franja, cierre,
   refinamiento, ecuaciones y procedencia diferenciada MTC/complementaria.
6. Dado cualquier cambio de geometría después del cálculo, cuando se edita, entonces se
   invalida el resultado anterior y se deshabilitan los reportes.
7. Dado un proyecto rectangular existente, cuando se calcula, guarda o reporta, entonces
   conserva los resultados y comportamiento verificados de v0.3.
8. Dada la entrega de escritorio desde el proyecto, cuando se ejecuta la verificación
   completa, entonces todos los módulos de producción tienen como máximo 250 líneas,
   las pruebas y análisis configurados pasan y el lanzador Python realiza una comprobación
   funcional. Esta versión no se entrega como portable.

## Points to clarify

- **suposición tomada validada** — se admite una sola rama mojada y K=1. *Base:* aprobación
  expresa de `proposals/seccion-irregular-verificada.md`. *Riesgo:* islas o exclusiones
  requieren otra definición hidráulica y quedan bloqueadas.
- **suposición tomada validada** — el lecho es homogéneo no cohesivo y el agua es clara,
  con mu una sola vez fuera de alpha. *Base:* alcance científico aprobado. *Riesgo:* no
  representa estratos, mezcla ni transporte generalizado.
- **decisión diferida** — distribución por rugosidades, varias ramas, K distinto de 1,
  estratos y mezcla; fuera de este ciclo.
- **decisión diferida** — interpolar beta, z o V; continúa prohibido por falta de regla
  publicada aprobada.

## Clarifications

- 2026-10-09 — El usuario respondió «sí» a continuar con la sección irregular después de
  revisar la propuesta técnica. Se adopta el esquema por franjas, una rama, K=1, material
  homogéneo, agua clara y mu una sola vez. La aprobación es global de autopilot.
- 2026-10-09 — El control de refinamiento es informático y debe declararse como tal; no se
  atribuye al MTC. Una diferencia superior a la tolerancia genera advertencia visible, no
  modifica coeficientes ni oculta el resultado.

## Out of scope

Se mantienen todas las exclusiones de la propuesta técnica. Un perfil que las requiera se
rechaza; no se aproxima silenciosamente para hacerlo entrar en este alcance.
