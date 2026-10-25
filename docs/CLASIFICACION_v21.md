# MiDistri-Pedidos v21 - Clasificación del catálogo

## Guía de uso
1. Urban Soft mantiene una categoría principal para Analítica y categorías adicionales para encontrar el mismo producto. En MiDistri el filtro Categoría incluye ambas. No aparecen copias del producto ni se multiplica el importe del pedido.
2. Buscar por nombre, código, categoría o subcategoría. Reconoce acentos, plurales y errores leves en palabras: alfajor y alfajro encuentran productos en Alfajores aunque su nombre no contenga esa palabra. Todos los términos se deben encontrar. Los números no se aproximan a otros códigos.
3. La tarjeta muestra las categorías y, si existe, la subcategoría pública. Sólo se sincronizan clasificaciones activas; costos privados no se publican. Filtros, conteo, orden de precios/ventas y paginación se conservan.
4. Las altas, bajas y cambios públicos se actualizan con la sincronización actual cada5min, después de guardar Urban Soft. No modificar el cron ni volver a enviar campañas. Producto inactivo, sin foto pública o sin precios válidos no aparece.
5. Precio vendedor y PVP siguen visibles. El importe se calcula al precio vendedor; se mantienen múltiplos de display, controles móviles, historial y referencia del pedido.

## Detalle técnico
Publicacion.clasificacion JSON opcional mediante migración midistri_portal0011. Contrato raíz opcional clasificacion={categorias:list[str],subcategoria:str}; campo anterior categoria se mantiene. Los datos anteriores sin clasificacion conservan su principal y subcategoría vacía. Campos privados/desconocidos en clasificacion, tipos incorrectos, duplicados y ausencia de principal anunciada rechazan el snapshot completo y conservan la última copia válida. No se cambia el contrato de indicadores ni orden_ventas.
El filtro se realiza sólo sobre publicaciones elegibles de la tienda seleccionada o de la sesión validada. Búsqueda y lista de categorías incluyen las adicionales sin cruzar tiendas. Sin nueva dependencia; compatible con Python3.7/Django3.2/MariaDB. No tocar cuentas legacy ni sus formularios.

## Migración, compatibilidad y rollback
Base portal20 y esquema0010. Instalar primero Urban604 (su campo nuevo es ignorado por portal20), luego portal21 y sincronizar. Aplicar únicamente0011; no modificar migraciones anteriores. Instalar no cambia pedidos, importes, SMTP, WhatsApp, conexiones, venv o variables. Después de aplicar0011 el instalador bloquea restauración ciega de código; corregir hacia adelante, nunca revertir datos comerciales. Antes de migrar puede restaurar archivos verificados de su respaldo.
La rutina de sincronización y su cron5min siguen iguales. No enviar campañas ni usar producción como prueba. Instalación productiva y aceptación HTTPS pendientes de confirmación.
