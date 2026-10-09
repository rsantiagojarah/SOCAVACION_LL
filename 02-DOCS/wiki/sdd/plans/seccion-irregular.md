---
type: plan
title: Plan — Sección transversal irregular
description: Plan técnico para geometría, reparto por franjas, persistencia, interfaz y memorias.
tags: [sdd, plan, lischtvan-levediev, seccion-irregular]
timestamp: 2026-10-09T00:00:00-05:00
topic: sdd
slug: seccion-irregular
status: approved in autopilot
---

# Plan — Sección transversal irregular

> Spec: [../specs/seccion-irregular.md](../specs/seccion-irregular.md) ·
> Propuesta: [../proposals/seccion-irregular-verificada.md](../proposals/seccion-irregular-verificada.md) ·
> Estado: aprobado en autopilot · Actualizado: 2026-10-09

## 0. Global Constraints

- **Método:** exclusivamente Lischtvan–Levediev para socavación general en suelos no
  cohesivos; agua clara `phi=1`; lecho homogéneo; `K=1`; una sola rama mojada.
- **Ecuación:** `alpha=Q/SUMA(h_j^(5/3)*b_j)`, `q_j=alpha*h_j^(5/3)`,
  `Q_j=q_j*b_j`, `Hs_j=[q_j/(0.68*beta*mu*phi*Dm^0.28)]^(1/(1+z))`.
- **Coeficientes:** mu se aplica una sola vez y no entra en alpha; solo mu puede
  interpolarse linealmente respecto a L entre 10 y 200 m en una fila V literal.
  No interpolar beta, z ni V y no extrapolar L.
- **Fuentes:** MTC es principal. El reparto irregular y beta/z se identifican como
  complementarios; cada valor conserva archivo y página. No modificar los PDF originales.
- **Unidades:** SI; Dm se ingresa y evalúa en mm conforme al desarrollo documentado.
- **Arquitectura:** monolito modular; ingreso, núcleo, resultados y reportes separados;
  el núcleo no importa Qt, archivos ni reportes.
- **Código:** identificadores propios en español; DRY, SOLID, KISS; cada módulo de
  producción tiene máximo 250 líneas; no se redondea dentro del cálculo.
- **Persistencia:** JSON versionado, lectura compatible de v1, guardado atómico y sin
  resultados derivados.
- **Calidad:** ejemplo manual independiente; regresión rectangular; cobertura de ramas
  del núcleo >=90%; análisis estático/tipos/dependencias y lanzador Python verificados.

## 1. Context & constraints

- Los criterios 1–3 fijan el reparto, la geometría y los errores científicos.
- Los criterios 4 y 7 exigen migración de proyecto y regresión total sin romper v0.3.
- Los criterios 5, 6 y 8 obligan a alimentar pantalla y reportes desde un solo resultado.
- La constitución sigue en borrador; rigen los requisitos explícitos del usuario que esta
  entrega ya aplicaba. No se afirma ratificación.
- Quedan fuera rugosidades, ramas múltiples, estratos, mezcla y solver hidráulico.

## 2. Architecture

```text
[Editor de perfil/UI] --> [Proyecto validado] --> [Motor LL]
        |                       |                    |
        v                       v                    v
 [Sesión/JSON v2]       [Geometría por franjas] -> [Reparto irregular puro]
                                                     |
                                                     v
                                  [Resultado único: pantalla/gráfico/reportes]
```

- **Editor de perfil** (interno) — captura pares x/cota y resolución sin calcular.
- **Modelo y validación** (interno) — representa geometría inmutable y aplica límites.
- **Geometría irregular** (interno) — recorta una rama mojada, interpola el terreno y
  produce franjas trapezoidales sin conocer LL.
- **Reparto irregular** (interno) — calcula alpha, q, Q_j y LL desde franjas formadas.
- **Motor** (interno) — selecciona coeficientes y despacha rectangular/irregular.
- **Persistencia v2** (interno) — serializa puntos y migra v1 en lectura.
- **Presentación y reportes** (interno) — consumen el resultado; nunca recalculan.

**Decisión principal:** separar geometría y ecuación LL. Así se prueba el área y la
conectividad sin coeficientes, y el ejemplo manual con franjas abstractas sin forzar una
discontinuidad topográfica inexistente.

## 3. Interfaces & contracts

```text
geometria.formar_franjas(puntos, Zw, divisiones) -> tuple[FranjaMojada, ...] | ValueError
  - x estrictamente creciente; 2..200 puntos y 2..400 divisiones internas;
    el proyecto admite 2..200 divisiones base y la malla final usa 2N.
  - conserva una sola rama de profundidad positiva.
  - añade vértices del terreno a límites uniformes para áreas trapezoidales exactas.
```

```text
irregular.evaluar_franjas(franjas, Q, Dm, beta, mu, z, Zw) -> EvaluacionIrregular | ValueError
  - alpha no contiene mu; phi=1; Q_j=q_j*b_j.
  - suma Q_j cierra Q con tolerancia relativa 1e-12.
```

```text
motor.calcular_proyecto(proyecto) -> Resultado | ValueError
  - rectangular conserva v0.3; irregular usa 2N divisiones uniformes como base final
    y añade vértices interiores, por lo que el número real de franjas puede superar 2N.
  - compara el denominador de reparto de N contra 2N; informa error relativo.
```

```text
proyectos.abrir_proyecto(ruta) -> Proyecto | ValueError | OSError
  - versión 1: exige campos v1 exactos y completa tipo rectangular/puntos vacíos.
  - versión 2: exige campos y puntos exactos; nunca ejecuta datos del archivo.
```

## 4. Data model & flow

**Entities**

- **PuntoTerreno** — `abscisa_m`, `cota_m` finitas.
- **Proyecto** — añade `tipo_seccion`, `puntos_terreno` y `numero_franjas`; mantiene
  campos rectangulares para compatibilidad.
- **FranjaMojada** — límites, centro, ancho, área, tirante medio y cota natural central.
- **PuntoResultado** — añade ancho, área, q y Q_j.
- **Resultado** — añade tipo, ancho mojado, número de franjas, cierre y error de refinamiento.

**Primary flow** (`calcular sección irregular`)

1. El formulario construye un Proyecto con perfil y N base.
2. La validación comprueba tipos, orden, alcance y datos hidráulicos.
3. El motor selecciona beta, z y mu con las reglas existentes.
4. Geometría forma mallas con base N y 2N, ambas aumentadas con vértices; el motor
   compara sus sumas `h^(5/3)*b`.
5. La malla 2N alimenta el reparto y produce un Resultado inmutable.
6. La misma instancia alimenta núcleo, tabla, gráfico y Word/PDF.

- Consistencia: la sesión invalida el resultado ante cualquier edición.
- Migración: solo lectura v1→modelo vigente; el siguiente guardado escribe v2 completo.

## 5. Testing strategy

| Criterio | Nivel | Evidencia | Dobles |
| --- | --- | --- | --- |
| #1 | unidad | constantes manuales de alpha, q, Q, Hs y Sg a 1e-9 | ninguno |
| #2 | unidad | áreas exactas, tirantes y cierre 1e-12 | ninguno |
| #3 | unidad/integración | perfiles inválidos bloqueados con mensaje | ninguno |
| #4 | integración | ida/vuelta v2 y apertura de fixture v1 | temporal real |
| #5 | integración/visual | contenido Word/PDF y series del gráfico | archivo real |
| #6 | interfaz | editar perfil invalida y deshabilita exportación | diálogos simulados |
| #7 | regresión | suite v0.3 sin cambios rectangulares | ninguno |
| #8 | sistema | verificador completo y autocomprobación del EXE | ejecutable real |

El control usa `error=abs(S_2N-S_N)/S_2N`, tolerancia `1e-3` (0.1%). Es una
decisión informática, no MTC. Si se supera, se conserva el resultado refinado y se advierte.

## 6. Sequencing & dependencies

- [x] T001 — Modelo, validación y persistencia v2 con lectura v1. Depende de: nada.
- [x] T002 — Geometría de una rama y pruebas de área/conectividad. Depende de: T001.
- [x] T003 — Reparto LL irregular, ejemplo manual y despacho del motor. Depende de: T002.
- [x] T004 — Editor y formulario condicional; invalidación de sesión. Depende de: T001.
- [x] T005 — Tabla, gráfico y memorias irregulares. Depende de: T003.
- [x] T006 — Regresión, análisis, QA visual y versión 0.4.0 desde el proyecto. Depende de: todas.

T004 puede avanzar en paralelo lógico, pero se aplicará por orden en el árbol compartido.

## 7. Risks & open decisions

| Riesgo | Disparador | Impacto | Mitigación |
| --- | --- | --- | --- |
| Interpretar dos pozas como un cauce | profundidad llega a cero dentro | reparto inválido | detectar componentes y bloquear |
| Resultado dependiente de malla | diferencia N/2N >0.1% | baja estabilidad | usar 2N, informar y pedir mayor N |
| Romper archivos v1 | esquema v2 estricto | pérdida de acceso | lector v1 + fixture de regresión |
| Reporte demasiado ancho | muchas columnas | memoria ilegible | tabla compacta y QA visual |
| Crecimiento de módulos | ramas mezcladas | superar 250 líneas | extraer editor y contenido irregular |

**Open decisions:** ninguna que cambie este ciclo. Toda ampliación científica requiere
una propuesta posterior.

## Tasks
<!-- generated by tasks on 2026-10-09; IDs are stable, do not renumber -->

| ID | [P] | Task | Done-check | Depends-on | Trace |
| --- | --- | --- | --- | --- | --- |
| T001 |  | Añadir modelo, validación y JSON v2 | `.venv/Scripts/python.exe -m unittest pruebas.test_proyectos pruebas.test_seccion_irregular.PruebasModeloPersistencia` termina en OK | — | spec §Acceptance #4, #7 |
| T002 |  | Implementar geometría mojada por franjas | `.venv/Scripts/python.exe -m unittest pruebas.test_seccion_irregular.PruebasGeometriaIrregular` termina en OK | T001 | spec §Acceptance #2, #3 |
| T003 |  | Implementar reparto LL y despacho | `.venv/Scripts/python.exe -m unittest pruebas.test_seccion_irregular.PruebasCalculoIrregular pruebas.test_calculo` termina en OK | T002 | spec §Acceptance #1, #2, #7 |
| T004 |  | Incorporar editor y formulario condicional | `.venv/Scripts/python.exe -m unittest pruebas.test_interfaz_irregular pruebas.test_interfaz_v1` termina en OK | T001, T003 | spec §Acceptance #3, #6, #7 |
| T005 |  | Presentar gráfico, tabla y memorias | `.venv/Scripts/python.exe -m unittest pruebas.test_reportes_irregular pruebas.test_reportes` termina en OK y PDF renderizado contiene todas sus páginas | T003, T004 | spec §Acceptance #5, #7 |
| T006 |  | Verificar v0.4.0 desde el proyecto | `powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/verificar.ps1` y autocomprobación del lanzador Python terminan con código 0; ningún módulo supera 250 líneas | T001–T005 | spec §Acceptance #8 |

**T002 — Interfaces**
- Consume: `PuntoTerreno(abscisa_m: float, cota_m: float)`.
- Produce: `formar_franjas(puntos, cota_agua_m, divisiones) -> tuple[FranjaMojada, ...]`.

**T003 — Interfaces**
- Consume: `FranjaMojada` con ancho, área, tirante y cota central.
- Produce: `Resultado` con puntos por franja, cierre y error de refinamiento.

**T004 — Interfaces**
- Consume y produce: `Proyecto.tipo_seccion`, `puntos_terreno`, `numero_franjas`.
- Invariante: cualquier edición emite `cambiado` e invalida el resultado vigente.

**T005 — Interfaces**
- Consume: solo `Resultado`; no llama al núcleo ni selecciona coeficientes.

## Review Workload Forecast

| Dimension | Forecast | Why |
| --- | --- | --- |
| Estimated changed lines | 700–1100 | geometría, dominio, UI, reportes y pruebas |
| Files / areas | 15–22 | modelo, cálculo, persistencia, interfaz, gráfico, memorias, QA |
| Review risk | high | cambio científico y migración de formato, aunque el alcance está acotado |
| Suggested delivery | ask-on-risk | supera el presupuesto de 400 líneas; autopilot ya autorizado, detener solo ante una bifurcación real |
