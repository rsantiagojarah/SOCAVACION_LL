---
type: verification
title: Comprobación local de Socavación LL v0.1
date: 2026-10-09
source_state: sin-Git-src-sha256-d89fee6006f4cb8b0f98387af3f53cf2792ef18d43f53523627b82825e58b516
---

# Comprobación local de v0.1

## Ejecución final

Comando configurado ejecutado después de la última edición de código:

```text
.venv/Scripts/python.exe -m unittest discover -s pruebas -v
Ran 53 tests in 7.217s
OK

.venv/Scripts/python.exe -m compileall -q src pruebas
Sin errores de compilación.

.venv/Scripts/python.exe -m pip check
No broken requirements found.
```

El entorno restringido avisó que no pudo guardar la caché de fuentes de Matplotlib
en el perfil de usuario. No impidió gráficos, reportes ni pruebas. No se cambiaron
permisos del perfil. `pip check` comprueba dependencias, no vulnerabilidades.

Se observaron 29 módulos en src; el mayor tiene152 líneas, menor al máximo250.
Núcleo importa únicamente math, dominio y coeficientes: no Qt ni generadores de reportes.
La huella de source_state concatena ruta relativa POSIX y bytes de cada .py de src,
ordenados por ruta. No hay commit porque la carpeta no es repositorio Git.

## Criterios y tareas

| Criterio de spec | Evidencia observable |
| --- | --- |
| 1: ejemplo manual | test_ejemplo_manual_rectangular y equilibrio independiente aprobados; además segundo ejemplo con mu=.98 |
| 2: rechazos | Pruebas de tablas literales, no finitos, cohesivos, mezcla y geometría inválida |
| 3: proyectos | 12 pruebas JSON y10 de sesión; ida/vuelta real y conservación ante fallos |
| 4: invalidación | test_calcular_e_invalidar_al_editar y test_error_no_deja_resultado_anterior |
| 5: memorias | 7 pruebas de archivos reales; todas las páginas de Word/PDF del ejemplo inspeccionadas |
| 6: módulos y desacoplamiento | Conteo automático, control sintético de251 líneas rechazado y archivos reales aceptados; importaciones del núcleo inspeccionadas mediante AST |
| 7: perfiles | Casos Sg<0 en núcleo, gráfico y ambas memorias; no se interpreta como depósito |
| 8: estilo/español | 11 pruebas Qt; cuatro fases renderizadas en1480x820 y1000x640 |

T1 corresponde a fuentes/ejemplos y contratos; T2 a criterio1/2/7; T3 a3/4;
T4 a5/7; T5 a4/8; T6 a esta corrida, revisión y guía de usuario.
El control de251 líneas prueba el límite de longitud, no la calidad semántica ni
el desacoplamiento completo. No se atribuye esa cobertura a un simple conteo.

## Revisión visual y adversarial

- Capturas reales Qt en `tmp/interfaz/`, cuatro fases a tamaño normal y mínimo.
  Formularios/tablas utilizan desplazamiento cuando no cabe el contenido.
- Memoria PDF de cuatro páginas en `tmp/memorias/`; todas inspeccionadas mediante PNG.
- DOCX abierto de solo lectura en una instancia Word automatizada, convertido a PDF
  para revisión; cuatro páginas inspeccionadas en `tmp/memorias/word_revision/`.
  Ecuaciones nativas con fracciones/exponentes legibles; tablas sin pérdida de columnas.
- Revisión independiente de código: sin hallazgos importantes abiertos. Dos defectos
  reproducidos y corregidos con regresión: reabrir el archivo actual tras Guardar,
  y responsable>255 caracteres al escribir el metadato Word.
- El cuerpo Word conserva responsable completo hasta500 caracteres; PDF conserva
  responsable500 y notas20000 sin espacios. Pruebas específicas aprobadas.
- Cancelar cierre/nuevo y error OSError al guardar preservan trabajo, comprobado
  por revisor con simulación de diálogos. No se afirma prueba manual de cada diálogo nativo.

## Integridad documental

Huellas finales coinciden con las iniciales:

```text
HHD: 0a1bdcd7c94016760642de91baf4d6e317e4cc85c529dfefae9a6bf76c8dcd88
Puentes: 46d37849141b3acef44bdae112496dafbb5d6813dc008d5495c2f2bb760936b1
```

Metrados solo se usó como referencia visual. Los complementos no se atribuyen al
MTC. La ficha de Schreider declara que es referencia/enlace, no PDF completo local.

## Capas no ejecutadas

- **HERRAMIENTA-AUSENTE:** no hay scripts/verify.sh de stack, ruff, mypy, coverage
  ni pip-audit configurados/instalados. No se midió cobertura ni se hizo auditoría
  automática de vulnerabilidades. La suite configurada sí se ejecutó completa.
- **SUSTITUIDA:** el renderizador documental estándar falló por ausencia de LibreOffice;
  se revisó el DOCX renderizado por Word. No demuestra idéntica paginación en LibreOffice.
- **SUSTITUIDA:** interfaz probada mediante Qt offscreen y simulación de diálogos;
  no certifica integración con todos los escritorios Windows/DPI ni instalador limpio.
- **NO-APLICA:** migraciones de base de datos, servidor, autenticación o despliegue web;
  la aplicación es local y guarda JSON.

## Veredicto

Los ocho criterios funcionales del alcance v0.1 tienen evidencia local favorable.
La revisión de código aprueba ese alcance;53 pruebas pasan. Puede entregarse como
primera versión para pruebas locales, con las exclusiones visibles.

La puerta integral de liberación SDD permanece **incompleta (FAIL de cobertura de
capas de calidad)** por falta de análisis estático, medición de cobertura y auditoría
de dependencias; no se declara PASS integral ni producto profesional certificado.
Siguiente endurecimiento: configurar herramientas para Python/PySide6 y probar
distribución en Windows limpio. La validación de ingeniería de una obra sigue siendo
responsabilidad de un especialista y no se sustituye con estos tests.
