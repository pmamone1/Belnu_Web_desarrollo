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
