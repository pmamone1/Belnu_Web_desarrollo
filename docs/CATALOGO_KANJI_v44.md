# Catálogo Kanji · MiDistri-Pedidos v44

## Guía de uso

### Abrir el catálogo
Entrá al catálogo de tu distribuidora. Si tiene artículos del catálogo proveedor Kanji publicados, aparece el logo junto a Ver catálogo Kanji. Tocá el enlace para ver esos artículos. También podés elegir Kanji en Categoría y combinar el filtro con la búsqueda o una subcategoría.

### Ver todos los productos de Kanji
El enlace abre la primera página de Kanji y restablece la búsqueda y la subcategoría. Si hay varias páginas, usá los botones de navegación. Los artículos del catálogo proveedor conservan también su categoría original.

### Administrar la publicación
Los artículos aparecen al publicarlos para esa distribuidora desde Catálogo proveedor Kanji en Urban Soft y al actualizarse la copia del catálogo de MiDistri. Sólo se muestran los productos habilitados y con foto y precios completos. Cada distribuidora ve su propio catálogo.

## Detalle técnico

El contrato de MiDistri v43 usa Publicacion.abastecimiento con origen proveedor para las ofertas de la única fuente externa integrada, el catálogo proveedor Kanji. La categoría se agrega al presentar la copia de la tienda. No se usa el nombre o SKU para inferir el origen ni se persiste la categoría adicional. Si se integra otro catálogo externo en el futuro, habrá que distinguir su origen antes de reutilizar el campo para categorizarlo.

El acceso visible usa el logo original suministrado y genera la URL del catálogo con distribuidora, categoría Kanji y orden Relevancia, sin arrastrar la búsqueda ni la subcategoría anterior. La sesión de vendedor sigue determinando su distribuidora autorizada. La pestaña Kanji oculta los destacados generales para que el resultado sea el catálogo filtrado. La navegación conserva el filtro y el tamaño de página.

Base MiDistri v43 con 0016_publicacion_abastecimiento aplicada. Esta entrega no cambia el puente de Urban Soft ni requiere migraciones. El instalador compila archivos estáticos y no ejecuta sincronización. Se reutiliza la copia vigente y las actualizaciones normales del catálogo.

Para restaurar, usar el respaldo de archivos del instalador v44 y su opción --restore. Se vuelve a publicar el CSS anterior. El esquema y las copias históricas quedan intactos. Instalación productiva pendiente.
