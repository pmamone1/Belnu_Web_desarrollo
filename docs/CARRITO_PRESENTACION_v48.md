# Presentación del carrito · MiDistri v48

## Guía de uso

### Ver cuántas unidades llevás
Desde el catálogo o Mis pedidos, el ícono de carrito junto a Ver mi pedido muestra el total de unidades. Por ejemplo, tres unidades de un producto y dos de otro se ven como 5. Al entrar al carrito, la misma cifra figura junto a Revisá tu pedido.

### Configurar el mensaje
Entrá a Configurar MiDistri, elegí la distribuidora y buscá Presentación del carrito en Diseño y mensajes de la tienda. Podés editar el título y el texto, o desmarcar Mostrar el bloque en el carrito. La vista previa cambia a medida que escribís. Para aplicarlo, usá Revisar y publicar.

### Qué muestra por defecto
Tu próximo pedido empieza acá. Hacé tus pedidos directo a tu distribuidora. La mercadería es consignada y tus pedidos tienen derecho a devolución, salvo casos especiales.

## Detalle técnico

La presentación del carrito es un bloque opcional en el JSON de la página por distribuidora (`presentacion_carrito`). Los borradores y las versiones que no lo tienen muestran el texto predeterminado sin cambiar su JSON ni su huella. Los valores nuevos se validan en el servidor: visibilidad booleana, título de hasta 150 caracteres y texto de hasta 1.000, ambos obligatorios cuando está visible. Se muestran como texto plano. Se usa el permiso existente de configuración y se conserva el circuito borrador/revisión/publicación.

La insignia se alimenta del carrito de la sesión del perfil activo, con su aislamiento existente por pestaña. Cuenta unidades, no renglones. Se actualiza al aplicar la cantidad; no incluye cambios que el vendedor todavía no guardó. El aviso es informativo: no cambia elegibilidad para devoluciones, precios, pedidos, remitos ni liquidaciones.

Base de instalación: MiDistri v47, con `0016_publicacion_abastecimiento` ya aplicada. No hay migraciones, cambios en Urban Soft, cron ni envíos. El instalador conserva respaldo de archivos y verifica hashes antes de reemplazar. Para revertir, restaurar código y estáticos del respaldo y recargar la aplicación. Si una tienda llegó a publicar el bloque, el campo queda conservado en los históricos; la v47 lo ignora. Para editar/restaurar esas versiones con su bloque, reinstalar la v48 antes de tocarlas.
