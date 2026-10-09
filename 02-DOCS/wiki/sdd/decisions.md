# Decisiones del proyecto

## 2026-10-09 — Implementación local de v0.1, posterior a las decisiones iniciales

- Autorización: el usuario pidió buscar las reglas faltantes, mantener MTC como
  fuente principal, copiar el estilo de Metrados y finalmente «SI IMPLEMENTA LA PRIMERA VERSION».
- Se implementa el alcance rectangular propuesto, no una solución general de secciones irregulares.
- Se identifican expresamente alpha de Schreider2001 y beta/z de DGA/MOP2022 como
  complementos; MTC conserva precedencia para ecuación, mu, agua clara y alcance.
  El anexo `proposals/base-calculo-v01.md` delimita esta actualización documental.
- Decisión histórica v0.1: selección literal sin interpolación, agua clara phi=1,
  un material homogéneo y exclusión de cohesivos, estratos, detritos, socavación local
  y diseño de cimentaciones. La parte de mu respecto a L fue sustituida expresamente
  por la decisión v0.3 registrada abajo.
- JSON versionado frente a base de datos: monolito local simple, guardado atómico y
  resultados derivados no persistidos. Un Resultado compartido evita recalcular en reportes.
- Interfaz adaptada sin modificar Metrados. No hay Git; no se crean ramas ni commits.
- Los documentos Word usan ecuaciones nativas; PDF usa expresiones lineales legibles.
  Son dos representaciones del mismo resultado, no dos motores de cálculo.
- Entrega mediante Python local y lanzador CMD; instalador distribuible queda pendiente.
- La constitución generada por el harness sigue siendo borrador: no se afirma una
  ratificación formal inexistente. Los requisitos explícitos del usuario rigen esta entrega.

## 2026-10-09 — Normativas locales como base del proceso

- Instrucción del usuario: basar el proceso de cálculo en los documentos de `docs/`.
- Fuentes examinadas: HHD 2011 y Manual de Puentes 2018. Se conserva su contenido original.
- Decisión: usar HHD para la ecuación LL granular y PUENTES para escenarios y alcance del estudio. El detalle se conserva en [proceso-calculo-normativa-local.md](proposals/proceso-calculo-normativa-local.md).
- Alternativa descartada: tratar la formulación previa y sus coeficientes ilustrativos como normativamente verificados sin cotejar los PDF.
- Pendientes: definición de α/Be, tablas β/z y resolución de ambigüedades de μ/φ. No se declara validación técnica completa ni aprobación para programar.
- Requisitos vigentes: monolito modular, ingreso/cálculo/presentación/reportes, DRY/SOLID/KISS, español y módulos de producción de máximo 250 líneas.

## 2026-10-09 — Coeficientes exactamente conforme a docs

- Instrucción explícita posterior: «LOS COEFICIENTES DEBEN TOMARSE COMO SE ENCUENTRA EN LA DOCUMENTACION» de la carpeta `docs`.
- Decisión obligatoria: preservar valores, decimales, fórmulas, unidades y condiciones publicadas; registrar archivo y página. No incorporar coeficientes externos ni supuestos.
- Se retiran la propuesta de interpolación bilineal de μ y el ejemplo con β/z sin respaldo local. Una justificación manual no reemplaza una fuente en docs.
- φ conserva literalmente la ecuación impresa; su discrepancia con el texto φ≥1 se informa, sin recortar ni corregir el valor calculado.
- Un parámetro indispensable no localizado sigue pendiente y no habilita un resultado completo. La revisión anterior no prueba que todos los coeficientes estén disponibles.
- Esta decisión sustituye las propuestas previas de completar coeficientes mediante bibliografía externa o criterios propios; no autoriza comenzar la programación.

## 2026-10-09 — Reparación de las rutas de hooks de Codex

- Síntoma: avisos repetidos «Hook failed / hook exited with code 1».
- Reproducción: el comando Windows del hook Stop terminó con código 1. Git informó que la carpeta no es un repositorio; `.Trim()` recibió null y Node buscó erróneamente `C:\.rsc\session-memory-adapter.mjs`.
- Corrección: en `.codex/hooks.json`, los campos `command` y `commandWindows` de los diez manejadores usan las rutas absolutas de los scripts existentes en este proyecto. Se preservaron eventos, filtros, tiempos y límites de contexto. No se inicializó Git ni se desactivaron hooks.
- Copia previa: `.rsc/backups/hooks-codex-antes-reparacion-20261009.json`.
- Verificación: diez comandos Windows ejecutados con entradas JSON de prueba; todos devolvieron código 0 y objetos JSON válidos, en 0.17–0.39 segundos. La prueba de SessionStart/actualizaciones usó `RSC_NO_UPDATE_CHECK=1` solo en el proceso de prueba, evitando instalaciones; se verificó su invocación, no la consulta remota de versiones.
- Restricción del diagnóstico: el entorno restringido impedía a Node resolver rutas (EPERM); la verificación final se ejecutó con permiso fuera de ese entorno.
- Estado: comandos reparados y probados; carga de la nueva configuración en la sesión de la aplicación pendiente de observación. Puede requerir recargar/reabrir el proyecto y revisar la confianza de los hooks si la aplicación lo solicita.
- Mantenimiento: las rutas corresponden a la ubicación actual. Si se mueve la carpeta o una actualización RSC regenera los hooks, revisar las rutas y repetir la comprobación.

## 2026-10-09 — Solicitud de completar el programa

- El usuario solicita implementar lo faltante después de consultar el bloqueo de luz libre.
- Se revisan formulario, modelo, núcleo y pendientes de la verificación v0.1.
- Se propone completar por entregas, frente a limitarse a usabilidad o conservar v0.1.
  Motivo: ampliar geometría, coeficientes y mezcla afecta hipótesis aún no aprobadas.
- Propuesta: `proposals/completar-programa.md`; reglas generales completadas en
  `constitution.md`, manteniendo status draft. No se afirma ratificación ni aprobación.
- SDD/specify exige aprobación antes de implementar esta ampliación. No se cambian
  código, coeficientes, dependencias ni PDFs en esta etapa; falta elegir modo de ejecución.

## 2026-10-09 — Ruta aprobada y rectificación de mu

- Usuario responde «SI» a aprobar la ruta y ejecución automática; se registra
  consentimiento global, no aprobación individual de fórmulas nuevas.
- Partición: A ingreso/UI; F herramientas/tipos; E parcial distribución a cargo raíz.
  B parcial agrega herramienta Dm con anexo en Notas y conserva formato de proyecto.
- Error reproducido: obtener_mu(False,4.1,25) devolvía0.945; paraL30 devolvía0.96.
  La nueva revisión de HHD107 tabla13 a400dpi muestra0.94 y0.95 respectivamente.

## 2026-10-09 — Interpolación de mu respecto a luz libre

- Contexto: el usuario indicó que la luz libre debe interpolarse y aprobó expresamente
  la fórmula lineal mostrada para L=27m entre25m y30m.
- Opciones: conservar solo celdas; vecino más próximo; interpolación lineal en L.
- Decisión: interpolar linealmente mu únicamente en L, dentro de10–200m y en una fila
  de V ya válida. No interpolar V, beta o z ni extrapolar L.
- Razón: conserva la luz medida y los valores extremos publicados. La tabla MTC p.107
  no explicita esta regla; pantalla y memorias deben identificarla como criterio del usuario.

## 2026-10-09 — bug: lienzo anterior visible al recalcular  (feature: interpolacion-luz-libre)

- Repro: autocomprobación del EXE calculó el ejemplo literal y luego L=27m antes de
  mostrar la ventana; la captura exhibió el lienzo anterior superpuesto.
- Causa: `removeWidget` y `deleteLater` retiraban el lienzo del layout, pero seguía
  visible y emparentado hasta que Qt procesara el borrado diferido.
- Fix: ocultar y desvincular el lienzo antes de limpiarlo/borrarlo; prueba de regresión
  exige que el padre sea `None` antes de insertar el nuevo.
- Por qué pasó: las pruebas previas comprobaban datos del gráfico, no dos renders consecutivos.
- Causa: transcripción inicial equivocada, repetida en pruebas; no errata de la fuente.
  Corrección mínima: dos celdas, nueva prueba independiente de fila completa y
  expectativas antiguas rectificadas explícitamente. No se amplían tolerancias.
- El usuario fue informado en chat. Proyectos afectados requieren recalcular sus
  memorias; el programa no guarda resultados como verdad en JSON.
- Irregular: DGA local pp68–69 contiene esquema por franjas con media de potencias;
  su adopción/discretización se propondrá aparte. No se sustituye hm por A/B.
- Interpolación/phi: investigación no cierra reglas/unidades. Continúan bloqueadas.

## 2026-10-09 — Sección irregular por franjas aprobada

- El usuario respondió «sí» a continuar después de revisar
  `proposals/seccion-irregular-verificada.md`; se registra aprobación técnica y autopilot.
- Se adopta una sola rama mojada, K=1, lecho homogéneo no cohesivo, agua clara y mu
  aplicado una sola vez fuera de alpha. No se amplían beta, z, V, phi ni el método.
- El perfil es lineal entre puntos. Las áreas de franja son trapezoidales exactas y los
  vértices del terreno se incorporan como límites de discretización.
- El resultado usa la malla 2N y compara `SUMA(h^(5/3)*b)` contra N. La tolerancia
  relativa 1e-3 es un diagnóstico numérico del programa, no una disposición MTC.
- JSON avanza a v2 con lectura compatible de v1. El núcleo seguirá separado de Qt,
  persistencia y reportes; ningún módulo de producción puede superar 250 líneas.
## 2026-10-09 — v0.4.0 se ejecuta desde el proyecto (feature: seccion-irregular)

El usuario indicó expresamente que no desea una versión portable. La entrega 0.4.0 se
ejecuta con `Abrir Socavacion.cmd` o `.venv/Scripts/python.exe iniciar_interfaz.py`.
Se eliminó solo la carpeta portable 0.4.0 recién generada; los artefactos anteriores
permanecen intactos hasta recibir una orden explícita.

## 2026-10-09 — Tramo vertical observado en XLSX HEC-RAS

- La inspección completa detectó dos puntos `Ground` consecutivos con x
  `23.3999996185303` y cotas `2511.32006835938` y `2511.28002929688`.
- La regla propuesta de rechazar toda x repetida habría impedido importar el archivo
  suministrado. Se corrige esa premisa con evidencia del propio archivo.
- Decisión: admitir x iguales solo como tramo vertical con cotas distintas. Se conserva
  el orden y cada valor; no se desplaza, redondea, interpola ni remuestrea el terreno.
- La integración trapezoidal usa el límite izquierdo y derecho correspondiente a cada
  lado del tramo vertical, cuya anchura y área horizontal son cero. No cambia la ecuación
  Lischtvan–Levediev ni sus coeficientes.
