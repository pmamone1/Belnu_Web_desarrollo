# Catálogo con más espacio · MiDistri-Pedidos v46

## Guía de uso

### Ver más productos en escritorio
El catálogo ocupa casi todo el ancho de la pantalla. Los filtros y las promociones siguen a la izquierda; a la derecha hay más espacio para las tarjetas. En pantallas anchas entran más productos por fila. Si elegís el diseño en lista, cada producto sigue ocupando una fila.

### Usar el catálogo en el celular
Los márgenes son más chicos. El botón de filtros, el buscador y el acceso Kanji se usan igual que antes.

## Detalle técnico

- Base MiDistri-Pedidos v45, con 0016_publicacion_abastecimiento aplicada. No hay cambios de esquema ni sincronización adicional. Se conserva la selección de ofertas, sus precios, las existencias y el orden por tienda.
- Los márgenes adaptan su ancho entre 10 y 24 px. Los diseños en tarjetas añaden columnas a partir de 1640 px y 2180 px. El diseño en lista y las pantallas de administración conservan su presentación.
- Instalar sobre v45, con plan de migraciones vacío. El instalador respalda los archivos, recopila los estáticos y recarga MiDistri. Para restaurar, usar `instalar.py --root /home/mcollini/belnuweb --restore <respaldo>`, que restaura código y recopila la versión anterior de los estáticos.
- Validar el catálogo en escritorio y celular, la vista en lista, los filtros y la versión de la hoja de estilo. No es necesario generar pedidos ni enviar campañas.
