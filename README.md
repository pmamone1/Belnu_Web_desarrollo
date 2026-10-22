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

# MiDistri - Pedidos Online v2
Contraparte de Urban Soft v580. Catálogo por distribuidora, precio vendedor y PVP, acceso personal sin registro, pedidos sin pago online.
Base10b49c4 y propuesta2eea423 adaptada. Python3.7/Django3.2, requests existente. Instalación productiva pendiente.
Ver docs/INSTALACION_MIDISTRI_PEDIDOS.md, docs/MANUAL_USUARIO.md y docs/VALIDACION_INTEGRACION.md.
No copiar paquetes, settings ni credenciales Urban a este repositorio.
