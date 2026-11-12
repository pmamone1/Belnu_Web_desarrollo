# Disponibilidad de Kanji · MiDistri-Pedidos v47

## Guía de uso

### Navegar el catálogo
Se muestran los artículos de Kanji que el proveedor informa como disponibles. El resto no aparece en las páginas del catálogo, sus destacados ni en los banners que usan esos productos.

### Buscar un artículo sin disponibilidad
Buscá por nombre o SKU. Podés ver la ficha, fotos y precio, pero no hacer un pedido de ese artículo desde MiDistri, aunque figure stock en depósito. Si estaba en un carrito, podés quitarlo. Cuando Kanji informa disponibilidad de nuevo, el artículo vuelve a aparecer en el catálogo. Los pedidos ya registrados conservan su historial.

## Detalle técnico

- Base v46 con 0016_publicacion_abastecimiento aplicada. No se cambia el contrato de sincronización, el esquema, los datos de producto, el precio ni el alcance de cada distribuidora.
- El listado público y la vista previa excluyen publicaciones de proveedor con disponible falso. Las búsquedas conservan esas fichas y su aviso, incluso en el orden de ventas. Los destacados y los banners basados en fichas omiten estos artículos sin editar su configuración.
- La validación del carrito rechaza cantidades positivas para esos productos y permite quitar un renglón. Los pedidos previamente registrados mantienen el circuito existente.
- La instalación respalda los archivos reemplazados. El plan de migraciones debe estar vacío. Para volver a v46, usar `instalar.py --root /home/mcollini/belnuweb --restore <respaldo>`. No se necesitan cambios de Urban Soft ni tareas adicionales de sincronización.
- Verificar catálogo, búsqueda, destacados, vista previa y carrito en una base de prueba, incluyendo artículos sin disponibilidad que tengan stock local y cambios de disponibilidad después de revisar el carrito.
