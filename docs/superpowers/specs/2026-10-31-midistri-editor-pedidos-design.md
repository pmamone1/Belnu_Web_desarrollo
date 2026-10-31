# MiDistri: edición de mensajes y pedidos desplegables

Diseño aprobado por el usuario el 31/10/2026: estilos independientes por mensaje y avanzar con los cambios propuestos, sin campañas.

## Intención y decisiones
Quitar Acceso Distribuidor del encabezado público y su campo en el editor. La administración conserva sus rutas, permisos y acceso desde Urban Soft.
Eliminar bloques promocionales y de mensajes del borrador, con Deshacer/Rehacer y conservación de versiones publicadas. Catálogo y contacto son componentes protegidos.
Cada mensaje (incluidos encabezado, navegación Catálogo y botón del pedido) admite tamaño14–56px, fuente entre Sistema/Arial/Georgia/Verdana/Monoespaciada, color de letra y fondo hex; sin CSS/HTML arbitrario. Sin estilo explícito conserva la apariencia previa. Se guarda por AJAX y se muestra en la previa; publicar sigue siendo explícito.
El borrador y su render pueden contener referencias retiradas para permitir corregirlas. Mostrar advertencia con bloque y diapositiva; no se publican fuentes retiradas ni se exhiben en el catálogo. No modificar ni eliminar materiales automáticamente.
Mis pedidos del vendedor: tabla por número, fecha, importe y estado. Botón accesible por fila despliega productos, SKU, cantidades solicitadas, aceptadas/preparadas, canceladas o pendientes, motivo y remito. No afirmar entrega sin remito. Respetar alcance por vendedor/distribuidora; indicar copia guardada si falla actualización. PC y celular sin cortar contenido.

## Enfoques
Elegido: estilos independientes, frente a un estilo general menos flexible. Tabla con detalle bajo cada fila, frente a tarjetas extensas actuales. Reutilizar snapshots validados y las rutas actuales, sin migraciones ni cambios económicos o de autenticación.

## Compatibilidad y entrega
Urban625 sobre624: documentación y compatibilidad del editor; sin cambios del contrato remoto de publicación, cron ni campañas. MiDistri33 sobre32: JSON opcional estilos_mensajes, sin reescribir versiones o huellas anteriores. Rollback de código con respaldo privado; estilos nuevos quedarían conservados en JSON pero no visibles en código viejo. No retroceder migraciones ni editar históricos.
Pruebas locales de validación/alcance, borrador con material retirado, publicación bloqueada, pedidos totales/parciales/cancelados y pantallas PC/celular. Manuales y ZIP separados, hashes y commits reales; instalación productiva pendiente. No activar sugerencias ni enviar campañas.
