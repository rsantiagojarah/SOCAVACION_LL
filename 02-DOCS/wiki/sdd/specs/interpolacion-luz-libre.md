---
type: spec
slug: interpolacion-luz-libre
status: approved
timestamp: 2026-10-09
---
# Interpolación de luz libre para mu

## Problem & why

La tabla 13 del HHD publica mu para luces discretas. Una luz medida entre dos columnas
no puede calcularse en la versión actual, aunque el usuario exige interpolarla.

## Cost of not building it

El usuario tendría que alterar la luz medida, escoger una celda próxima o resolver mu
fuera del programa; las tres opciones pierden trazabilidad.

## The cheapest alternative

Calcular manualmente mu y anotarlo. No es suficiente porque el núcleo no admite un mu
manual y la sustitución podría separarse del proyecto y de sus memorias.

## Goals

- Admitir luces comprendidas entre las columnas extremas de la tabla 13.
- Conservar exactamente las celdas publicadas y documentar cuándo mu fue interpolado.
- Mantener una única evaluación para pantalla, gráfico y memorias.

## Non-goals / out of scope

No interpolar ni extrapolar velocidad, beta o z. No extrapolar luz fuera de10–200m.
No atribuir al MTC una regla de interpolación que no se localizó en la página107.
No cambiar ecuación59, alpha, phi, geometría ni alcance rectangular.

## Users & context

Ingeniero que conoce la luz libre medida y una velocidad perteneciente a una fila válida
de la tabla13, y necesita conservar el dato real sin ajustarlo a una columna.

## Behaviour

Con obstáculos, una L exactamente tabulada conserva su mu literal. Una L estrictamente
intermedia obtiene mu por interpolación lineal entre las dos columnas contiguas de la
misma fila de velocidad. La aplicación muestra los dos extremos, la sustitución y el
resultado. Fuera del dominio se bloquea. Sin obstáculos, mu=1 y L no participa.

## Acceptance criteria

1. Dado V=2m/s y L=27m, el resultado es mu=0.974 usando L1=25,mu1=0.97 y L2=30,mu2=0.98.
2. Todas las luces tabuladas conservan exactamente su valor publicado en cada fila.
3. L<10 o L>200 se rechaza sin extrapolar; L=10 y L=200 se admiten.
4. Las velocidades válidas permanecen `<1`, exactas1,1.5,2,2.5,3,3.5 y `>4`;
   V=4, 3.5<V<=4 y otros valores intermedios continúan bloqueados.
5. Beta y z intermedios continúan bloqueados.
6. Pantalla y Word/PDF indican que la interpolación lineal en L es un criterio aprobado
   por el usuario, no una regla publicada por el MTC, e imprimen la sustitución utilizada.
7. Proyectos JSON v1 reabren sin migración y los ejemplos con L tabulada no cambian.

## Points to clarify

- **suposición tomada** — interpolación lineal solo en el eje L y dentro de la misma fila.
  Base: confirmación expresa del usuario al ejemplo L=27m. Riesgo: el MTC no explicita
  esta regla junto a la tabla; por eso se rotula como criterio aprobado, no normativo.
- **decisión diferida** — cualquier interpolación en V, beta o z queda fuera de este ciclo.

## Aprobación

2026-10-09: el usuario respondió «SI» a la fórmula lineal mostrada y a limitarla a L.

