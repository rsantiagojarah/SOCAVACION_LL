---
title: Propuesta técnica — Software de socavación general
status: propuesta-general-con-v01-implementada
date: 2026-10-09
method_scope: Lischtvan-Levediev / suelos no cohesivos
---

# Propuesta técnica — Software de socavación general

> Estado posterior: el usuario aprobó la interfaz y solicitó implementar la primera
> versión. El alcance ejecutado y sus exclusiones están en
> [especificación v0.1](../specs/primera-version.md), y las fuentes/ejemplos en
> [base operativa](base-calculo-v01.md). Esta propuesta general no significa que
> se hayan implementado secciones irregulares ni todos los desarrollos futuros.

## 1. Intención y límites obligatorios

Desarrollar una aplicación de escritorio para Windows, en Python y en español, para estimar **solo la socavación general** con el método de Lischtvan–Levediev aplicado a materiales granulares no cohesivos.

No se implementarán métodos de socavación local, contracción por otros métodos, ni la ecuación para suelos cohesivos. Tampoco se admitirá un proyecto cuyo material de lecho se clasifique como cohesivo. La aplicación debe mostrar este alcance en pantalla, en los reportes y en el archivo del proyecto.

La herramienta es de apoyo al juicio profesional. No sustituye la verificación del ingeniero responsable, la representatividad de la topografía/batimetría ni el estudio granulométrico.

## 2. Base técnica propuesta

Actualización del 2026-10-09: por instrucción del usuario, se adoptan como base los dos PDF de `docs/`. La definición detallada, las páginas de respaldo, la tabla de contracción y los pendientes están en el [proceso de cálculo basado en normativa local](proceso-calculo-normativa-local.md). Ese documento prevalece sobre cualquier simplificación de esta propuesta.

Precisión posterior del usuario: los coeficientes se tomarán exclusivamente como figuran en `docs`, conservando valores, decimales, ecuaciones y condiciones. No se permiten valores externos, supuestos ni ajustes/interpolaciones sin regla publicada en esos archivos. Los parámetros no localizados permanecen pendientes.

La fuente de la ecuación es el *Manual de Carreteras: Hidrología, Hidráulica y Drenaje*, sección 4.1.1.5.4, b.2.2, ecuación 59, p. 108 del archivo local. El *Manual de Puentes 2018*, §1.2.3a, p. impresa 47 / PDF 51, sustenta los escenarios y distingue la socavación general, por contracción y local.

Para cada punto mojado `i` de la sección transversal, se propondrá calcular:

```text
Hs,i = [ α · h_i^(5/3) / (0.68 · Dm^(0.28) · β · μ · φ) ]^(1 / (1 + z))

Sg,i = Hs,i − h_i
cota_socavada_i = cota_fondo_i − max(0, Sg,i)
```

La fórmula propuesta anteriormente para α requiere sustento adicional para secciones irregulares; no se considera una definición verificada en los PDF. La regla `max(0,Sg)` es una convención de presentación propuesta: se conserva también el resultado algebraico. Véanse los apartados 4.2 y 4.6 del proceso detallado.

Donde:

| Símbolo | Nombre | Unidad / regla |
| --- | --- | --- |
| `Qd` | Caudal de diseño | m³/s |
| `Be` | Ancho empleado en la definición de α | m; convención pendiente, no equivale automáticamente a luz libre o ancho estable |
| `A` | Área hidráulica al nivel de agua de diseño | m² |
| `Hm` | Tirante medio geométrico | m; A/B para sección simple con ancho mojado B |
| `h_i` | Tirante local de la franja `i` | m |
| `Dm` | Diámetro característico del lecho | mm, según la caracterización adoptada por el proyectista |
| `β` | Coeficiente de frecuencia | adimensional; tabla operativa no localizada en los PDF revisados |
| `μ` | Corrección por contracción del cauce | adimensional; `1.0` sin obstáculos; la tabla MTC es obligatoria para puentes con contracción |
| `φ` | Corrección por forma de transporte | adimensional; `1.0` para agua clara; para lecho móvil se calcula con el peso específico de la mezcla según MTC |
| `z` | Exponente de la ecuación | adimensional; relación operativa con Dm pendiente de fuente verificable |
| `Hs,i` | Tirante después de la socavación | m |
| `Sg,i` | Profundidad de socavación general local | m |

La pendiente se registrará como antecedente hidráulico. La velocidad interviene tanto en el control `V ≈ Qd / A` como en la selección de μ. El peso específico de mezcla sustenta φ; se conserva la ecuación impresa y se informa su discrepancia cerca de agua clara, sin corregir sus coeficientes. La interpretación de la unidad impresa para convertir desde SI sigue pendiente.

La tabla 13 de μ ya se transcribió y comprobó visualmente en el proceso detallado. β, z y la definición operativa de α siguen pendientes. No se codificarán valores de memoria o de fuentes sin verificar. El modelo completo aún no está validado.

### Ejemplos manuales

El ejemplo anterior con β y z supuestos se retira del proceso y de las pruebas de referencia. Los ejemplos completos se desarrollarán con coeficientes respaldados por archivo y página de `docs`. Las comprobaciones parciales de granulometría, celdas de μ y sustitución literal de φ se conservan en el proceso detallado.

## 3. Datos de entrada y validaciones

1. Proyecto: nombre, ubicación, autor, fecha, norma/fuente y notas.
2. Hidráulica: `Qd`, período de retorno, velocidad media, pendiente, cota del nivel de agua y condición de transporte.
3. Sección transversal: lista ordenada de pares `(abscisa, cota)`; la aplicación interpola los cruces con el nivel de agua y forma franjas mojadas.
4. Suelo: declaración obligatoria de material no cohesivo, `Dm`, método/fuente del valor y, si aplica, peso específico de mezcla agua–sedimento.
5. Puente/contracción: sin obstáculos o geometría suficiente para seleccionar/revisar `μ`.
6. Coeficientes: archivo de docs, página, tabla/ecuación, valor publicado y condiciones de selección. El ingreso manual solo puede transcribir un valor respaldado en docs; no habilita ajustes libres.

Validaciones propuestas: valores finitos, `Dm > 0`, sección ordenada, área mojada positiva, material no cohesivo y coeficientes con fuente en docs. Los puntos secos se conservan y se excluyen del cálculo. Admitir mm como submúltiplo SI y documentar conversiones. Advertir discrepancias entre `Qd/A` y V. No inventar un umbral normativo de pendiente ni interpolar/extrapolar coeficientes sin regla publicada en docs.

## 4. Arquitectura monolítica modular propuesta

Se implementará un único ejecutable/proceso local. Los módulos colaboran por contratos Python simples; no habrá microservicios ni base de datos remota.

```text
Interfaz de escritorio (presentación)
        │ comandos y modelos de vista
        ▼
Servicios de aplicación (orquestación de casos de uso)
        │ objetos de dominio validados
        ├──────────────► Núcleo Lischtvan–Levediev (puro, sin GUI ni archivos)
        │                         │
        │                         ▼
        │                  Perfil y resultados por franja
        ▼
Persistencia de proyecto        Reportes Word/PDF y gráficos
```

Estructura inicial propuesta:

```text
src/socavacion_ll/
  dominio/       # entidades, unidades SI, validaciones y errores
  calculo/       # ecuación LL, coeficientes trazables, franjas y perfil
  aplicacion/    # abrir, guardar, calcular y exportar
  presentacion/  # formularios, tabla de sección, gráfico y mensajes
  infraestructura/# JSON de proyecto, plantillas, Word/PDF y recursos
  pruebas/       # unitarias, casos manuales e integración de reportes
```

Reglas de diseño:

- Nombres de carpetas, clases, funciones, variables, mensajes y reportes en español.
- Ningún archivo de producción supera 250 líneas. Si crece, se separa por responsabilidad antes de añadir lógica.
- DRY: una única definición de unidades, ecuaciones, coeficientes y formato de números.
- SOLID: el cálculo no conoce la interfaz, reportes ni archivos; los puertos de almacenamiento y exportación se sustituyen en pruebas.
- KISS: JSON versionado para proyectos en la primera entrega. No se añade base de datos, nube, cuentas ni plugins sin un caso aprobado.
- El núcleo devuelve resultados y trazabilidad de cada operación; no redondea internamente. El redondeo ocurre solo en presentación y reporte.

Tecnología propuesta para aprobación: Python 3.12+, PySide6 para la interfaz, Matplotlib para perfil y gráfico, `python-docx` para Word, ReportLab para PDF, Pydantic/dataclasses para validación y Pytest para pruebas. Se confirmará la compatibilidad de versiones antes de fijarlas.

Actualización visual: por petición expresa del usuario se adaptó el estilo de
`C:/Users/CARMEN/Desktop/PROYECTOS/Metrados_rj`. La vista previa utiliza PySide6 6.11.2,
tema oscuro, Segoe UI, acento turquesa, cabecera compacta y navegación de cuatro fases.
Sus pruebas actuales utilizan unittest. Esta entrega solo implementa presentación
navegable de solo lectura: no calcula, guarda ni exporta. No implica aprobación del
alcance reducido propuesto para el núcleo. Evidencia en
[adaptación visual de Metrados](../../ftd/estilo-interfaz-metrados.md).

## 5. Entregas por fases

| Fase | Resultado verificable |
| --- | --- |
| 0. Fundación técnica | Constitución del proyecto, bibliografía/tables verificadas, casos manuales y entorno de pruebas. |
| 1. Ingreso de datos | Proyecto, hidráulica, suelo y sección transversal con validación SI y persistencia JSON. |
| 2. Núcleo de cálculo | Cálculo por franjas, coeficientes trazables, perfil socavado y pruebas unitarias contra ejemplos manuales. |
| 3. Presentación | Interfaz moderna en español, tabla de resultados, advertencias y gráfico de terreno, agua y socavación. |
| 4. Reportes | Memoria Word/PDF con ecuaciones, sustitución, resultados por franja, fuentes, advertencias y versión del proyecto. |
| 5. Verificación y entrega | Pruebas de regresión, caso de sección irregular, apertura/edición/guardado, empaquetado Windows y revisión técnica. |

## 6. Riesgos y controles

1. **Tablas o curvas ambiguas.** Control: fuente primaria, transcripción doble, pruebas de puntos tabulados y registro de edición.
2. **Uso fuera del método.** Control: declaración y bloqueo para cohesivos; rótulo visible de “socavación general, no local”.
3. **Geometría de sección deficiente.** Control: validadores geométricos, puntos secos excluidos y advertencias en la memoria.
4. **Resultado entendido como diseño automático.** Control: avisos de límite técnico y trazabilidad completa en cada exportación.
5. **Deriva de arquitectura.** Control: módulos de máximo 250 líneas, pruebas del núcleo aislado y revisión de dependencias.

## 7. Fuentes iniciales verificadas

1. `docs/MAN_11 HHD-2011.pdf`: ecuaciones 52, 58 y 59; tablas 13 y 29. Se excluye la ecuación 60 de suelos cohesivos.
2. `docs/Manual de Puentes MTC 2018 (PGA).pdf`: §§1.2.2–1.2.6, en particular §1.2.3a.
3. Las referencias bibliográficas citadas en los manuales no habilitan la incorporación de coeficientes externos. El registro de fuentes locales y huellas está en el proceso detallado.

## 8. Decisiones que requieren aprobación

El alcance, la arquitectura monolítica modular, las cuatro fases, el límite de 250 líneas y los nombres en español son requisitos expresos del usuario; no requieren volver a decidirse. La revisión de las normativas locales ya está autorizada y realizada en los términos documentados.

Antes de programar falta cerrar los pendientes técnicos del proceso detallado y presentar para aprobación el modelo completo, los ejemplos, el conjunto tecnológico y el plan definitivo. La solicitud de documentar o revisar fuentes no constituye aprobación para empezar a programar.

## 9. Historial de revisión

- 2026-10-09: propuesta inicial.
- 2026-10-09: revisión desde los PDF de `docs/`; corregidos el estado de α/β/z, el papel de V, la distinción de anchos, las unidades y el carácter ilustrativo del ejemplo. Incorporadas discrepancias de fuentes y escenarios de PUENTES 2018.
- 2026-10-09: instrucción explícita de tomar los coeficientes tal como aparecen en docs; retirados el ejemplo con coeficientes supuestos, las interpolaciones no documentadas y el ingreso manual libre.
