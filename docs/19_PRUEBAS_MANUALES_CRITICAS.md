## Pruebas v6

En datos sintéticos: pedir10 a$25.000 y2 de otro producto; preparar6 del primero y0 del segundo. Esperado: cargo$150.000, canceladas4+2, un PDF sin el segundo, original intacto. Repetir confirmación: sin duplicados. Cero todo: sin cargo/PDF. Alterar cantidades/revisión ajena/caducada: rechazar. Dos contactos activan a la vez sin revocarse; baja de uno lo excluye. Excel: pendientes0 para esa preparación, sin LIN/VV/contactos. Sin autorización65, ni pedidos ni exportación65. Revisar catálogo público y filtros sin acceso a pedidos personales.

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

# Pruebas manuales MiDistri
Comprobar móvil: enlace GET no consume, POST entra y muestra sólo catálogo de su distribuidora/LIN/VV.
Anónimo sólo ve PVP. Cambiar precio antes de envío exige revisar; conexión fallida conserva UUID.
Reintentar mismo pedido no duplica cargo; otro vendedor no ve pedido/remito. HTML de error no se descarga como PDF.
Comprobar cancelación stock y preparación con remito nativo. Flags/Email apagados no envían.


### Contrato v2 y recuperación
SKU80 debe sincronizar y regresar en el pedido recibido sin quedar pendiente. SKU81 se rechaza.
Verificar recuperación de copia parcial y rechazo de respaldo alterado.
Homologación real Python3.7 y motor del servidor pendiente; no se habilitan flags ni envíos al instalar.

### Control posterior de formularios CSRF
1. Obtener un formulario nuevo por GET después de instalar; no reenviar la página403.
2. Guardar con el navegador: catálogo/conexión en Urban y entrada/carrito en Portal.
3. Verificar que misma procedencia+token válido pasa y que sin token u origen externo se rechaza.
4. Revisar que ambos sistemas siguen apagados hasta configurar conexión y autorizar el piloto.
No generar cargos ni enviar Email para comprobar esta corrección.


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
