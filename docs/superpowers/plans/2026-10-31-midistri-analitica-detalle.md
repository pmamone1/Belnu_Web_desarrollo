# Analítica desplegable Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Steps use checkbox syntax.

**Goal:** Abrir detalles verificables desde cada indicador del resumen, dentro de la misma consulta.
**Architecture:** Conservar una base de métricas sin filtros inferiores dentro del resultado existente; módulo de proyección paginada. La vista actual responde también JSON privado con fragmento HTML, sin nuevas rutas ni modelos.
**Tech Stack:** Django3.2/Python3.7, JavaScript/CSS del portal, herramientas de release existentes.
**Spec:** docs/superpowers/specs/2026-10-31-midistri-analitica-detalle-design.md

## Global Constraints
Mismo corte/período/alcance y propietario. Detalle cuenta igual al resumen. Sin migraciones, campañas, SMTP, captura, reescrituras históricas o cambios económicos. Bases32/33 y624/625.

## Review Focus
Deduplicación producto/visita en bloque20/65; filtros inferiores/fichas no alteran el detalle global; inactivos históricos; caducidad y permisos por petición; carreras AJAX/cierre durante carga y paginación accesible.

### Task 1: Datos, permisos y panel
Files: analitica_informes.py, analitica_detalle.py, analitica_views.py, analitica_detalle.html, analitica_panel.html. Test: test_analitica_detalle_v34.py.
Interfaces: tarjetas(resumen,params)->list de nueve enlaces; detalle(data,metrica,pagina)->contexto con columnas, filas, total, paginador. data.metricas_base contiene eventos/vendedores/pedidos sin filtros inferiores, del mismo corte.
- [x] Tests RED: nueve totales, producto único en dos tiendas, UUID visita compartido, inactivos, corte/tiendas, filtros y consulta caducada,50 filas, JSON/HTML y permisos.
- [x] Implementar base y proyección sin materializar todos los eventos; render HTML autoescapado. Mantener código de informe/Excel actual.
- [x] Tests GREEN y suite de analítica. Expected: OK.
- [ ] Commit de implementación.

### Task 2: Interacción, entrega y revisión
Files: analitica_detalle.js, analitica_panel.css, tools/qa_analitica_v34.py, tools/test_analitica_v34.cjs; docs/manuales y release scripts/tools nuevos.
Interfaces: GET parcial=metrica devuelve JSON{html}; mismo control de permiso y vencimiento que vista completa. Enlaces preservan filtros/tienda y reinician página al cambiar indicador.
- [x] QA local: abrir/cerrar/cambiar tarjeta/paginar, cero resultados, carga/error/respuestas fuera de orden, teclado, PC1440/celular390/320 y cuatro temas. Expected: PASS.
- [x] Actualizar documentos obligatorios, manuales PDF y comandos; pruebas de paquetes en todas las bases admitidas sin producción. Expected: PASS.
- [x] Revisión independiente final y correcciones importantes RED/GREEN.
- [ ] Publicar commits, verificar ZIP contra HEAD, guardar en Downloads y entregar comandos completos. Sin instalación productiva ni envíos.
