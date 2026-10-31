# Indicadores de analítica desplegables

Diseño aprobado en chat el31/10/2026: botones con detalle debajo del resumen, en la misma pantalla; implementar, revisión final y paquetes/GitHub; sin campañas.

Cada una de las nueve cifras abre un panel debajo del resumen: consultas de producto (acciones con vendedor/producto/SKU/fecha), productos distintos (una fila por producto), vendedores con actividad, visitas distintas (primera/última acción registrada y participantes), ingresos (incluido recordado), fotos ampliadas, videos/enlaces, pedidos y conversión (vendedores con actividad, con/sin pedido). Los totales/detalles deben conciliar exactamente con el resumen; sin cambiar la definición existente de venta/pedido o conversión.

El panel usa el mismo período, corte y alcance acreditado de la consulta. No aplica los filtros de las tablas inferiores porque el resumen tampoco los aplica; decirlo expresamente. Incluir vendedores históricos/inactivos con actividad en el corte. Producto distinto se cuenta por producto_id como el resumen, sin duplicarlo por20/65. Visitas se cuentan por UUID de visita; no son ingresos y primera/última acción no acredita tiempo de permanencia. Un video abierto no acredita reproducción completa.

AJAX con indicador de carga, estado accesible, cerrar detalle, paginación50 y manejo de error/caducidad. Conservar el resultado anterior identificándolo si falla una carga. Ignorar respuestas fuera de orden; cerrar durante carga cancela la actualización visible. Enlaces funcionales sin JS para abrir/paginar/cerrar. No descargar eventos de sesión, emails o tokens; mostrar sólo datos necesarios ya autorizados.

Cada petición valida operador, permisos, propietario, tiendas y vencimiento. No cambiar timestamps/intervalos/captura, snapshots/históricos, precios o pedidos. Sin migraciones ni envíos. Reutilizar informes; añadir datos base del resumen antes de filtros y un módulo separado que proyecte filas paginadas. Conservar Excel y fichas existentes.

Enfoques considerados: ventana superpuesta o detalle bajo el resumen. Elegido por el usuario: debajo, evitando tapar el período y permitiendo revisar las tablas en la misma vista. Implementación nativa en el proyecto, sin dependencias nuevas.

Entrega acumulativa MiDistri34 sobre32/33 y Urban626 sobre624/625 (acompañamiento documental, sin cambios de lógica Urban). Conservar compatibilidad e instaladores/hashes de versiones anteriores. Manuales PDF con capítulo vigente delante, ZIP separados e inventario explícito. Instalación productiva pendiente; no activar campañas ni incentivos. Rollback sólo de archivos nuevos/reemplazados, sin reversión de datos; rigen las limitaciones de edición de estilos al retroceder a32.

## Aclaraciones incorporadas por el usuario

Mostrar spinner al cambiar/guardar en editor y actualizar previa; desaparece al terminar o fallar, conserva edición concurrente y spinner de publicación. Destacar Estadísticas de vendedores como botón visible en la navegación administrativa, con los mismos permisos. Ambos pedidos se incorporaron durante la ejecución de esta versión, sin campañas.

## Detalle de interés por producto y lectura del catálogo
El usuario añadió: ampliar cada producto para ver vendedores, cantidad de vendedores y cuántos pidieron respecto de las vistas, además de sugerencias de análisis del catálogo. Mostrar nombres sin LIN/VV en la tabla de vendedores; mantener búsqueda. Retirar Banners y promociones porque su ruta ya redirige al mismo editor, sin quitar rutas ni datos.
Interés registrado incluye consulta de producto, foto ampliada y video/enlace; visitantes únicos por distribuidora/vendedor. Consultas de producto se muestran separadas. Conversión de vendedores = únicos con pedido del mismo producto posterior a primera interacción registrada / únicos con interés. Pedidos cancelados y anteriores no cuentan como conversión; pedidos son solicitudes, no cobros. La asociación temporal no prueba causalidad. Mostrar también pedidos posteriores / consultas, que puede superar100% si hay varios pedidos. Si hay pedidos no cancelados sin desglose, las tasas quedan por determinar, sin falsos ceros. No usar productos actuales o importes para reconstruir snapshots.
Enriquecer tabla Interés en productos con vendedores/interés, pedidos posteriores y conversión; el producto abre el mismo panel de detalle debajo del resumen. Identidad por tienda respetada y filtro de ficha mantenido. Las tasas consideran el período completo de interacciones de ese producto, no el tipo de acción elegido en el historial; explicitarlo. Dar recomendaciones de lectura/acciones posibles y limitaciones, sin agregar captura o campañas automáticas ni afirmar atribución de ventas.
