# Plan de primera versión

## 0. Global Constraints

- Exclusivamente Lischtvan-Levediev y suelos no cohesivos.
- Sección rectangular, lecho homogéneo y agua clara; phi=1.
- MTC HHD 2011 y Puentes 2018 como fuentes principales; complementos separados.
- Valores literales, sin interpolar/extrapolar beta, z o mu.
- SI; Dm en mm dentro de la expresión empírica 0.68*Dm^0.28.
- Monolito modular, máximo 250 líneas por módulo, identificadores propios en español.
- No modificar Metrados ni los PDF principales. No redondear dentro del núcleo.

## 1. Context & constraints

Implementa los ocho criterios de [la especificación](../specs/primera-version.md).
Autorización: petición reiterada de implementar la primera versión tras aceptar su interfaz.
Los requisitos expresos del usuario prevalecen sobre el esqueleto de constitución aún en borrador.

## 2. Architecture

```text
Presentación Qt -> servicio de sesión -> núcleo LL puro
                         |                   |
                         v                   v
                    proyectos JSON      resultado inmutable
                                             |
                                     gráfico y memorias
```

Todos los componentes son internos y locales. Solo la instalación descarga dependencias.
Una única evaluación alimenta pantalla y memorias; los reportes no recalculan ecuaciones.
Se elige JSON versionado frente a base de datos para mantener simple una entrega local.

## 3. Interfaces & contracts

- Proyecto y Resultado: dataclasses inmutables en `dominio/modelos.py`.
- calcular_proyecto(proyecto) -> Resultado o ValueError con mensaje en español.
- guardar_proyecto(ruta, proyecto), abrir_proyecto(ruta) -> Proyecto; guardado atómico.
- SesionProyecto: mantiene datos, resultado vigente, ruta y estado modificado.
- exportar_word(ruta, resultado), exportar_pdf(ruta, resultado): renderizan un resultado.
- crear_figura(resultado): representación compartida entre GUI y memorias.

## 4. Data model & flow

Proyecto: identificación, Q, T, B, fondo, agua, V, pendiente, Dm, clasificación,
agua clara, obstáculos, luz libre y número de puntos (2 a 201, límite de interfaz).
Geometría rectangular: puntos equidistantes en [0,B], h=agua-fondo constante.
Resultado: copia de Proyecto, área, Vcontrol, alpha/beta/mu/phi/z, operaciones,
puntos, advertencias y referencias. No se guarda como dato confiable en JSON.
La lectura de JSON es estricta; no ejecuta código ni acepta NaN, Infinity o booleanos numéricos.

## 5. Testing strategy

| Criterio | Nivel | Comprobación |
| --- | --- | --- |
| 1,2,7 | Unitaria | Ejemplos manuales, tablas literales, negativos y entradas inválidas |
| 3 | Integración | Ida/vuelta real, JSON malformado, fallo de escritura |
| 4 | Unidad y GUI | Estado de sesión y bloqueo de exportación tras editar |
| 5 | Integración | Archivos reales, lectura de contenido y revisión visual |
| 6 | Estática | Conteo de líneas e importaciones |
| 8 | GUI | Navegación, formularios y capturas en dos tamaños |

## 6. Sequencing & dependencies

- [x] T1: contratos y fuentes; dos ejemplos en base-calculo-v01.md, sin nuevas reglas normativas.
- [x] T2: núcleo puro y validación; 13 pruebas de cálculo/coeficientes aprobadas.
- [x] T3: JSON y sesión; 22 pruebas de almacenamiento/sesión aprobadas.
- [x] T4: gráficos y reportes; 7 pruebas y revisión visual de Word/PDF.
- [x] T5: formularios, acciones y resultados; 11 pruebas de interfaz y capturas en dos tamaños.
- [x] T6: 53 pruebas, revisión independiente, capturas, memorias y LEEME.md.

Evidencia y capas no ejecutadas: `../verifications/primera-version-2026-10-09.md`.
Estos checks describen implementación local, no certificación ni liberación industrial.

T2 y T3 son disjuntos después del contrato; T4 usa su interfaz estable; T5 integra.
El skill implement solicita delegación de tareas disjuntas; la raíz conserva integración.
No hay repositorio Git en esta carpeta: no se crean ramas ni commits.

## 7. Risks & open decisions

- Riesgo científico: no extender alpha rectangular a sección irregular; impedir esa entrada.
- Riesgo de interpretación: fuentes complementarias rotuladas; mu aplicado una sola vez.
- Riesgo de obsolescencia: toda edición invalida resultados y reportes.
- Riesgo de pérdida: confirmación de cambios y escritura mediante temporal del mismo directorio.
- Riesgo documental: verificar salida visual de ambas memorias; cualquier limitación se declara.
- Riesgo de tablas: ausencia de celda se rechaza, incluidas V=4 y 3.5<V<=4 para mu.

## Análisis previo

El alcance limitado evita convertir pendientes en hipótesis ocultas. Se mantienen
las cuatro fases y los requisitos originales. Los criterios se asignan a pruebas.
No se toma esta implementación como resolución de los pendientes fuera de v0.1.
