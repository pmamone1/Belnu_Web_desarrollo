# Editor y pedidos MiDistri Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Steps use checkbox syntax.

**Goal:** Mejorar edición y consulta de pedidos sin alterar operación.
**Architecture:** Campos JSON opcionales y validados, controles sobre borrador y proyección de snapshots de pedidos. Sin modelos o endpoints nuevos.
**Tech Stack:** Django3.2/Python3.7 portal, Django5/Python3.10 Urban, JavaScript/CSS existentes.
**Spec:** docs/superpowers/specs/2026-10-31-midistri-editor-pedidos-design.md

## Global Constraints
Sin campañas ni SMTP, no producción como QA, sin migraciones ni cambios económicos; aislamiento por vendedor/distribuidora. Conservar huella de páginas antiguas sin estilos.

## Review Focus
Referencias retiradas no bloquean edición pero sí publicación; JSON malicioso rechazado; deshacer restaura eliminación; cantidades pendientes no se confunden con cero confirmado; móvil muestra toda la tabla/detalle.

### Task 1: Editor y mensajes
Files: pagina.py, editor_views.py, mensaje_estilos.py, editor_visual.js/html/css, plantillas públicas y midistri_formatos.py. Test: test_editor_v33.py.
Interfaces: validar_mensajes(data)->dict, css_mensaje(data,key)->str, advertencias_pagina(data,did)->list; consumidores: render público/editor y firma existente.
- [ ] Escribir tests de validación independiente, compatibilidad huella, fuentes retiradas guardables y publicación bloqueada, ocultación de acceso público.
- [ ] Ejecutar tests y comprobar RED.
- [ ] Implementar controles AJAX, eliminación reversible, estilos seguros y advertencias localizables.
- [ ] Ejecutar tests/editor previo y controles de navegador sintéticos. Expected: PASS.
- [ ] Commit de editor.

### Task 2: Pedidos desplegables
Files: historial_presentacion.py, views.py, pedidos.html, pedidos_tabla.js/css. Test: test_pedidos_tabla_v33.py.
Interfaces: resumen_pedido(pedido)->dict con total solicitado/vigente, filas, estado de cantidades; sólo snapshots validados existentes.
- [ ] Tests de parcial, revisión, cancelación y falta de actualización; aislamiento del vendedor.
- [ ] Ejecutar y comprobar RED.
- [ ] Proyectar y renderizar tabla/despliegue accesible con remito y detalles.
- [ ] Ejecutar tests e inspeccionar PC/celular. Expected: PASS.
- [ ] Commit de pedidos.

### Task 3: Entrega Urban625/MiDistri33
Files: documentación obligatoria, manual PDF, scripts/tools de instalación y paquetes nuevos sobre624/32.
Interfaces: manifiestos con hashes y base exacta; sin migraciones nuevas, sin cambios de configuración operativa.
- [ ] Actualizar documentación y PDF principal; revisar unión con histórico.
- [ ] Verificar instaladores dry-run/rollback e inventarios, suite pertinente y sintaxis versiones objetivo. Expected: PASS.
- [ ] Revisión independiente final; corregir hallazgos importantes con RED/GREEN.
- [ ] Publicar commits, generar y verificar ZIP; guardar en Downloads y entregar comandos completos. Expected: hashes y HEAD remoto coinciden.
