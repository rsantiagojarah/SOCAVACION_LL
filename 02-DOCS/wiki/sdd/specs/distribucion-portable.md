---
type: spec
slug: distribucion-portable
status: approved in autopilot
timestamp: 2026-10-09
---
# Distribución portable — parte de E
## Problem & why
El lanzador actual depende de Python local y no basta para abrir el programa en otro equipo.
## Cost of not building it
Cada instalación exige preparar un entorno de desarrollo y dependencias.
## The cheapest alternative
Mantener instrucciones de instalación, menos cómodo que distribuir la carpeta autocontenida.
## Goals
Producir ejecutable Windows con bibliotecas, fuentes de reportes y referencias locales.
## Non-goals / out of scope
No firmar binarios, publicar, añadir actualización automática ni afirmar prueba en Windows limpio
si ese entorno no está disponible. Instalador y recuperación de borradores quedan pendientes de E.
## Users & context
Usuario de Windows que quiere abrir la aplicación sin ejecutar comandos Python.
## Behaviour
Abrir EXE muestra la misma interfaz. La carpeta se mueve completa. Una autocomprobación
opcional comprueba cálculo, guardado/apertura, Word/PDF y captura sin editar proyectos del usuario.
Empaquetar nunca elimina una distribución existente; requiere un destino nuevo.
## Acceptance criteria
1. Se genera EXE y se ejecuta sin invocar el Python de .venv.
2. Autocomprobación desde ruta con espacios entrega resultado esperado, JSON, DOCX, PDF y captura.
3. Fuente/paquete usan la misma evaluación; no nuevas ecuaciones ni red en funcionamiento.
4. La construcción falla con destino existente sin borrarlo; fuentes locales acompañan distribución.
5. Documentación distingue prueba en equipo actual de Windows limpio aún no realizada.
## Points to clarify
- **suposición tomada**: carpeta portable primero, preserva separación de recursos y permite inspección.
- **decisión diferida**: firma, instalador y Windows limpio no se simulan ni se declaran aprobados.
## Clarifications
Autorización global automática de ruta E, sin cambios científicos; no preguntas nuevas necesarias.
