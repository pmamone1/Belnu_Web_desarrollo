# Integración MiDistri Implementation Plan

> **For agentic workers:** ejecutar inline con superpowers:executing-plans. Pasos verificables antes de publicar.

**Goal:** catálogo por distribuidora y pedidos móviles sin registro ni pago.
**Architecture:** Urban recibe solicitudes y emite pedidos nativos; MiDistri presenta copia sincronizada y conserva reintentos.
**Tech Stack:** Urban Django 5.x; MiDistri Django 3.2 / Python 3.7; HTTP JSON y reportlab/openpyxl en Urban.
**Spec:** docs/integracion_urban_soft_diseno.md

## Global Constraints
- Dos repositorios y dos entregas, sin compartir bases ni settings.
- No stock, reservas ni cobro online. Precio vendedor único; solo productos activos.
- Recepción/Excel no debitan. Emisión transaccional, auditable e idempotente.
- Línea y nombre en Excel; sin matrícula.
- Enlaces con vencimiento/un uso; GET nunca activa.

## Review Focus
- Reintentos, doble envío, concurrencia: una solicitud/un cargo.
- Cambio o baja del vendedor y distribuidora: revocar acceso.
- Productos desactivados/cambio de precios: rechazar compra silenciosamente distinta.
- Fallo API/email: conservar pedido y permitir reintento sin duplicar saldo.
- Catálogo viejo y rutas legacy: no publicar productos ajenos a Urban.

### Task 1: Urban API y operaciones
Files: nueva app midistri_bridge (models, api, services, views, urls, tests, migrations, templates); sistema7000/settings.py, urls.py; middleware/políticas.
Interfaces: GET snapshot (aplicación autorizada); POST activate/profile/orders/status; consola móvil staff /midistri/.
- [x] Tests de segregación, activación, precios, no saldo al recibir, idempotencia y emisión.
- [x] API con credencial de aplicación; modelos aditivos; solicitudes y snapshots; consola móvil y Excel.
- [x] Tests de las operaciones y migraciones.

### Task 2: Portal móvil
Files: nueva app midistri_portal (models, client, views, urls, templates, tests, migrations, management); settings y middleware legacy.
Interfaces: consume API anterior; sesión propia de vendedor; catálogo local.
- [x] Tests de activación POST, catálogo exclusivamente Urban, distribuidora fija, envío y reintento.
- [x] Catálogo móvil, carrito, pedidos, repetición, gestión y sync.
- [x] Compatibilidad Python 3.7, manifiesto estático y tests Django 3.2.

### Task 3: Entrega coordinada
Files: docs técnicas/manual/checklist/version/cambios de Urban; instrucciones MiDistri; paquetes separados.
- [x] Revisión independiente y corregir fallos importantes.
- [x] Verificar instalación aislada/migraciones sin cambios y suites pertinentes.
- [ ] Publicar commits/PR separados y ZIP con destinos explícitos. No instalar producción desde este entorno.
