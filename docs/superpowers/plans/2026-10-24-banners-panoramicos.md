# Banners panorámicos de MiDistri — plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Promociones a todo el ancho con imágenes grandes y transiciones suaves.
**Architecture:** Ampliar la presentación del bloque banner sin cambiar los datos de la tienda ni el catálogo. Mantener inicialización al sustituirse el cuerpo de la página y compatibilidad de la página anterior.
**Tech Stack:** Django 3.2 / Python 3.7, CSS y JavaScript del portal. Sin dependencias nuevas.
**Spec:** ../specs/2026-10-24-banners-remitos-design.md
**Estado:** implementación local realizada; revisión final y publicación en preparación.

## Global Constraints
- Mantener cuatro plantillas/temas y las opciones contain/cover.
- No publicar borradores ni cambiar precios, pedidos, catálogo, conexiones o permisos.
- No enviar campañas.
- Una foto sin navegación; vídeos sin autoplay; respetar movimiento reducido.
- Preservar templates/accounts/forgotPassword.html, cambio preexistente ajeno.

## Review Focus
- Un banner panorámico no genera scroll horizontal en teléfono ni escritorio.
- La vista previa móvil no se expande al ancho completo de la pantalla de escritorio.
- Clics rápidos, foco y sustitución del cuerpo no dejan dos temporizadores o controles rotos.
- Movimiento reducido desactiva animación y comienza con rotación pausada.
- La tienda inicial anterior a la primera publicación también mejora sin publicar borradores.

### Task 1: Formato panorámico
**Files:** midistri_portal/static/midistri_portal/pagina.css; templates/midistri_portal/pagina_bloques.html y promociones.html; tools/qa_pagina_v12.py; tools/test_banners_browser_v12.cjs.
**Interfaces:** clase banner-panoramico identifica los bloques banner; las capas de foto y texto conservan orden de lectura y enlaces existentes.
- [x] Escribir prueba de navegador que mida el banner frente al viewport: diferencia máxima 2 px y document.scrollWidth <= viewport; móvil 390 px y escritorio 1440 px.
- [x] Implementar full bleed con contenido protegido por márgenes, imagen grande y composición adaptable. Conservar foto completa/recortada, vídeos y precios actuales.
- [x] Probar cuatro diseños, cuatro temas, preview móvil, una foto, nombres largos y promoción antigua.

### Task 2: Transición y accesibilidad
**Files:** pagina.js y controlador de promociones anterior, si corresponde; herramientas/pruebas del Task 1.
**Interfaces:** cambio de diapositiva con fundido cruzado 600 ms, transición cancelable; la diapositiva oculta no recibe foco ni lectura duplicada.
- [x] Escribir y observar fallar pruebas de transición, clic rápido, pausa, flechas, foco/hover y evento midistri:render.
- [x] Implementar transición progresiva sin mover el resto del catálogo; movimiento reducido cambia inmediatamente y no inicia autoplay.
- [x] Verificar vídeo detenido al cambiar, página oculta sin rotación y limpieza de temporizadores/listeners al reinicializar.

### Task 3: Revisión y entrega
- [x] Ejecutar suite del portal, pruebas de navegador local y compatibilidad sintáctica Python 3.7.
- [x] Revisar capturas de escritorio y móvil con fotos sintéticas de proporciones distintas.
- [x] Actualizar manual/documentación/versionado y manual PDF; revisar visualmente la unión con el contenido anterior.
- [x] Preparar instalador y ZIP independientes con preflight, respaldo de archivos y pruebas del paquete.
- [x] Revisión independiente final; publicar commit/PR de MiDistri y verificar bytes del ZIP contra commit/manifiesto.
- [x] Guardar sólo ZIP en Downloads y entregar comandos completos cPanel. Sin instalación productiva automática.

Validación y revisión local completas: docs/VALIDACION_v12.md. Entrega verificada al publicar; instalación productiva pendiente.
