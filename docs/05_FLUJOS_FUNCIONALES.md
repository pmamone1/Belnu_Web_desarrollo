## MiDistri Pedidos Online v3 - corrección de formularios MiDistri
Corrige el403 CSRF provocado por Referrer-Policy:no-referrer en formularios.
Se usa same-origin: conserva la referencia interna, sin enviarla a otros sitios.
CSRF, autenticación, alcance y permisos se conservan. No hay migraciones,
cambios de importes, datos históricos, claves, venv, cron ni habilitación de envíos.
Instalación productiva pendiente. Requiere MiDistri v2 instalada.
Ver [detalle](CSRF_PORTAL_v3.md) y [validación](VALIDACION_v3.md).

# Flujo MiDistri
Urban publica > portal sincroniza > distribuidora invita > vendedor entra por enlace > elige/revisa/envía > depósito recibe Excel > Urban confirma preparado/cargo/remito o cancela por stock.
Ante fallo se conserva el intento para reintentar. Un cambio de precio requiere revisión nuevamente.
