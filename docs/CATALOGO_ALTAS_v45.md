# Altas del catálogo en sesiones abiertas · MiDistri-Pedidos v45

## Guía de uso

### Encontrar una publicación nueva
Después de que MiDistri actualice su catálogo, podés buscar el artículo por nombre o SKU o abrir su categoría. Ya no hace falta salir, volver a entrar ni cambiar el criterio de orden para verlo. Los artículos nuevos aparecen al final cuando recorrés el catálogo por Relevancia; los artículos que ya estaban conservan su orden.

### Consultar disponibilidad
Un producto publicado puede verse con su foto y precio aunque el proveedor no tenga stock. En ese caso, si tampoco hay unidades en depósito, el portal no permite agregarlo al pedido.

## Detalle técnico

- Base MiDistri v44 con la migración 0016_publicacion_abastecimiento aplicada. No se modifica el esquema, el contrato con Urban Soft, el carrito, las existencias ni el acceso del vendedor. No se requiere una sincronización nueva si los artículos ya están en la copia del portal.
- El orden de Relevancia se conserva por tienda, perfil y pestaña. Cada consulta concilia esa lista con los productos elegibles de la misma tienda antes de aplicar filtros. Se conservan las posiciones relativas, se quitan las ofertas retiradas y se anexan los ID nuevos al final, sin repetirlos. El buscador conserva la prioridad de coincidencias exactas. Esta regla reemplaza la indicación histórica que demoraba las altas hasta la próxima sesión.
- Para instalar sobre v44, usar el ZIP v45, verificar el plan de migraciones vacío, respaldar los archivos reemplazados y reiniciar sólo MiDistri. Para restaurar, usar `instalar.py --root /home/mcollini/belnuweb --restore <respaldo>`. Se restauran archivos sin revertir datos, sin recolectar estáticos ni invalidar sesiones.
- Validar con una sesión que ya tenga un orden guardado: publicar un SKU en la base de prueba y confirmar que aparece por búsqueda y categoría, que las posiciones relativas anteriores se conservan y que otra distribuidora no lo ve.
