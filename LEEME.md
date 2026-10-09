# Socavación LL — versión 0.5.0

Aplicación local de Windows, con el estilo de Metrados. Calcula exclusivamente
Lischtvan–Levediev para secciones rectangulares e irregulares, lecho homogéneo no
cohesivo y agua clara.
Esta versión requiere revisión del ingeniero responsable antes de usar resultados en obra.

**Corrección importante respecto a0.1:** tabla13 MTC, fila V>4 m/s: L25m usa
mu=0.94 y L30m usa mu=0.95. Se corrigió nuestra transcripción anterior0.945/0.96,
no el PDF original. Recalcular memorias anteriores que usaron esas dos celdas.
Los ejemplos publicados con V=2 m/s mantienen sus resultados.

## Abrir la interfaz

En Windows, abrir `Abrir Socavacion.cmd` con doble clic.
El lanzador utiliza exclusivamente el entorno `.venv` de este proyecto.
No inicia ni depende de Metrados, AutoCAD, Rust o una base de datos.

Si el entorno aún no está preparado, desde PowerShell en esta carpeta:

```powershell
py -3.12 -m venv .venv
& .venv/Scripts/python.exe -m pip install -e ".[pruebas]"
& .venv/Scripts/python.exe iniciar_interfaz.py
```

El primer comando crea un entorno Python local; el segundo descarga la biblioteca
gráfica y las dependencias de cálculo/reportes; el tercero abre la ventana.
La descarga inicial necesita Internet. En otro equipo, recrear `.venv`, no copiarlo.
La versión 0.5.0 se entrega para ejecutarse desde este proyecto con
`Abrir Socavacion.cmd` o con el Python de `.venv`. No se entrega como aplicación portable.

## Qué funciona

- Cabecera, barras y tema oscuro con colores y tipografía de la referencia.
- Cuatro pantallas navegables desde el panel lateral o con Alt+1 a Alt+4.
- Separador ajustable, selección de tablas y desplazamiento de los formularios.
- Formularios editables, validación y selección literal de coeficientes con fuentes.
- Cálculo en 2 a 201 puntos equidistantes, gráfico y tabla de resultados.
- Sección irregular mediante pares abscisa/cota, una rama mojada y reparto por franjas.
- Importación de una sección HEC-RAS desde `.xlsx`: lee `Ground`, permite elegir `WS`,
  registra `Bank Sta` en Notas y exige confirmar que las coordenadas están en metros.
- Los tramos verticales de HEC-RAS se conservan con abscisas iguales y cotas distintas;
  no se desplazan, redondean, reordenan ni remuestrean los puntos importados.
- Control de cierre de caudal y comparación numérica entre mallas N y 2N.
- Guardar, abrir y modificar proyectos `.ll.json` versionados, con escritura atómica.
- Word y PDF con datos, ecuaciones, sustituciones, resultados, gráfico y referencias.
- Editar cualquier dato invalida el resultado y bloquea exportaciones hasta recalcular.
- Confirmación antes de abandonar cambios; los archivos inválidos no reemplazan el trabajo.
- **Consultar tablas:** muestra beta, z y mu con fuente y página, sin modificar entradas.
- **Calcular Dm:** recibe Di representativo y porcentaje por intervalo; conserva el
  desarrollo como anexo textual en Notas, que también se guarda y aparece en memorias.
- Ayuda junto a luz libre y notas multilínea. Al marcar sin obstáculos, una L inválida
  se restaura a0 con aviso visible; valores válidos se conservan y no participan en mu.
- Con obstáculos, mu se interpola linealmente respecto a L entre columnas contiguas
  de la tabla13. La memoria conserva extremos, sustitución y advertencia de procedencia.

Para probar: pulsar **Ejemplo**, después **Calcular** (F5), revisar resultados y exportar.
El ejemplo entrega `Hs=4.736513861635 m` y `Sg=1.736513861635 m`.
Es una comprobación aritmética, no un proyecto real. Las memorias no necesitan Word
instalado para generarse; Word se utilizó únicamente para comprobar su apariencia.

Atajos: Ctrl+N nuevo, Ctrl+O abrir, Ctrl+S guardar, Ctrl+Shift+S guardar como y F5 calcular.

Para importar HEC-RAS: seleccione **Irregular por franjas**, abra **Editar perfil
irregular**, pulse **Importar HEC-RAS XLSX…**, elija el perfil `WS`, confirme metros
y acepte primero el resumen y después el editor de la sección.

## Restricciones de esta versión

Una sección y un escenario por archivo. La geometría irregular admite una sola rama
mojada, terreno lineal por tramos, lecho homogéneo y K=1. No admite varias ramas,
estratos, cohesivos, flujo de detritos, mezcla agua-sedimento ni socavación local. El resultado
no es socavación total ni determina la cimentación. Con mu, incluye esa corrección
por contracción; no sumar una segunda contracción. Los puntos tienen igual tirante
y material: no representan una topografía irregular.

Longitudes en m, caudal en m³/s, velocidad en m/s y pendiente en m/m. Dm se ingresa
en mm, submúltiplo SI requerido por la ecuación empírica. No equivale a D50.
Se ingresa Dm documentado o se calcula desde Di y porcentajes documentados.
No se infieren marcas de clase desde aberturas de tamiz ni se usan porcentajes acumulados.
Las fracciones deben sumar100% (tolerancia informática1e-8 puntos porcentuales);
no se normalizan. La herramienta admite1 a100 fracciones y exige fuente del ensayo.
El anexo textual se conserva, pero no reconstruye automáticamente las filas al reabrir
la calculadora; todavía no es un gestor estructurado de muestras.
Un Dm calculado no tabulado conserva su valor y bloquea LL: no se aproxima para obtener z.
El tirante deriva de las cotas; la pendiente no resuelve el nivel de agua.
Usar un mismo datum vertical para fondo/agua y registrarlo en Notas.

T admite exactamente `2, 5, 10, 20, 50, 100, 500, 1000` años.
Dm admite exactamente (mm):
`0.05, 0.15, 0.5, 1, 1.5, 2.5, 4, 6, 8, 10, 15, 20, 25, 40, 60, 90, 140, 190, 250, 310, 370, 450, 570, 750`.

Sin obstáculos, mu=1. Con obstáculos, L admite cualquier valor entre10 y200m.
Las columnas publicadas son
`10, 13, 16, 18, 21, 25, 30, 42, 52, 63, 106, 124, 200` m;
entre ellas se interpola mu linealmente dentro de la misma fila de V. Esta regla fue
aprobada expresamente por el usuario; no está publicada junto a la tabla MTC.
Filas de velocidad: `0<V<1`, valores exactos `1, 1.5, 2, 2.5, 3, 3.5`, o `V>4` m/s.
No se interpola V, beta ni z; no se extrapola L. `3.5<V<=4` y otras filas no
tabuladas se bloquean. No alterar datos medidos para forzar una celda.

Sg negativa se conserva, sin interpretarla como sedimentación, y se distingue del
perfil limitado al terreno natural. Los límites se imprimen también en las memorias.

MTC 2011 y 2018 son las fuentes principales, intactas en `docs/`. Alpha/beta/z tienen
respaldo complementario identificado; sus tablas no se atribuyen al MTC.
Véase [base técnica y ejemplos manuales](02-DOCS/wiki/sdd/proposals/base-calculo-v01.md).

## Verificación

Desde la raíz, ejecutar las pruebas de interfaz sin abrir ventanas visibles:

```powershell
& .venv/Scripts/python.exe -m unittest discover -s pruebas -v
```

Las pruebas comprueban ejemplos aritméticos, tablas y límites, persistencia,
invalidación, memorias, navegación, paleta y máximo de 250 líneas por módulo.
La evidencia está en `02-DOCS/wiki/sdd/verifications/`. No sustituyen la validación
profesional del modelo hidráulico para una obra real.

Para repetir análisis, tipos de núcleo/dominio, cobertura de ramas y auditoría:

```powershell
& .venv/Scripts/python.exe -m pip install -e ".[desarrollo]"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/verificar.ps1
```

El primer comando instala herramientas de desarrollo. El segundo ejecuta los controles
y falla si falta una herramienta, una prueba no pasa o la auditoría no se puede completar.
La excepción de ejecución se limita a ese proceso; no cambia la política permanente de Windows.
La auditoría necesita Internet; los cálculos y proyectos ordinarios no.
Los registros quedan en `tmp/calidad/`. El umbral de ramas es90%, no un criterio MTC.

La opción `--comprobar-instalacion DIRECTORIO` del lanzador Python crea una subcarpeta única
con ejemplo, memorias, captura e informe JSON. Comprueba funcionamiento local sin tocar
proyectos existentes; no acredita revisión hidráulica ni prueba en Windows limpio.

Pendientes de la ruta completa: varias ramas mojadas, estratos y rugosidades distribuidas,
reglas documentadas para interpolar V/beta/z, mezclas, gestor de escenarios/muestras, recuperación de
borradores e instalador. No se declaran implementados por esta actualización.

## Organización

Monolito modular: `dominio/` define datos y validaciones; `calculo/` contiene LL puro;
`aplicacion/` gestiona sesión; `presentacion/` conecta las cuatro fases;
`infraestructura/` conserva proyectos y genera gráficos/memorias.
DRY: un Resultado alimenta pantalla y reportes. SOLID: responsabilidades separadas.
KISS: archivos JSON sin servidor ni base de datos. Identificadores propios en español;
los nombres de extensión exigidos por Qt, como `paintEvent`, conservan su API.
No se han incorporado ecuaciones a las clases de interfaz.

## Procedencia visual

Adaptación autorizada por el usuario de `Metrados_rj/app/metrado/theme.py` y
`chrome.py`, cuya cabecera atribuye la paleta original a Gitbin.
Se mantiene esa atribución; los archivos fuente de Metrados no se modifican.
