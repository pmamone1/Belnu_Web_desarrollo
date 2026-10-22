## MiDistri Pedidos Online v3 - corrección de formularios MiDistri
Corrige el403 CSRF provocado por Referrer-Policy:no-referrer en formularios.
Se usa same-origin: conserva la referencia interna, sin enviarla a otros sitios.
CSRF, autenticación, alcance y permisos se conservan. No hay migraciones,
cambios de importes, datos históricos, claves, venv, cron ni habilitación de envíos.
Instalación productiva pendiente. Requiere MiDistri v2 instalada.
Ver [detalle](CSRF_PORTAL_v3.md) y [validación](VALIDACION_v3.md).

# Checklist MiDistri v2
- [ ] Tests portal/instalador, sintaxis3.7 y paquete verificados.
- [ ] Comunicación HTTP sintética revisada.
- [ ] ZIP sin credenciales/DB/media/venv y commit publicado.
- [ ] Instalación productiva y piloto: pendientes de ejecución autorizada.

QA22/10: pruebas focalizadas y recuperación de instalador verificadas; ver documento de validación. Publicación del código no confirma instalación. Flags, cron, SMTP y validación en motores/runtime productivos siguen pendientes.

Corrección de referencia: RED reproducido, GREEN focalizado e instalador9/9. Manual PDF y unión revisados. Instalación productiva y piloto pendientes; no declarar publicaciones ni claves creadas.
