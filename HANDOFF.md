## Planificación MiDistri · 22/10/2026 · sin implementar

Código de ingreso de 30 minutos, sesión por pestaña, recuperación del acceso Distribuidor, campañas configurables y galerías/tienda. Diseño conversacional aprobado; implementación y paquetes pendientes de revisar el plan. No se envió la campaña ni se modificó código de aplicación. Ver [diseño](docs/superpowers/specs/2026-10-22-midistri-acceso-codigo-y-tienda-design.md) y [plan principal](docs/superpowers/plans/2026-10-22-midistri-acceso-codigo-y-tienda.md).

## Entrega MiDistri v6 · 22/10/2026

Instalación productiva pendiente. Base v5; instalar P6 antes de U584. Sin migraciones MiDistri nuevas. Runtimes separados: belnuweb Python3.7; Urban Python3.10. No enviar campaña. Conservar templates/accounts/forgotPassword.html ajeno a esta entrega; no incluirlo. Restauración a v5 bloqueada si Urban anuncia contrato nuevo o no puede comprobarse. [Guía](docs/PEDIDOS_PARCIALES_v6.md) y [validación](docs/VALIDACION_v6.md).

## MiDistri-Pedidos v5 — presentación opcional del catálogo

La sincronización admite Display0 de Urban como presentación no informada.
Se conservan fotos, precios, PVP y permisos. Sin nuevas migraciones ni cambios
en Urban. Después de instalar v5, actualizar la copia del catálogo desde el panel.
Instalación productiva pendiente. Ver [guía v5](docs/DISPLAY_CERO_v5.md).

## MiDistri-Pedidos v4 - Panel de Distribuidor
Instalación pendiente; requiere Urban Soft v583. Entrada desde Urban Soft con
permisos y alcance actuales, sin cuenta staff adicional. Productos y pedidos,
publicación completa con previa y presentación propia por tienda. Precio vendedor
y PVP desde Urban. Migración aditiva0003. Habilitación administrativa explícita;
no publica catálogo ni envía Email al instalar.
Ver [guía vigente](docs/PANEL_DISTRIBUIDOR_v4.md) y [validación](docs/VALIDACION_v4.md).

## MiDistri Pedidos Online v3 - corrección de formularios MiDistri
Corrige el403 CSRF provocado por Referrer-Policy:no-referrer en formularios.
Se usa same-origin: conserva la referencia interna, sin enviarla a otros sitios.
CSRF, autenticación, alcance y permisos se conservan. No hay migraciones,
cambios de importes, datos históricos, claves, venv, cron ni habilitación de envíos.
Instalación productiva pendiente. Requiere MiDistri v2 instalada.
Ver [detalle](docs/CSRF_PORTAL_v3.md) y [validación](docs/VALIDACION_v3.md).

# Handoff MiDistri v2
Destino exclusivo belnuweb/Python3.7. Base confirmada10b49c4. Propuesta previaPR2 conservada y endurecida con validación de respuesta/propietario/PDF y LIN/VV.
Datos/base/store anteriores intactos; migra sólo midistri_portal0001–0002. No hay instalación ni envíos productivos.
