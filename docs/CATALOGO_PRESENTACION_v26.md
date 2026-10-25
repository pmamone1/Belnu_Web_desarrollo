# MiDistri-Pedidos v26 — Presentación del catálogo

## Guía de uso
1. En Ordenar se muestra sólo Más vendidos. El cálculo sigue siendo por importe de venta neta consignada cerrada/debitada; no se cambia el ranking ni su alcance.
2. Los botones de banners/promociones en los márgenes izquierdo y derecho muestran Ver, conservando su destino. Las promociones centrales mantienen su texto habitual/configurado.
3. Cantidad y Agregar / actualizar quedan juntos al pie de la tarjeta y alineados por fila, aunque el título, el display o las etiquetas ocupen más líneas. No se recortan los contenidos ni se fija una altura que oculte información.
4. Los diseños compacto, fotos, promociones y lista conservan su distribución; en móvil los controles permanecen dentro de la tarjeta. Las unidades, múltiplos de display, cantidades y carrito no cambian.
5. Se conserva el saludo sólo con nombre. Esta actualización acumulativa se instala sobre MiDistri23,24o25, sin tocar Urban606 ni enviar campañas. Después, recargar navegador; no recalcular indicadores ni sincronizar.

## Detalle técnico
catalogo_productos.html cambia sólo la etiqueta visible de orden=ventas. pagina_bloque.html usa promo_etiqueta_boton.html para abreviar los CTA de zona izquierda/derecha, incluidos enlaces propios, sin alterar href ni copiar cambios al contenido guardado. pagina.css usa margen automático del bloque producto-compra en tarjetas flex y alineación final en lista; formularios sin margen inferior adicional. El base.html cambia la versión del CSS a26 para renovar la carga en el navegador.

## Compatibilidad y rollback
Bases revisadas MiDistri23/24/25, misma migración0011 y sin nuevas migraciones, rutas, variables o dependencias. Inventario acumulativo incluye correcciones del saludo y documentación previa; no incluye el cambio ajeno de recuperación de contraseña. No modifica precios, ranking, pedidos, saldos, documentos, perfil, permisos, remitentes, WhatsApp o cron. Preflight de sólo lectura compara hashes de cada base y plan vacío antes de copiar; respaldo automático de los archivos reemplazados. Rollback con respaldo propio del instalador: restaura archivos y presentación anterior de la base instalada, sin revertir esquema o datos. Producción pendiente.
