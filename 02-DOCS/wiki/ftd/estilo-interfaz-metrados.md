---
author: CARMEN
branch: sin-repositorio-git
status: in-progress
---
# Adaptación visual de Metrados a Socavación

## Intent

Aplicar a SOCAVACION_LL el estilo solicitado de `C:/Users/CARMEN/Desktop/PROYECTOS/Metrados_rj`.
Es un cambio visual acotado, independiente de la aprobación del alcance del núcleo LL.

## Scope

Incluye tema oscuro, colores, tipografía Segoe UI, cabecera compacta, barra plana,
navegación lateral, separador ajustable, tablas y estados vacíos para las cuatro fases.
La vista previa será navegable y ejecutable, con datos ilustrativos de solo lectura.
Las acciones todavía no implementadas estarán deshabilitadas y claramente rotuladas.
No incluye cálculo, persistencia de proyectos ni exportación de memorias.
No modifica Metrados, sus datos, su entorno, ni los documentos normativos.
No copia el dominio de metrados, la integración AutoCAD, Rust ni SQLite.
Código propio en español, salvo nombres de API y puntos de extensión exigidos por Qt.
Máximo 250 líneas por módulo; separación por responsabilidades.

## Checklist

- [x] Leer los archivos visuales de referencia: tema y cabecera completos, navegación y composición pertinentes.
- [x] Adaptar los colores y componentes a un paquete independiente, sin importaciones de Metrados.
- [x] Probar navegación, acciones pendientes deshabilitadas y tablas de solo lectura.
- [x] Revisar capturas a tamaño inicial y mínimo; el contenido excedente es accesible mediante desplazamiento.
- [x] Verificar el límite de 250 líneas y conservar las huellas de los archivos fuente.
- [x] Documentar cómo iniciar la vista previa y sus límites.

## Evidence

- Fuente: `app/metrado/theme.py`, `chrome.py`, `navigation.py` y composición de `window.py`.
- Referencia: PySide6 6.11.2 instalado en su entorno; no se modificará ese entorno.
- SHA-256 de theme.py: `3e98dd1e696a7b326973ccde8b18bf3253393162e8e21b8cde5f64ec09b74ede`.
- SHA-256 de chrome.py: `91c3f44e41d95abc919fe2f15d3efab23f91fd2c786e49b203105d734b032ec6`.
- Fondo `#11151b`, panel `#191e26`, superficie `#171b22`, acento `#25b9c4`.
- Fuente Segoe UI a 11 px; cabecera 34 px; acciones 38 px; estado 24 px.
- Prueba inicial observada: error `ModuleNotFoundError: socavacion_ll` antes de crear el paquete.
- Verificación final: `.venv/Scripts/python.exe -m unittest discover -s pruebas -v`;
  7 pruebas aprobadas. Incluye control del máximo de 250 líneas y ausencia de imports de Metrados.
- PySide6 6.11.2 instalado en `.venv` propio; la aplicación no depende del entorno de referencia.
- Ocho capturas revisadas: cuatro pantallas a 1480×820 y a 1000×640 en `tmp/interfaz/`.
- En la revisión offscreen se cargaron las fuentes de Windows explícitamente porque ese motor
  no las enumera automáticamente. Corregido el ajuste de rótulos en la banda de fase.
- Huellas de `theme.py` y `chrome.py` comprobadas de nuevo: coinciden con las iniciales.
- `LEEME.md` explica lanzamiento, pruebas y límites; `Abrir Socavacion.cmd` inicia la interfaz.
- No se afirma validación hidráulica ni prueba manual interactiva en todos los escalados de Windows.

## Next

Revisión visual del usuario. Después, retomar el cierre técnico y el alcance de la versión calculadora
en SDD, sin considerar esta entrega como aprobación de ecuaciones o limitaciones nuevas.
