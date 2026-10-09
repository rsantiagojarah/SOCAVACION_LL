---
type: technical-basis
title: Base operativa y ejemplos manuales de v0.1
date: 2026-10-09
status: implementado-con-alcance-limitado
---

# Base operativa de v0.1

> Rectificación posterior: la tabla mu original se transcribió mal en dos celdas.
> Para V>4, L25 usa0.94 y L30 usa0.95. Véase la nota en el proceso normativo local.
> Las memorias antiguas afectadas requieren recalcularse; los ejemplos de este anexo
> tienen V=2 y no cambian. La revisión inicial no detectó este error documental.
>
> Actualización v0.3: el usuario aprobó interpolar linealmente mu solo respecto a L
> entre10 y200m. Es criterio del proyecto, no regla atribuida a la tabla13 MTC.

Actualiza el diagnóstico inicial de `proceso-calculo-normativa-local.md` para el
alcance rectangular. No cierra sus pendientes de secciones irregulares o mezclas.
El usuario solicitó buscar los coeficientes faltantes, mantener ambos MTC como
fuentes principales y posteriormente ordenó implementar la primera versión.
Los complementos se rotulan como tales: no son normativa peruana ni tablas MTC.

## Fuentes y selección

| Elemento | Procedencia verificable | Regla implementada |
| --- | --- | --- |
| Hs granular | `docs/MAN_11 HHD-2011.pdf`, p.108, ec.59 | Dm en mm; h y Hs en m |
| mu | Mismo HHD, p.107, tabla13 | Celdas y categorías exactas; 1 sin obstáculos |
| phi | Mismo HHD, pp.107–108 | Solo agua clara, phi=1; se bloquean mezclas |
| Escenarios y alcance | `docs/Manual de Puentes MTC 2018 (PGA).pdf`, §1.2.3a, impresa47/PDF51 | No confundir LL con socavación total |
| alpha | Schreider y otros (2001), ec.1, impresa16/PDF2 | Q/(B*h^(5/3)), solo sección rectangular |
| beta y z | `docs/complementarias/DGA_2022_Cachapoal_SIT527.pdf`, impresa69/PDF79, tablas7-1 y7-2, atribuidas a Mery2013 | Valores literales, sin interpolación |

La ficha `docs/complementarias/Schreider_2001_referencia.md` conserva título y URL
de la fuente consultada. No hay copia local completa de ese artículo: su descarga
directa devolvió HTTP403, aunque la ecuación se pudo verificar con la consulta web.
No se inventó un PDF ni se atribuyó esa definición de alpha a los manuales MTC.

MTC p.158 discrepa al rotular Dm en m. Se usa mm conforme al desarrollo específico
de p.108, conservando 0.68. Esta decisión aparece en pantalla y reportes.
La formulación de alpha aquí tiene unidad m^(1/3)/s y no incluye mu;
mu se aplica una sola vez en el denominador de Hs.

## Tablas complementarias

| T (años) | 2 | 5 | 10 | 20 | 50 | 100 | 500 | 1000 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| beta | 0.82 | 0.86 | 0.90 | 0.94 | 0.97 | 1.00 | 1.05 | 1.07 |

Pares literales `Dm_mm : z` (la fuente complementaria denomina X a este exponente):

```text
0.05:.43  0.15:.42  0.5:.41  1:.40    1.5:.39  2.5:.38
4:.37     6:.36     8:.35    10:.34   15:.33   20:.32
25:.31    40:.30    60:.29   90:.28   140:.27  190:.26
250:.25   310:.24   370:.23  450:.22  570:.21  750:.20
```

No sustituir z por 1/(1+z): el núcleo calcula este último por separado.
La tabla completa de mu permanece transcrita en el proceso normativo local.
Su categoría >4 no incluye 4; el intervalo 3.5<V<=4 se bloquea.
No hay selección del vecino más próximo ni entradas manuales de coeficientes.

## Procedimiento rectangular implementado

```text
1. Validar no cohesivo, homogéneo, agua clara, Q>0, B>0, V>0, T>0, Dm>0.
2. h = Zagua - Zfondo > 0; A = B*h; Vcontrol = Q/A.
3. alpha = Q/(B*h^(5/3)).
4. beta = tabla(T); z = tabla(Dm); mu = tabla(V,L), interpolada linealmente solo
   entre columnas L contiguas cuando L no es exacta, o 1 sin obstáculos; phi=1.
5. N = alpha*h^(5/3).
6. D = 0.68*beta*mu*phi*Dm^0.28.
7. e = 1/(1+z); Hs = (N/D)^e.
8. Sg = Hs-h; Z_LL = Zagua-Hs.
9. Zperfil = Zfondo-max(0,Sg), solo convención de presentación.
```

Hs mide desde el agua; Sg mide descenso del fondo. Sg<0 no prueba sedimentación.
Con geometría y material uniformes, todos los puntos tienen el mismo Hs.
La pendiente se conserva, pero no interviene en estas ecuaciones. No hay solver
hidráulico: el usuario aporta nivel de agua y velocidad del estudio hidráulico.
Si V difiere de Q/A, se advierte; no se reemplaza V automáticamente para obtener mu.
La comparación numérica usa tolerancia relativa 1e-6, decisión informática, no MTC.
Se mantienen todos los decimales internos; solo se redondea para mostrar/imprimir.

## Ejemplo manual 1: sin obstáculos

Entradas: Q=120 m³/s, B=20 m, Zfondo=100 m, Zagua=103 m, V=2 m/s,
pendiente=0.001 m/m, T=100 años, Dm=1 mm; agua clara y lecho no cohesivo homogéneo.

```text
h = 103-100 = 3 m
A = 20*3 = 60 m²; Vcontrol = 120/60 = 2 m/s
alpha = 120/(20*3^(5/3)) = 0.961499713538 m^(1/3)/s
beta = 1; z = 0.40; mu = 1; phi = 1
N = alpha*3^(5/3) = Q/B = 6
D = 0.68*1*1*1*1^0.28 = 0.68
e = 1/1.40 = 5/7
Hs = (6/0.68)^(5/7) = 4.736513861635 m
Sg = Hs-3 = 1.736513861635 m
Z_LL = 103-Hs = 98.263486138365 m
```

Control independiente: `Q/(B*Hs)` coincide con `0.68*Hs^0.4`, aproximadamente
1.266754447527 m/s. Las pruebas usan tolerancia de 1e-9 m frente al valor manual.

## Ejemplo manual 2: contracción tabulada

Se conservan las entradas anteriores; activar obstáculos y L=30 m.
Tabla13 MTC, fila V=2 y columna L=30: mu=0.98. B y L no son sinónimos;
este ejemplo es aritmético, no pretende justificar la geometría de una obra.

```text
alpha no cambia: 0.961499713538 m^(1/3)/s
D = 0.68*0.98 = 0.6664; N = 6; e = 5/7
Hs = (6/0.6664)^(5/7) = 4.805359695054269 m
Sg = 1.805359695054269 m
Z_LL = 98.194640304945731 m
```

Valores obtenidos independientemente del núcleo; segundo caso comprobado mediante
aritmética decimal de 50 dígitos y fijado como constante en `pruebas/test_calculo.py`.
No se generan valores esperados invocando la función que se está probando.

## Límites todavía abiertos

- Alpha/Be y reparto de caudales en secciones irregulares.
- Mezclas, unidad de gamma y discrepancia de phi en la fuente.
- Interpolación de beta/z y velocidades sin fila documental; mu respecto a L quedó
  resuelto por criterio explícito del usuario, no por una regla publicada del MTC.
- Estratos, varios materiales, curvas granulométricas y múltiples escenarios por proyecto.
- Validación por especialista para obra real, instalación distribuible y auditoría normativa vigente.

Todo lo anterior queda fuera de v0.1, no se considera resuelto por sus pruebas.
