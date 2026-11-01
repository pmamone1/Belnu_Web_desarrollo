# Catálogo lateral de MiDistri Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans. Ejecución en este chat, inline, una revisión independiente al final.

**Goal:** Catálogo visual con filtros/promociones a la izquierda y navegación estable por relevancia.
**Architecture:** Adaptador de presentación sin mutar páginas guardadas. Formularios GET asociados entre lateral y barra; paginación compartida. CSS específico por catálogo y panel nativo details progresivo, con vista previa real usando las mismas plantillas.
**Tech Stack:** Django3.2/Python3.7, HTML/CSS/JS existentes, sin dependencias ni migraciones.
**Spec:** docs/superpowers/specs/2026-11-01-midistri-catalogo-lateral-design.md

## Global Constraints
48 productos iniciales, opciones24/48/96/192 validadas. Relevancia conserva valorURL recomendados y orden_sesion; no altera ranking, precios ni elegibilidad. Filtros y promociones laterales de ambas zonas se reúnen en orden publicado sin reescribir borradores. Banners centrales se conservan. No footer Urban en portal, no SMTP ni campañas; preservar forgotPassword.html ajeno.

## Review Focus
Una página con promos en ambos márgenes no debe duplicarlas en centro. Cambiar tamaño de página no reordena ni repite IDs. SinJS y preview móvil conservan acceso a filtros. Nombres largos/precios/cantidades9990 y display15 deben caber a390/320. Diseños Lista/Fotos y página inicial antigua siguen utilizables.

### Task 1: Navegación y estructura
Files: create midistri_portal/catalogo_presentacion.py, test_catalogo_lateral_v37.py; modify views.py, pagina_views.py, editor_views.py, templates pagina_bloques/catalogo_inicial/catalogo_productos; create catalogo_filtros/catalogo_paginacion.
Interfaces: tamano_pagina(value)->24|48|96|192 default48; paginacion(page,filters)->{anterior,siguiente}, query encoded. contexto_catalogo_presentacion(context,GET/saved)->context visible with page_size/options and links. Summary sidebar template consumes categorias/subcategorias, activevalues, bloques; fields form=catalogo-filtros. No DB writes.
- [x] RED tests: default48/invalid48/options24/96/192; two pages no repeated IDs/reload stable; category/subcategory/q/size URLs; sidebar promos ordered left/right once; central preserved; preview/legacy render.
- [x] Implement minimal helper, views and shared GET/sidebar/pagination templates. Expected test_catalogo_lateral_v37 and test_rotacion_v32 PASS. Commit.

### Task 2: Presentación responsive y editor
Files: create static/midistri_portal/catalogo_lateral.css/js; modify base.html, pagina.css targeted selectors and editor_views preview context; create tools/qa_catalogo_v37.py and test_catalogo_v37.cjs.
Interfaces: .catalogo-layout sidebar + .tienda-centro, .catalogo-barra form and .catalogo-grid products; native details .catalogo-lateral remains usable withoutJS. Same template hierarchy in preview.
- [x] RED browser: desktop sticky sidebar/4 columns, no rightsidebar, images square/contain, buttons aligned. Mobile768/390/320 filters accessible with no document overflow, controls44px, noJS, four themes/designs; price not split. Existing gallery/cart/events intact.
- [x] Implement styles and progressive toggle, preview consistent. GREEN browser and relevant portal suite, commit.

### Task 3: Entrega37 acumulativa34/35/36
Files: docs/manual/version/CAMBIOS/checklist/tests and PDFprincipal; scripts instalar/paquete/test_* v37 and releaseinventory. Preserve all prior included portal improvements; no Urban changes required by catalog.
- [x] Tests/source compatibility Python3.7, installer dryrun/apply/recovery on verified bases34/35/36, inventory/PDFjoin and ZIPvscommit; expected all PASS.
- [ ] One independent wholebranch review; Important/Critical RED→GREEN, minors/rulings recorded. Commit and publish GitHub; verified ZIP to Downloads and full cPanelcommands with Urban628; no production installation or campaigns.
