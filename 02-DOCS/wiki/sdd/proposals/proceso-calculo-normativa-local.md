---
title: Proceso de cálculo sustentado en los manuales locales del MTC
status: base-principal-con-anexo-v01-y-pendientes-fuera-de-alcance
date: 2026-10-09
---

# Proceso de cálculo sustentado en los manuales locales del MTC

> Actualización de implementación: el diagnóstico inicial de faltantes se conserva
> como trazabilidad. La [base operativa v0.1](base-calculo-v01.md) documenta las fuentes
> complementarias verificadas después, las tablas beta/z, alpha rectangular y los
> ejemplos implementados. Prevalece para ese alcance limitado. Los faltantes no se
> atribuyen al MTC ni se consideran resueltos para secciones irregulares o mezclas.

## 1. Fuentes y alcance

Por instrucción del usuario, los documentos de `docs/` son la base documental del proceso. Este documento precisa y corrige la base técnica de la [propuesta del software](software-socavacion-lischtvan-levediev.md). No autoriza programación ni declara validado el modelo completo.

| ID | Archivo local | Uso en el software | Paginación |
| --- | --- | --- | --- |
| HHD | [MAN_11 HHD-2011.pdf](../../../../docs/MAN_11%20HHD-2011.pdf) | Granulometría y formulación Lischtvan–Levediev | 222 páginas; las páginas citadas coinciden con el contador PDF |
| PUENTES | [Manual de Puentes MTC 2018 (PGA).pdf](../../../../docs/Manual%20de%20Puentes%20MTC%202018%20%28PGA%29.pdf) | Escenarios, antecedentes y alcance del estudio de puentes | 634 páginas; página impresa 47 = página PDF 51 |

Copias identificadas mediante SHA-256 (huella que permite detectar cambios del archivo):

- HHD: `0a1bdcd7c94016760642de91baf4d6e317e4cc85c529dfefae9a6bf76c8dcd88`.
- PUENTES: `46d37849141b3acef44bdae112496dafbb5d6813dc008d5495c2f2bb760936b1`.

Los originales se conservan intactos. La consulta web se limitó a corroborar su marco de aprobación: [RD 20-2011-MTC/14](https://www.gob.pe/institucion/mtc/normas-legales/4443017-20-2011-mtc-14) y [aprobación del Manual de Puentes 2018](https://busquedas.elperuano.pe/dispositivo/NL/1730970-1). Las ecuaciones y tablas de este documento se leyeron en los archivos locales, no en resúmenes web. Esta revisión no constituye una auditoría exhaustiva de modificaciones normativas posteriores.

**Alcance confirmado por el usuario:** Lischtvan–Levediev, suelos no cohesivos, Python de escritorio para Windows, SI, cuatro fases funcionales, monolito modular, DRY/SOLID/KISS, identificadores en español y archivos de producción de máximo 250 líneas.

### Regla obligatoria de coeficientes — precisión del usuario, 2026-10-09

La regla siguiente refleja el estado anterior a la búsqueda posterior solicitada.
Para v0.1 solo se amplía mediante los complementos identificados en el anexo citado;
se mantiene la prohibición de inventar, interpolar, extrapolar o corregir coeficientes.

Los coeficientes se tomarán exclusivamente de la documentación presente en `docs/`, tal como están publicados: valores, decimales, ecuaciones, unidades y condiciones de aplicación. Cada selección deberá identificar archivo, página y tabla/ecuación.

No se introducirán coeficientes externos, valores supuestos, ajustes de curvas, redondeos previos al cálculo, correcciones de presuntas erratas ni interpolaciones/extrapolaciones que la documentación no establezca. Las conversiones de unidades deben ser explícitas y conservar la equivalencia de la ecuación, sin alterar sus coeficientes empíricos.

**Excepción posterior aprobada, v0.3:** el usuario ordenó interpolar la luz libre y
aprobó la interpolación lineal de mu únicamente respecto a L, entre columnas contiguas
de la tabla13 y dentro de10–200m. Esta es una convención del proyecto: la p.107 no
publica una regla de interpolación. No autoriza interpolar V, beta o z ni extrapolar L.
Las celdas originales continúan intactas y toda salida debe mostrar los dos extremos.

Si un coeficiente o regla no se localiza, se registrará «no localizado en docs»; no se completará con bibliografía externa ni con un valor manual sin respaldo local. Si es imprescindible, el cálculo afectado permanecerá sin resultado hasta contar con la referencia local. Las discrepancias se mostrarán sin modificar silenciosamente las expresiones publicadas. Esta regla sustituye las propuestas anteriores de completar coeficientes con otras fuentes o interpolaciones elegidas por el desarrollador.

## 2. Qué demuestra cada manual

| Tema | Ubicación exacta | Consecuencia para el proceso |
| --- | --- | --- |
| Muestreo y diámetro medio | HHD §4.1.1.5.2 a.3, pp. 91–92, ec. 52 | Registrar muestras, fracciones y procedencia de Dm |
| Escenarios de avenida | HHD pp. 92–93; PUENTES §1.2.3a, impresa 47 / PDF 51 | Guardar cada escenario con su propio caudal y estado hidráulico |
| Hipótesis del método | HHD §4.1.1.5.4 b.2.2, pp. 105–106, figura 07 | Cálculo por franjas; caudal unitario conservado durante la erosión |
| Ecuación granular básica | HHD p. 106, ec. 58 | Caso sin correcciones de contracción ni mezcla |
| Contracción | HHD p. 107, tabla 13 | μ depende de velocidad y luz libre; μ=1 sin obstáculos |
| Mezcla agua–sedimento | HHD pp. 107–108 | φ depende de la condición de transporte y peso específico de mezcla |
| Ecuación granular corregida | HHD p. 108, ec. 59 | Modelo único del núcleo; μ aparece una sola vez |
| Alcance del resultado LL | HHD p. 158, tabla 29 | Con μ, incluye contracción por efecto del puente |
| Socavación total del puente | PUENTES §1.2.3a, impresa 47 / PDF 51 | La socavación local sigue fuera del programa; no denominar total al resultado LL |
| Datos y memoria | PUENTES §§1.2.2–1.2.6, impresas 45–49 / PDF 49–53 | Trazar hidráulica, granulometría, escenarios, resultados y limitaciones |

## 3. Fase de ingreso de datos

### 3.1 Proyecto y escenarios

Guardar nombre, ubicación, responsable, sección, datum vertical, fuente topográfica, material no cohesivo y antecedentes hidráulicos. En torrenteras, documentar si se trata de flujo de agua con sedimentos: la sola denominación «torrentera» no demuestra aplicabilidad a un flujo de detritos.

Para puentes, PUENTES §1.2.3a diferencia:

1. Diseño para socavación: salvo criterio diferente del propietario, la condición más severa entre la avenida de 100 años y un desbordamiento de menor período que resulte más severo.
2. Verificación para socavación: una avenida de período no mayor de 500 años o un desbordamiento de menor recurrencia, según la evaluación correspondiente.

No imponer siempre 100/500 años como pareja automática. Registrar el criterio de selección. El programa compara la componente LL de cada escenario; no verifica estabilidad de cimentaciones ni selecciona por sí solo el evento que gobierna la socavación total.

### 3.2 Hidráulica y geometría

| Entrada | Unidad | Tratamiento propuesto |
| --- | --- | --- |
| Caudal Qd y período T | m³/s; años identificados en la ficha hidrológica | Procedentes del estudio hidrológico |
| Abscisas xᵢ y cotas del fondo Zᵢ | m | Sección ordenada y referida a un datum común |
| Cota de agua Zw | m | Por escenario, procedente del estudio hidráulico |
| Velocidad media V | m/s | Control Qd/A y consulta de μ; no es solo informativa |
| Pendiente del cauce y, si disponible, de energía | m/m | Campos diferenciados, con origen documentado |
| Luz libre L | m | Entre estribos en una luz; mínimo claro entre apoyos contiguos en varias luces |
| Condición sin/con obstáculos | categoría | Determina si se usa μ=1 o la tabla 13 |
| Peso específico de mezcla γm | kN/m³ | Solo cuando corresponde la corrección por mezcla |

La primera versión recibe el nivel de agua del estudio hidráulico. No incorpora implícitamente un solver hidráulico ni otro método de socavación. El tirante local se deriva de las cotas: `hᵢ = Zw − Zᵢ`. Si también se ingresa un tirante, debe identificarse su punto de referencia y verificarse contra estas cotas.

Validaciones propuestas: números finitos, Qd>0, puntos suficientes, abscisas estrictamente crecientes, área mojada positiva, unidades explícitas y datum consistente. Recortar segmentos en su intersección con Zw antes de integrar el área; no integrar por encima del agua. Los puntos secos se conservan en el dibujo y quedan fuera de la ecuación LL.

Para varias ramas mojadas o distribuciones hidráulicas heterogéneas, exigir delimitación y criterio de reparto del caudal. No repartir Qd entre ramas por mera igualdad de anchos. Esta política es una decisión de implementación pendiente de cierre técnico.

### 3.3 Granulometría

HHD, ecuación 52, p. 92:

`Dm = Σ(Dⱼ · Δpⱼ) / 100`

Usar el diámetro representativo/marca de clase Dⱼ y el porcentaje en peso de cada intervalo Δpⱼ. No usar porcentajes acumulados directamente como pesos. Documentar la elección de las marcas de clase y comprobar que las fracciones sumen 100% dentro de una tolerancia declarada; no normalizar silenciosamente una muestra incompleta.

Permitir Dm medido/documentado o calculado desde fracciones. Dm y D50 son magnitudes diferentes: HHD p. 91 menciona ambas opciones de caracterización, pero el software no las intercambiará automáticamente. La determinación de comportamiento no cohesivo requiere información geotécnica; Dm por sí solo no la prueba.

PUENTES §1.2.2a (impresa 46 / PDF 50) sitúa muestras en dos puntos cercanos a apoyos, B aguas arriba y 0.5B aguas abajo; HHD p. 91 menciona ambos puntos adicionales aguas arriba. También difieren las indicaciones de profundidad. Registrar la diferencia y proponer PUENTES 2018 como referencia específica del plan de muestreo de puentes, con justificación del responsable; no mezclar ambas instrucciones como si fueran idénticas.

## 4. Fase del núcleo de cálculo

### 4.1 Geometría hidráulica derivada

Propuesta de discretización, no transcripción de una ecuación MTC: interpolar linealmente entre puntos de la sección, integrar el área mojada A y obtener el ancho mojado B. Para una sección simple, el tirante medio geométrico es `Hm=A/B` y la velocidad de control es `Vcontrol=Qd/A`.

No tratar ancho mojado, ancho estable, ancho efectivo y luz libre como sinónimos. La convención exacta de Be utilizada para determinar α debe quedar resuelta antes de programar ese cálculo.

### 4.2 Coeficiente hidráulico α: diagnóstico inicial; irregular sigue pendiente

La propuesta anterior incluía una fórmula para α que no quedó respaldada por una ubicación verificable en los manuales entregados. Se retira del proceso adoptable. No se identificó allí su desarrollo operativo para una sección irregular ni una definición suficiente de Be.

Para cerrar este punto se requiere localizar la definición en `docs` y comprobar su relación con el reparto del caudal por franjas, incluido el cierre `Σ(qᵢ·Δbᵢ)≈Qd`. Una equivalencia demostrada para una sección rectangular no basta para una sección irregular. No sustituir la definición por una normalización propia.

Si se emplea la ecuación 59, μ no puede incorporarse de nuevo dentro de α. Esta restricción evita aplicar dos veces la corrección de contracción. El α de la ecuación de energía de HHD p. 100 es otro coeficiente y no debe reutilizarse como α de LL.

### 4.3 Coeficientes de frecuencia β y exponente z

Actualización: las tablas complementarias de DGA/MOP2022 están en docs/complementarias
y en el anexo v0.1. Las siguientes observaciones se refieren a los dos manuales MTC.

HHD p. 108 identifica β como coeficiente de frecuencia y usa z en el exponente. No se localizaron tablas/relaciones operativas completas para β(T) y z(Dm) en el material revisado. El Manual de Puentes tampoco aportó una formulación LL complementaria identificable mediante búsqueda textual.

No cargar valores por defecto ni ajustar polinomios de memoria. HHD p. 215 cita bibliografía, pero esa cita no aporta por sí sola los valores faltantes ni autoriza a incorporarlos desde fuera de `docs`. Estado: β(T) y z(Dm) no localizados como reglas operativas completas en los archivos revisados; su automatización queda pendiente de referencia local verificable.

### 4.4 Contracción μ: tabla verificada visualmente

Transcripción de HHD, tabla 13, p. 107. Columnas: luz libre en metros; filas: V en m/s.

| V / L | 10 | 13 | 16 | 18 | 21 | 25 | 30 | 42 | 52 | 63 | 106 | 124 | 200 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| <1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 1.0 | 0.96 | 0.97 | 0.98 | 0.98 | 0.99 | 0.99 | 0.99 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 1.5 | 0.94 | 0.96 | 0.97 | 0.97 | 0.97 | 0.98 | 0.99 | 0.99 | 0.99 | 0.99 | 1.00 | 1.00 | 1.00 |
| 2.0 | 0.93 | 0.94 | 0.95 | 0.96 | 0.97 | 0.97 | 0.98 | 0.98 | 0.99 | 0.99 | 0.99 | 0.99 | 1.00 |
| 2.5 | 0.90 | 0.93 | 0.94 | 0.95 | 0.96 | 0.96 | 0.97 | 0.98 | 0.98 | 0.99 | 0.99 | 0.99 | 1.00 |
| 3.0 | 0.89 | 0.91 | 0.93 | 0.94 | 0.95 | 0.96 | 0.96 | 0.97 | 0.98 | 0.98 | 0.99 | 0.99 | 0.99 |
| 3.5 | 0.87 | 0.90 | 0.92 | 0.93 | 0.94 | 0.95 | 0.96 | 0.97 | 0.98 | 0.98 | 0.99 | 0.99 | 0.99 |
| >4.0 | 0.85 | 0.89 | 0.91 | 0.92 | 0.93 | 0.94 | 0.95 | 0.96 | 0.97 | 0.98 | 0.99 | 0.99 | 0.99 |

Sin obstáculos: μ=1, según el texto de la misma página. No confundir L con Be. Las
categorías `<1.0` y `>4.0` y las filas exactas de V se usan literalmente. La fuente no
explica interpolación; deja además sin fila literal `V=4.0` y el intervalo
`3.5<V≤4.0`. Por aprobación posterior del usuario, solo para L se evalúa entre dos
columnas contiguas:

`μ=μ₁+(μ₂−μ₁)·(L−L₁)/(L₂−L₁)`, con `10≤L≤200m`.

No redondear L a la columna más próxima. No extrapolar ni interpolar la fila V. La
memoria identifica la convención como criterio aprobado por el usuario, no norma MTC.

Rectificación de transcripción (2026-10-09): una segunda revisión visual a400dpi
del PDF original confirma fila >4.0: L25=0.94 y L30=0.95. La primera versión de esta
documentación y del código tenía incorrectamente0.945 y0.96. Se corrige nuestra
transcripción, no el manual. Evidencia: `tmp/pdfs/ampliacion/tabla13-107.png`.
Recalcular proyectos anteriores afectados por esas dos celdas; resultados/reportes
emitidos con ellas no se corrigen automáticamente. Casos V=2 publicados no afectados.

### 4.5 Corrección por mezcla φ y compatibilidad de unidades

HHD pp. 107–108 imprime:

`φ=1` para `γm=1.0 T/m³` (agua clara).

`φ=−0.54+1.5143·γm` para `γm>1.0 T/m³` (lecho móvil).

La misma fuente denomina γm peso específico y afirma φ≥1, pero la recta produce φ<1 para `1<γm<1.016971538…`. Por instrucción del usuario, conservar la expresión y sus condiciones impresas, incluidos −0.54 y 1.5143, sin aplicar `max(1,φ)` ni cambiar el intervalo. Mostrar la discrepancia junto al valor obtenido y en la memoria. La aplicación literal queda definida; la discrepancia documental permanece registrada y no se declara resuelta.

La fuente utiliza T/m³ para un peso específico. La compatibilidad con entradas SI requiere dejar inequívoca esa unidad antes de automatizar su conversión; no sustituirla silenciosamente por densidad en kg/m³. Hasta cerrar la interpretación documental, conservar la unidad impresa en la transcripción. Ninguna conversión podrá cambiar los coeficientes −0.54 y 1.5143 ni evaluar la ecuación con una unidad incompatible.

### 4.6 Ecuación granular por punto

HHD p. 108, ecuación 59, comprobada visualmente:

`Hs,ᵢ = [α · hᵢ^(5/3) / (0.68 · β · μ · φ · Dm^0.28)]^(1/(1+z))`

En esa expresión empírica h y Hs están en metros y Dm en milímetros. Se propone almacenar longitudes en metros y convertir explícitamente `Dm_mm=1000·Dm_m` al evaluar el término empírico. Los milímetros son un submúltiplo SI; no se prohíbe su uso en la interfaz granulométrica.

**Discrepancia de la fuente:** p. 108 define Dm en mm, pero la tabla resumen 29 de p. 158 dice m manteniendo 0.68. Se propone usar mm conforme al desarrollo específico de la ecuación 59 y registrar esta decisión. No usar Dm en metros con el mismo coeficiente 0.68 sin transformar la expresión.

Calcular `Sg,ᵢ=Hs,ᵢ−hᵢ` y `Zll,ᵢ=Zw−Hs,ᵢ`. Hs es la profundidad desde la superficie del agua hasta el fondo calculado, no el descenso del lecho. Para hᵢ≤0, no evaluar LL.

Política propuesta para Sg<0: conservar el valor algebraico y marcar «sin profundización predicha por este cálculo». No inferir sedimentación. Para un perfil de erosión limitado al fondo original, mostrar por separado `Sg_aplicada=max(0,Sg)` y `Zperfil=Zfondo−Sg_aplicada`. El recorte es una convención de presentación propuesta, no una ecuación del manual.

## 5. Fases de presentación y reportes

Presentación: tabla por escenario y punto con x, Zfondo, Zw, h, Dm, α, β, z, μ, φ, Hs, Sg algebraica, Sg aplicada y Zperfil. Gráfico con terreno natural, agua y perfil calculado; distinguir puntos secos y resultados pendientes/inválidos. Cambiar entradas invalida los resultados anteriores hasta recalcular.

Reportes Word/PDF: datos originales, unidades y conversiones, hipótesis, escenario, procedencia de muestras, ecuaciones, sustituciones, selección de coeficientes conforme a `docs`, resultados por punto, gráfico y referencias con archivo/página/ecuación. Una única salida trazable del núcleo alimenta pantalla y reportes; estos no recalculan fórmulas.

Con μ corrector, rotular «Socavación general LL incluyendo corrección por contracción». PUENTES §1.2.3a exige considerar también socavación local para el estudio completo. No sumar otra estimación de contracción al resultado corregido ni presentarlo como socavación total o cota final de cimentación.

## 6. Comprobaciones y pendientes originales

Comprobaciones aritméticas independientes; no constituyen casos normativos aprobados:

- Granulometría ilustrativa: D=[0.2,0.6,1.0] mm y Δp=[20,50,30]% → Dm=(4+30+30)/100=0.64 mm.
- Tabla 13: V=2.0 m/s y L=30 m → μ=0.98; ausencia de obstáculos → μ=1.
- El ejemplo anterior que utilizaba β y z supuestos queda retirado como referencia de cálculo y de pruebas. Los casos completos deberán utilizar exclusivamente coeficientes localizados en `docs`.
- Inconsistencia de φ: con γm=1.01 en la unidad impresa, la recta da 0.989443, menor que 1.

| Pendiente | Evidencia necesaria para cerrarlo |
| --- | --- |
| α y Be para secciones irregulares | Definición localizada en docs; cierre de caudal por franjas y ejemplo manual |
| β(T), z(Dm) | Ubicación en docs de valores/relaciones, dominios y unidades |
| φ | Interpretación documental de unidades para entrada SI; expresión literal ya fijada, con discrepancia visible |
| μ para L intermedia | Resuelto por criterio lineal del usuario dentro de10–200m; no atribuirlo al MTC |
| μ para V sin fila o L fuera del intervalo | Regla localizada en docs; sin ella, no asignar coeficiente |
| Alcance geotécnico | Declarar qué distribución de materiales se admite; no asumir tratamiento de estratos |

Una vez cerrados, desarrollar manualmente una sección rectangular y una irregular con puntos secos, un caso de puente con contracción y los escenarios pertinentes. Registrar valores intermedios, precisión y tolerancias antes de convertirlos en pruebas automatizadas. No usar resultados del futuro núcleo para generar sus propios valores esperados.

## 7. Evidencia de la revisión inicial

- [x] Inventario e identificación de los dos PDF locales.
- [x] Lectura de páginas pertinentes y comprobación visual de HHD 92, 106–108, 158 y PUENTES PDF 51.
- [x] Proceso organizado en las cuatro fases solicitadas.
- [x] Discrepancias y fórmulas no sustentadas diferenciadas de contenido normativo.
- [x] Instrucción posterior incorporada: coeficientes literales de docs, sin fuentes externas ni ajustes propios.
- [ ] Cierre técnico de los pendientes y ejemplos manuales completos.
- [ ] Aprobación del proceso y del plan antes de programar, según instrucción del usuario.

La revisión visual fue realizada en esta sesión; no se afirma revisión independiente por un segundo especialista. Imágenes de apoyo en `tmp/pdfs/revision_normativa/`.
