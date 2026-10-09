---
type: spec
slug: granulometria-documentada
status: approved in autopilot
timestamp: 2026-10-09
---
# Granulometría documentada — parte de B
## Problem & why
Actualmente Dm solo se introduce como número; el usuario necesita obtenerlo desde
fracciones documentadas usando la ecuación52 ya propuesta del MTC.
## Cost of not building it
Se mantiene una operación manual fuera de la aplicación y sin sustitución conservada.
## The cheapest alternative
Calcular fuera y pegar en Notas; exige duplicar transcripción y comprobaciones.
## Goals
Calcular Dm desde Di y porcentaje de cada fracción, con procedencia y cálculo conservados.
## Non-goals / out of scope
No inferir marcas de clase desde tamices, no porcentajes acumulados, no interpolar z.
Gestión de muestras estructuradas y escenarios múltiples quedan pendientes de B.
## Users & context
Ingeniero con resultados de ensayo que documentan diámetro representativo de cada intervalo.
## Behaviour
Herramienta de fracciones con fuente obligatoria, filas editables y vista del Dm obtenido.
Aceptar aplica Dm y anexa fracciones/fuente/ecuación a Notas; cancelar no cambia nada.
Si Dm no está tabulado, advierte que calcular Dm no habilita LL. Nunca redondea para
forzar una celda ni normaliza una suma incompleta. El anexo se conserva en JSON y memorias.
## Acceptance criteria
1. [(0.2,20),(0.6,50),(1,30)] da0.64mm; [(0.5,50),(1.5,50)] da1mm.
2. Rechaza vacíos, no finitos, Di<=0, porcentajes<0/>100 y suma distinta de100
   con tolerancia informática absoluta1e-8 puntos porcentuales, sin normalizar.
3. Cancelar no altera Dm/notas; aceptar actualiza ambos e invalida evaluación.
4. Fuente y fracciones sobreviven a guardar/reabrir y aparecen en notas de reportes.
5. Dm=.64 permanece.64 y LL sigue bloqueado por z, sin sustituir por valor tabulado.
6. Anexo que supera límite de Notas se rechaza sin modificación parcial ni pérdida.
## Points to clarify
- **suposición tomada**: anexo textual usa Notas existente para mantener compatibilidad v1;
  no se presenta como gestor estructurado de muestras ni permite recuperar automáticamente filas.
- **decisión diferida**: persistencia estructurada de fracciones y escenarios requiere migración posterior.
## Clarifications
HHDp92 ecuación52 revisada visualmente por raíz e investigador. Di es dato documentado,
no diámetro inferido. Fórmula ya estaba en propuesta original; no nueva relación científica.
