## Planificación MiDistri · pendiente de implementación

- [ ] Revisar plan principal y ejecutar sus subplanes.
- [ ] Verificar código/sesión, callback, contactos, multimedia y presentación en pruebas locales.
- [ ] Actualizar PDF principal, migraciones, instalador y ZIP del proyecto al completar la implementación.
- [ ] Publicar dos commits/PRs y entregar comandos separados; no enviar campaña.

Ver [diseño](superpowers/specs/2026-10-22-midistri-acceso-codigo-y-tienda-design.md) y [plan principal](superpowers/plans/2026-10-22-midistri-acceso-codigo-y-tienda.md).

## Checklist v6

- [ ] Usuario confirma instalación P6 y luego U584 en sus runtimes y raíces separados.
- [ ] Confirmar check/reinicio y ausencia de migraciones nuevas de MiDistri; no inferir instalación de VERSION.
- [ ] Validar catálogo público con precio vendedor/PVP y filtro; permisos de20/65.
- [ ] Validar preparación parcial, cero, reintento, PDF y resumen sin identidad en entorno de pruebas.
- [ ] Controlar remitente/bajas por contacto sin enviar campaña existente.
- [ ] ZIP/commit, manualPDF y validación incluidos; ningún secreto, base, media o venv.
- [ ] Registrar instalación y contador de respaldos sólo después del recibo productivo.

## MiDistri-Pedidos v5 — presentación opcional del catálogo

La sincronización admite Display0 de Urban como presentación no informada.
Se conservan fotos, precios, PVP y permisos. Sin nuevas migraciones ni cambios
en Urban. Después de instalar v5, actualizar la copia del catálogo desde el panel.
Instalación productiva pendiente. Ver [guía v5](DISPLAY_CERO_v5.md).

## MiDistri-Pedidos v4 - Panel de Distribuidor
Instalación pendiente; requiere Urban Soft v583. Entrada desde Urban Soft con
permisos y alcance actuales, sin cuenta staff adicional. Productos y pedidos,
publicación completa con previa y presentación propia por tienda. Precio vendedor
y PVP desde Urban. Migración aditiva0003. Habilitación administrativa explícita;
no publica catálogo ni envía Email al instalar.
Ver [guía vigente](PANEL_DISTRIBUIDOR_v4.md) y [validación](VALIDACION_v4.md).

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


## Verificación manual de MiDistri operativo (v583 / portal v4)

- Entrar con un Distribuidor autorizado desde Pedidos > Administrar MiDistri-Pedidos.
  Verificar que no aparezcan tiendas ajenas. 20 incluye65 sólo si ambas están autorizadas.
- Quitar un permiso o desactivar al operador durante la sesión: la siguiente acción
  debe bloquearse. Urban Point ordinario no accede a datos privados.
- Publicar catálogo completo: revisar resumen por tienda, proveedor y exclusiones.
  Confirmar una vez; repetir confirmación no debe duplicar publicaciones.
  Ocultar un producto debe preservar pedidos anteriores. Precio cero/negativo se
  muestra para corregir en Urban y no se publica como precio válido.
- Guardar logo/contacto/mensajes y verificar tienda del vendedor. Una edición
  concurrente debe pedir recarga. Una caída del acuse no debe repetir el guardado.
- Pedido: revisar y Excel no generan cargo. Recibido > OK > revisión de preparación >
  confirmación genera un único pedido/cargo/remito. Cancelar sólo antes de emitir.
- Campaña de acceso: todos, líneas y uno; revisar Email, LIN, VV y excluidos.
  Sin confirmar no debe haber invitaciones. Dos vendedores con un mismo Email
  reciben enlaces diferentes; respetar bajas y remitentes por distribuidora.
- Desactivar envío, revocar conexión/contacto/permiso: no debe enviarse el acceso.
  Un SMTP incierto requiere conciliación, sin reenvío automático.
- Verificar con HTTPS real tras instalación: intercambio entre sitios, expiración,
  cookies Secure/HttpOnly, escritorio y móvil. Esto permanece pendiente en cPanel.
- Instalación: los paquetes rechazan destino/base/plan ajenos. --restore después de
  migrar debe detenerse antes de modificar código; usar corrección hacia adelante.

Validación v5: sincronizar un catálogo sintético con Display0, comprobar fotos y ambos precios, ausencia de presentación0, separación20/65 y conservación de copia previa ante texto/booleano/negativo. En cPanel revisar sincronización real después de instalar; no generar pedidos de prueba en producción.
