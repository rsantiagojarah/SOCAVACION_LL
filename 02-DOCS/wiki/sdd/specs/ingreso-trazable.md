---
type: spec
slug: ingreso-trazable
status: approved in autopilot
timestamp: 2026-10-09
---
# Ingreso trazable — entrega A

## Problem & why
El bloqueo de luz libre no explica su causa cerca del campo; los usuarios no pueden
consultar las celdas que restringen sus entradas sin salir del flujo de trabajo.
## Cost of not building it
Persisten confusión y riesgo de modificar datos medidos para hacerlos coincidir con una tabla.
## The cheapest alternative
Explicar la casilla en el manual ayuda, pero no acompaña al usuario durante el ingreso.
## Goals
Explicar obstáculos/L, consultar valores y fuentes, mejorar origen de datos sin cambiar LL.
## Non-goals / out of scope
No interpolar, no modificar coeficientes, no cambiar JSON ni añadir nueva geometría.
Datum/origen se registran en Notas existentes durante esta entrega; campos estructurados
se reservan a la migración posterior. No declarar ese pendiente completado.
## Users & context
Ingeniero que ingresa datos hidráulicos y necesita saber por qué un cálculo no es admisible.
## Behaviour
La casilla de obstáculos queda junto a L, con explicación visible en ambos estados.
Cambiar estado conserva L y mantiene invalidación. Un botón permite consultar tablas
beta/z/mu y sus fuentes en lectura; consultar/cerrar no altera proyecto ni coeficientes.
Las notas admiten edición multilínea y recuerdan registrar datum/origen de los datos.
Excepción explícita: al marcar sin obstáculos con L vacía, no numérica, no finita o
negativa, restablecer0 y avisarlo junto al campo; impide bloquear cálculo por un campo
que acaba de quedar deshabilitado. No sustituir valores válidos ni hacerlo al calcular.
## Acceptance criteria
1. Al marcar sin obstáculos, L se deshabilita y se explica mu=1 y L no utilizado.
2. Al desmarcar, L se habilita y conserva valor. Actualización v0.3: mu interpola
   linealmente L dentro de10–200m; V sigue requiriendo fila publicada.
3. Consultar tablas muestra todos los valores actuales y fuente/página, sin edición ni aplicación implícita.
4. Notas multilínea sobreviven a formulario, guardar y abrir sin pérdida de saltos.
5. Cambiar estado o notas invalida evaluación/exportación; abrir tabla no las invalida.
6. Se conservan los ejemplos LL, archivos v1 y módulos <=250 líneas.
## Points to clarify
- **suposición tomada**: conservar el valor L deshabilitado evita perder trabajo; no participa en mu.
- **decisión diferida**: nuevos campos estructurados pertenecen a la migración de proyectos.
## Clarifications
2026-10-09: se validan internamente las dos entradas; ninguna cambia alcance científico.
Aprobación global «SI» de la ruta de completar programa; no aprobación ítem por ítem.
