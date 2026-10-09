---
type: technical-proposal
date: 2026-10-09
status: pendiente-aprobacion-tecnica
---
# Propuesta técnica para sección irregular

## Evidencia nueva

El documento local `docs/complementarias/DGA_2022_Cachapoal_SIT527.pdf`,
pp.impresas68–69/PDF78–79, desarrolla franjas para LL granular. Revisión visual
realizada por investigador y raíz; imágenes en `tmp/pdfs/ampliacion/dga-078.png`
y `dga-079.png`. Esta fuente es complementaria, no norma peruana MTC.

Expresiones publicadas (se omite el índice de sección para facilitar lectura):

```text
h_j = Area_mojada_j / ancho_j
hm^(5/3) = SUMA[h_j^(5/3) * ancho_j / B]
q = K * Q / B
Hs_j^(1+z) = [q/(0.68*beta*Dm^0.28)] * (h_j/hm)^(5/3)
```

La fuente adopta K=1 cuando no excluye zonas libres de erosión o con erosión menor.
Su hm es una media de potencias: NO reemplazar por A/B en sección irregular.

## Adopción propuesta, requiere aprobación antes de código

Con K=1, derivación algebraica de la relación anterior:

```text
alpha = Q / SUMA[h_j^(5/3) * ancho_j]
q_j = alpha * h_j^(5/3)
Q_j = q_j * ancho_j
SUMA(Q_j) = Q
```

Para mantener la ecuación59 principal MTC, propuesta de combinación explícita:

```text
Hs_j = [q_j/(0.68*beta*mu*phi*Dm^0.28)]^(1/(1+z))
Sg_j = Hs_j - h_j
Z_LL_j = Zagua - Hs_j
```

Mu se aplica una sola vez y NO entra en alpha; phi=1 en la ampliación propuesta.
Beta/z y la fila V de mu mantienen selección literal. Mu puede interpolarse linealmente
solo respecto a L según la decisión v0.3 del usuario, sin atribuir esa regla al MTC.
No se atribuye la expresión
derivada de alpha a una ecuación impresa en los MTC.

## Discretización propuesta

1. Ingresar x/cota ordenadas, sin abscisas repetidas; datum común y agua horizontal conocida.
2. Representar terreno lineal entre puntos e intersectarlo con nivel de agua.
3. Mantener puntos secos en dibujo, excluirlos de ecuación. Admitir solo una rama mojada.
4. Dividir tramos mojados en franjas; calcular área exacta trapezoidal de cada franja
   y h_j=área/ancho. Evaluar el resultado en su abscisa central, no fingir valor nodal exacto.
5. Informar tamaño/número de franjas y verificar estabilidad al refinar; tolerancia
   numérica se fijará en plan y no se presentará como regla MTC.
6. Comprobar SUMA(Q_j)=Q dentro de tolerancia informática explícita.

No cubre ramas desconectadas, distribución de rugosidades, estratos, zonas excluidas
de erosión ni K distinto de1. Si aparecen, solicitar definición hidráulica independiente.
La interpolación geométrica lineal no autoriza interpolar coeficientes empíricos.

## Pendientes que NO resuelve esta propuesta

- Valores intermedios beta/z y filas V: no se localizó regla explícita de interpolación LL.
  La interpolación de mu solo en L es criterio aprobado del proyecto.
- Mezcla/phi: persiste ambigüedad de T/m³ y contradicción cerca de gamma=1.
- Granulometría desde tamices: Di debe documentarse; no se inventa marca de clase.

## Comprobación aritmética de la propuesta, no función implementada

Dos franjas de10m, tirantes2m y4m; Q=120m³/s, Dm=1mm,
beta=mu=phi=1, z=0.4. Evaluación independiente con Decimal a50 dígitos:

```text
SUMA[h_j^(5/3)*ancho_j] = 132.541705030954
alpha = 120/132.541705030954 = 0.905375405967
q_1 = 2.874387743717 m²/s; Q_1 = 28.743877437173 m³/s
q_2 = 9.125612256283 m²/s; Q_2 = 91.256122562827 m³/s
Q_1+Q_2 = 120 m³/s
Hs_1 = (2.874387743717/0.68)^(1/1.4) = 2.800069980118 m
Hs_2 = (9.125612256283/0.68)^(1/1.4) = 6.390545450233 m
Sg_1 = 0.800069980118 m; Sg_2 = 2.390545450233 m
```

Valores mostrados redondeados; no se usaron esos redondeos como entradas intermedias.
Ejemplo sintético, no calibración ni validación para un río real.

## Aprobación requerida

Aprobar el esquema por franjas anterior, K=1, una sola rama mojada, lecho homogéneo
no cohesivo y agua clara, con mu una sola vez; conservar bloqueo de interpolación y mezcla.
Esta aprobación técnica es distinta de autorizar la ruta general de implementación.
Hasta recibirla, el programa continúa calculando únicamente sección rectangular.
