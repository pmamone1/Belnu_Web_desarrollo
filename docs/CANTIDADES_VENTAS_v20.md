# MiDistri-Pedidos v20 — Cantidades y orden por ventas

## Guía de uso

1. En el catálogo, el nombre y los precios tienen una letra más pequeña. En celular la foto ocupa 150px y la tarjeta crece para contener toda la información. Los botones − y +, la cantidad y Agregar / actualizar quedan completos, sin recortes ni desbordes. Los botones conservan un área de 44px y el campo numérico una letra de 16px.
2. El selector conserva los múltiplos del display y los límites que valida Urban Soft. Este ajuste visual no modifica precios, cantidades ni pedidos existentes.
3. En «Ordenar» elegí «Más vendidos» para ver primero los productos con más unidades confirmadas y debitadas en todo Urban Soft de tu distribuidora. No se limita a los pedidos hechos desde MiDistri ni a los diez productos destacados.
4. Se conservan la búsqueda, categoría y paginación. Los productos sin ventas documentadas quedan después de los que tienen posición; el desempate es por nombre. Si Urban Soft informa que falta evidencia para un ranking completo, no se muestran posiciones inventadas y el catálogo avisa que se ordena por nombre.
5. Urban603 corrige la omisión de ventas históricas con líneas vacías en liquidaciones cuando sus remitos guardados permiten conciliar el detalle. No cambia saldos ni documentos antiguos. Instalar ambos paquetes y esperar el cron habitual de cinco minutos.

## Detalle técnico

CSS limitado a producto-info y producto-compra: título18px, precio20px, cantidad16px, botones44px y grid sin salto de línea. El carrito y las demás pantallas conservan sus reglas; cantidades.js, display y validación de servidor no cambian. Cache de pagina.css pasa a v20.

Nueva opción GET orden=ventas en allowlist. Se filtra por tienda, elegibilidad, categoría y búsqueda antes de ordenar. La posición de cada producto llega como orden_ventas opcional al nivel de publicación, compatible con portal19 que la ignora. Se valida entero positivo hasta1000000, rechazando bool, y se conserva en Publicacion.indicadores existente. La ordenación Python evita diferencias JSON entre MariaDB y SQLite, con desempate estable y paginación sobre el resultado completo. No se publican cantidades vendidas ni stock exacto.

Sin nuevas migraciones, variables ni cambios de remitentes, WhatsApp, sesión o permisos. Base exacta19. Requiere Urban603 para el orden completo y la corrección histórica; con snapshot anterior conserva los diez puestos conocidos. Instalación productiva pendiente. Rollback: restaurar código desde respaldo del instalador; no se modifica esquema ni se revierte base. Campaña sin enviar y MiDistri-Puntos sigue sólo en análisis.
