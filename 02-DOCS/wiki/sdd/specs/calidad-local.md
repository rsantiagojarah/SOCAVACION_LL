---
type: spec
slug: calidad-local
status: approved in autopilot
timestamp: 2026-10-09
---
# Controles reproducibles de calidad — entrega F
## Problem & why
La entrega v0.1 pasa pruebas funcionales pero no tiene análisis estático, de tipos,
medición de ramas ni auditoría automatizada de dependencias.
## Cost of not building it
No hay evidencia repetible de esas categorías de defectos antes de distribuir cambios.
## The cheapest alternative
Una revisión manual reduce algunos riesgos pero no detecta regresiones automáticamente.
## Goals
Un comando verifica pruebas, límites, análisis, tipos, cobertura y dependencias; falla ante error real.
## Non-goals / out of scope
No cambiar ecuaciones ni prometer ausencia de vulnerabilidades o validación profesional.
No ocultar alertas mediante listas de exclusión generales; no hacer actualizaciones mayores sin revisar impacto.
## Users & context
Desarrollador/ingeniero que necesita repetir la comprobación en el entorno del proyecto.
## Behaviour
Herramientas ausentes o auditoría sin red se identifican como verificación incompleta, no éxito.
Los resultados numéricos permanecen idénticos. La cobertura de ramas del núcleo debe ser >=90%.
## Acceptance criteria
1. Pruebas completas y ejemplos anteriores pasan.
2. Análisis estático de producción y tipos de núcleo/dominio sin errores; alcance declarado.
3. Medición de ramas del núcleo >=90%; el comando falla si falta evidencia o cae el umbral.
4. Auditoría de dependencias ejecutable y evidencia del resultado; no declarar limpia si no consultó avisos.
5. Un comando local ejecuta comprobaciones y propaga fallos; probar control positivo y negativo.
## Points to clarify
- **suposición tomada**: tipos graduales con núcleo/dominio primero; GUI dinámica declarada no verificada por tipos.
- **decisión diferida**: distribución Windows limpio pertenece a E, no la reemplaza esta verificación.
## Clarifications
Modo automático aprobado por «SI»; no se exige cambiar pruebas existentes para acomodar herramientas.
