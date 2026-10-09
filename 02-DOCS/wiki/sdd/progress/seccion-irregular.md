# Progreso — Sección irregular

## T001 — 2026-10-09

- status: complete
- red: `python -m unittest ...PruebasModeloPersistencia` falló por ausencia de
  `PuntoTerreno`, campos irregulares y formato v2.
- green: `python -m unittest pruebas.test_proyectos
  pruebas.test_seccion_irregular.PruebasModeloPersistencia` — 15 pruebas, OK.
- files: `dominio/modelos.py`, `dominio/validacion.py`,
  `infraestructura/proyectos.py`, pruebas de proyecto y sección irregular.
- decision: JSON v2 estricto; v1 se migra en memoria a rectangular y solo se escribe v2.
- blocker: el subagente `developer` del harness no pudo iniciar porque su modelo fijado no
  está disponible con esta cuenta; implementación local como fallback.
- skill_resolution: used `implement`; missing `.rsc/skill-registry.json` y agente developer
  ejecutable; fallback a unittest configurado y trabajo local.
- review: hallazgo Important — enteros de magnitud extrema podían escapar como
  `OverflowError`; prueba roja añadida, validador corregido y revisión final APPROVED.

## T002 — 2026-10-09

- status: complete
- red: `...PruebasGeometriaIrregular` falló porque no existía el módulo de geometría.
- green: clase T002 — 3 pruebas, OK; acumulado T001/T002/proyectos — 19 pruebas, OK.
- files: `calculo/geometria_irregular.py`, `pruebas/test_seccion_irregular.py`.
- decision: los límites de franja combinan N divisiones uniformes con cada vértice
  interior; así ninguna franja atraviesa un quiebre y el área trapezoidal es exacta.
- blocker: none.
- skill_resolution: used `implement`; missing stack skill Python específico; fallback a
  `unittest` ya calibrado en `config.yaml`.
- review: hallazgo Important por tolerancia dependiente de la abscisa absoluta y Minor
  por colapsar estaciones distintas; ambos reproducidos con pruebas rojas y corregidos.

## T003 — 2026-10-09

- status: complete
- red: `...PruebasCalculoIrregular` falló por ausencia del núcleo irregular y del
  despacho/resultados por franja.
- green: T003 + regresión rectangular — 20 pruebas, OK; acumulado técnico — 41, OK.
- files: `calculo/irregular.py`, `calculo/motor.py`, `dominio/modelos.py`, pruebas.
- decision: el resultado usa 2N; `tirante_m` global contiene hm potencial, no A/B;
  `numerador` global irregular muestra el q de la primera franja y cada punto conserva su q.
- blocker: none.
- skill_resolution: used `implement`; missing developer ejecutable; fallback local.
- review: cálculo científico aprobado; observación Minor aclarada en el plan: 2N es la
  base uniforme y los vértices añadidos pueden elevar el número real de franjas.

## T004 — 2026-10-09

- status: complete
- red: `pruebas.test_interfaz_irregular` falló al cargar los campos nuevos y por ausencia
  del selector/editor.
- green: interfaz irregular + regresión v1 — 7 pruebas, OK.
- files: `presentacion/ingreso.py`, `presentacion/seccion_irregular.py`, prueba de interfaz.
- decision: ancho/fondo/puntos rectangulares se conservan al cambiar de tipo, pero quedan
  deshabilitados en irregular; el nivel de agua sigue siendo común.
- blocker: none.
- skill_resolution: used `implement`; fallback local por developer no disponible.

## T005 — 2026-10-09

- status: complete
- red: la memoria Word irregular convertía por coincidencia parcial `alpha = Q / SUMA`
  en la ecuación rectangular; una aserción OOXML reprodujo el defecto.
- green: `python -m unittest pruebas.test_reportes_irregular pruebas.test_reportes`
  terminó en OK; la regresión específica de reportes irregulares también termina en OK.
- files: `presentacion/evaluacion.py`, `infraestructura/graficos.py`,
  `infraestructura/reportes/contenido_irregular.py`, exportadores Word/PDF y pruebas.
- decision: tabla, gráfico, Word y PDF consumen la misma instancia `Resultado`; no
  recalculan geometría, coeficientes ni LL.
- visual_qa: 5 páginas PDF y 4 páginas Word renderizadas; sin recortes, solapes,
  fórmulas rectangulares espurias ni cabeceras aisladas.
- review: APPROVED; ecuaciones, fuentes y advertencias corresponden al resultado.

## Decisión de entrega — 2026-10-09

- El usuario rechazó expresamente una distribución portable para v0.4.0.
- Se eliminó `dist/Socavacion_LL_0.4.0` y se sustituyó el done-check por la
  autocomprobación del lanzador Python desde el proyecto.
- Los portables anteriores ya existentes no se modificaron.

## T006 — 2026-10-09

- status: complete
- gate: 109 pruebas OK; ramas 141/154 = 91.5584%; Ruff, mypy, `pip check` y
  `pip-audit` en PASS; ninguna vulnerabilidad conocida.
- runtime: autocomprobación del lanzador Python terminó 0 y verificó rectangular,
  interpolación de mu, irregular, persistencia, memorias y captura.
- visual_qa: memoria v0.4.0 renderizada como PDF (5 páginas) y Word (4 páginas),
  inspeccionada sin recortes, solapes ni fórmulas incorrectas.
- constraints: mayor módulo de producción 248 líneas; manuales originales conservan
  sus hashes SHA-256 registrados en la verificación.
- delivery: sin portable v0.4.0 por instrucción expresa del usuario.
- verification: `../verifications/seccion-irregular-2026-10-09.md` — PASS.
