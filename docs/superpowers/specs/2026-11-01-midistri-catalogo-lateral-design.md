# MiDistri: catálogo con filtros y promociones a la izquierda

Fecha: 01/11/2026. Diseño aprobado por el usuario el01/11/2026; implementación en curso.

## Intención y elección
El usuario quiere una presentación similar a https://urbanpoints.com.ar/productos: filtros permanentes a la izquierda, imágenes amplias, tarjetas ordenadas y orden Relevancia. Eligió reunir filtros y promociones en el lateral izquierdo; se conservan los banners centrales. Se consideraron promociones encima/debajo del catálogo y dos laterales: la primera opción aleja el material de los filtros y la segunda reduce demasiado las fotos. Se elige una sola columna lateral.

## Distribución propuesta
En PC: un lateral de aproximadamente 260–288 px, fijo durante el recorrido del catálogo mediante posición sticky, bajo el encabezado. Categoría, subcategoría, filtros activos y Limpiar arriba; todas las promociones laterales debajo, respetando orden y visibilidad guardados. Se conservan sus enlaces. Un lateral largo tendrá desplazamiento accesible, sin impedir llegar al pie. Los banners centrales mantienen su ubicación y configuración.
A la derecha: búsqueda, cantidad de resultados, Ordenar por y cantidad por página; luego tarjetas con imagen completa cuadrada, SKU pequeño, nombre, precios legibles, marcas y controles de pedido alineados al pie. Cuatro columnas cuando el ancho permita tarjetas de al menos unos 210–230 px, tres en anchos intermedios y dos en celular desde 390 px; una en pantallas menores si los controles no caben. Estos umbrales son una propuesta de implementación que se verificará con nombres largos y displays.
En celular el lateral se convierte en un panel de Filtros y promociones que puede abrirse/cerrarse; búsqueda y orden siguen visibles. Sin JavaScript los filtros y promociones permanecen accesibles en el flujo normal. Controles táctiles de al menos 44 px, foco visible, etiquetas y estado de apertura.

## Relevancia y navegación
El rótulo Recomendados pasa a Relevancia sin cambiar su valor URL ni el criterio vigente: ventas netas consignadas acreditadas y variedad. Una ayuda breve lo explica; no se cambian ventas por pedidos firmes. Se conserva el orden fijo por sesión, distribuidora y perfil al paginar, buscar, filtrar y volver del carrito; una búsqueda prioriza coincidencia/similitud y sólo desempata con ese orden. Se mantienen Más vendidos, nombre y precios.
Propuesta de implementación: 48 productos iniciales por página, opciones 24/48/96/192 y paginación visible arriba y abajo. Validar valores en servidor y conservar filtros/orden/tamaño de página al navegar; cambiar un filtro vuelve a página1. Mantener compatibilidad con enlaces actuales sin tamaño, y aplicar límites para no cargar el catálogo completo ni todas las galerías/vídeos anticipadamente.

## Compatibilidad
Reorganización de presentación, sin cambiar el contenido guardado de páginas, borradores ni promociones. Los bloques laterales izquierdo y derecho existentes se presentan en el lateral único en el orden publicado; el editor y su vista previa deben mostrar esa ubicación real. Adaptar los cuatro diseños existentes, incluido Lista, sin romper la vista inicial pública ni los estilos por tienda. Logo y marca del distribuidor se conservan; no se incorpora el pie corporativo de Urban Soft al portal.
La elegibilidad sigue siendo por tienda activa, producto activo, foto pública y precios positivos. Se conservan carrito, múltiplos de display, importes, stock informativo, galería, analítica, accesos, remitentes y separación por distribuidora. No implica envíos, cambios de DNS, campañas, precios ni históricos.

## Validación y entrega
Probar navegación estable sin repetidos/saltos, filtros dependientes, búsqueda y URLs antiguas, carga parcial y error; productos retirados desaparecen al dejar de ser elegibles. Verificar PC1440/1280, tableta768 y celular390/320, temas, cuatro diseños, nombres largos, cantidades de display y teclado/sinJS. Editor/publicación/galería deben coincidir con la página real. Documentación, manual principal y cambios de versión actualizados; revisión final, ZIP para cPanel y commit GitHub. La versión y las bases se fijarán tras verificar el estado publicado. Sin enviar campañas.
