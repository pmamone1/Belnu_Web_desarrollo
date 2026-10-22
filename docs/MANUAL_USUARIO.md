## MiDistri Pedidos Online v3 - corrección de formularios MiDistri
Corrige el403 CSRF provocado por Referrer-Policy:no-referrer en formularios.
Se usa same-origin: conserva la referencia interna, sin enviarla a otros sitios.
CSRF, autenticación, alcance y permisos se conservan. No hay migraciones,
cambios de importes, datos históricos, claves, venv, cron ni habilitación de envíos.
Instalación productiva pendiente. Requiere MiDistri v2 instalada.
Ver [detalle](CSRF_PORTAL_v3.md) y [validación](VALIDACION_v3.md).

# MiDistri: guía de operación
## Urban Point
1. En Urban Soft, Urban Point > MiDistri · Catálogo, crear una conexión y elegir distribuidoras.
2. Guardar la clave mostrada una sola vez en el cPanel de MiDistri, no en mensajes ni planillas.
3. Buscar productos, elegir proveedor y distribuidora, marcar y publicar. Elegir20/65 incluye ambos
   dentro del alcance permitido. Retirar una publicación no elimina productos ni pedidos anteriores.
4. Pedidos y datos personales sólo aparecen en el ámbito privado autorizado, con excepción de SuperUsuario.

## Distribuidora
1. Comunicaciones > MiDistri · Pedidos online. Buscar y elegir vendedor.
2. Elegir conexión. Crear enlace para copiar/WhatsApp, o seleccionar un contacto Email habilitado,
   escribir el Email exacto y enviar. Enlace personal válido48h; no publicarlo.
3. Pedido recibido: revisar detalle. Marcar OK permite incluirlo en Excel para depósito con LIN/VV.
   Estos pasos no cobran al vendedor. Si falta stock, cancelar antes de confirmar preparación.
4. Cuando esté preparado, un usuario con autorización financiera pulsa
   Confirmar preparación, generar cargo y remito. No hace falta repetir ante doble clic.
5. Abrir el remito emitido; es copia del documento nativo. Reenvíos de Email no debitan otra vez.
6. Revisar avisos: pendiente puede procesarse; aceptado significa aceptación SMTP, no lectura.
   Por conciliar/enviando exige revisar proveedor. Si un proceso fue interrumpido, esperar15min.
   Conciliar con motivo permite registrar aceptación o dejar pendiente sólo si consta que no se envió.
   La conciliación no envía Email ni altera la cuenta.

## Vendedor
Abrir enlace y tocar Entrar. El portal muestra su distribuidora, LIN/VV, productos activos,
precio vendedor y PVP. Elegir cantidades, revisar precios y enviar. No se paga en el portal.
Consultar Mis pedidos, estados y remito al estar preparado. Ante fallo de conexión, reintentar
el pedido guardado; no volver a armarlo para evitar solicitudes distintas.
Si cambió precio o se retiró un producto, revisar nuevamente antes de confirmar.
No se necesita cuenta administrativa ni registro público. El acceso puede revocarlo su distribuidora.
