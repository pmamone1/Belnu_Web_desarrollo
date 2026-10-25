# MiDistri-Pedidos v18 — Editor y pedidos

## Guía de uso

1. El carrusel muestra sólo flechas laterales. Con una sola foto no hay flechas. Se pausa al enfocar o pasar el puntero; al salir continúa si tenía rotación automática. El teclado admite flechas y Espacio sobre el carrusel para pausar/reanudar; respeta movimiento reducido.
2. El editor muestra el cabezal comercial real y la página completa. Seleccioná un bloque a la izquierda para desplazarte hasta él y resaltarlo. Página completa permite ver el conjunto a escala; Vista de edición recupera el tamaño de trabajo. Ver cabezal vuelve arriba. El porcentaje de zoom se indica.
3. Agregar bloques incluye Banner lateral izquierdo/derecho. Elegí fotos del catálogo o subí material propio y configurá un enlaceHTTPS. Lugar en página permite cambiarlo después. En celular se integra o se oculta según la opción del bloque.
4. En un banner o carrusel, indicá entre 1 y 20 productos y tocá Elegir productos al azar. Se eligen productos distintos del catálogo autorizado, activos, con foto y precios válidos. Reemplaza las fotos sólo de ese bloque en el borrador; permite Deshacer. No varía silenciosamente en cada visita: revisá y publicá cuando te guste.
5. Guardar por AJAX no publica. Revisar y publicar conserva su confirmación. El catálogo y los precios no se editan como texto del banner.
6. Si el producto informa display, el precio vendedor y PVP aclaran «x unidad» en letra menor. Un display de 6 permite pedir6,12,18; botones y campos usan ese paso. Sin display se pide de a una unidad. No se redondea automáticamente; un carrito antiguo inválido debe corregirse antes de enviar.
7. El total se calcula por unidades y precio vendedor, no por display. La distribuidora puede confirmar cantidades menores por disponibilidad mediante su circuito de revisión; el vendedor recibe el detalle final del pedido.
8. Una anulación posterior en Urban se informa por Email y en el historial. El pedido puede quedar cancelado completo o seguir con una parte vigente; el total y PDF vigente reflejan esa situación. La solicitud original y sus precios históricos se conservan.

## Instalación y operación técnica

Requiere Urban 601 primero. Paquete acumulativo sobre portal16 o17. Sin migraciones/modelos nuevos en portal, sin variables o dependencias nuevas. Mantiene sesión, SSO, permisos y alcance por distribuidora, remitentes y WhatsApp. La instalación no publica el borrador ni envía Emails/campañas.

Vista previa: iframe sin scripts con altura de contenido completo y lienzo desplazable; escala según viewport1280/390 o encuadre completo. Selección usa coordenadas escaladas, catálogo/contacto tienen marcadores de navegación. Se conserva autosave, UUID/replay, freeze, undo y firma. Flechas en la vista previa pueden cambiar la diapositiva sin activar enlaces.

Acciónaleatorio valida permiso/tienda antes de consultar, exige entero1..20, deduplica por publicación y toma sólo fotos de publicaciones elegibles. No guarda ni publica; client incorpora el resultado mediante edición normal. Recursos combina fotos y videos sin perder imágenes cuando un producto tiene video.

Display se valida en catálogo/carrito/checkout y en Urban; la firma incluye el paso actual. Reintento de un PedidoLocal existente conserva snapshot e idempotencia. Historial admite metadata de anulación tipada (motivo de 5 a 2000, fecha con zona, estado coherente) y atención efectiva sin modificar originales. Importes continúan por unidad.

Rollback de código al respaldo16/17 compatible con el mismo JSON de página y esquema. La validación de cantidades permanece en Urban 601 aunque se restaure portal anterior. No revertir datos, precios o documentos. Guardas de fuente/hashes impiden reemplazar archivos ajenos. Conservar salida/respaldo ante error.

## Validación

Ver VALIDACION_v18.md. Instalación productiva y aceptación HTTPS pendientes. MiDistri-Puntos sigue sólo en análisis. Sin campaña.
