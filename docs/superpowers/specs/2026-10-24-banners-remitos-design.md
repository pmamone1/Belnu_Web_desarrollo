# Banners panorámicos y remitos identificados
Fecha: 24/10/2026. Estado: diseño aprobado e implementado localmente; instalación productiva pendiente.

## MiDistri
- Los bloques de promoción tipo banner ocupan el ancho de la ventana, sin provocar desplazamiento horizontal. Carruseles y vídeos de otros bloques conservan su función.
- Altura de imagen de referencia: 480–600 px en escritorio; 300–420 px en móvil, ajustada a la ventana. Conservar la opción mostrar foto completa o recortar; no recortar forzosamente fotos de productos.
- Texto, precio vendedor, PVP y botón sobre una composición legible con contraste y espacio propio; no tapar el producto con texto.
- Fundido cruzado de aproximadamente 600 ms entre fotos. Mantener intervalo configurado, controles manuales, pausa, navegación por teclado, pausa por foco/ratón y vídeos sin reproducción automática.
- Con movimiento reducido: cambio inmediato y rotación inicialmente detenida. Una sola foto: sin flechas, contador ni temporizador.
- Funciona en las cuatro plantillas, los cuatro temas, vista previa de teléfono y sesión del vendedor que sustituye el contenido sin recargar todos los scripts.
- También cubrir promociones de la página anterior que se conserva hasta publicar la nueva tienda. No publicar borradores automáticamente.

## Urban Soft: remitos
Alcance: carga individual y por lote; preparación de devolución individual y consolidada; venta individual, de liquidación y consolidada; pedidos normales y MiDistri; remito de pedido incluido en liquidación; preparación web declarada por vendedor.
- Cada página identifica tipo de documento, número y nombre de salida/pedido/lote, fecha documental disponible y vendedor con LIN y VV antes de su nombre.
- Ejemplo: “Remito de devolución · Lote #5” / “Incluye: #18 Electro Viral; #19 Juguetes” / “LIN 7004 · VV 5 · BRANDSEN” / “Pág. 1/2”.
- Numeración por remito de cada vendedor; comienza nuevamente en 1 para el siguiente. No confundir número de página del paquete descargado con páginas de un remito.
- Mantener el orden de recorrido y contenido, precios, cantidades, totales, fotos y notas. Repetir cabecera de columnas cuando una tabla continúa. Nunca separar la foto de su fila.
- Conservar los formatos de papel admitidos y la posibilidad actual de colocar varios remitos cortos por hoja. Cuando un remito requiere varias hojas, reservar su continuidad sin mezclarla con el comienzo de otro vendedor.
- No forzar todos los remitos a una sola página mediante letra ilegible. Ajustar de forma moderada y continuar cuando sea necesario.
- Cubrir tanto impresión / guardar PDF desde pantalla como PDF nativo adjunto o descargado.
- Documentos históricos: no editar HTML congelado, PDFs originales, snapshots, hashes ni referencias de envíos realizados. Generar, cuando corresponda, una copia de presentación verificada con identificación y páginas. Si faltan datos históricos, indicar “no consta en el documento histórico”; nunca completarlos por intuición con datos maestros actuales. Las copias ya enviadas no se sustituyen en las casillas de los destinatarios.

## Referencias a lotes
- Junto a cada referencia visible de un lote de carga/devolución, mostrar en letra menor los números y nombres de sus salidas, incluyendo consultas, preparación, portal web del vendedor y documentos.
- Identificar por separado los lotes de Excel de créditos posteriores: tomar las salidas de sus créditos; no confundir su número con el de un lote de devolución.
- Conservar restricciones de alcance y privacidad. El portal de un vendedor sólo recibe referencias autorizadas para su propia devolución.
- En documentos congelados, prevalecen los nombres y referencias del snapshot. Si no constan, señalarlo. No alterar los conceptos económicos históricos.
- Evitar consultas repetidas por fila mediante precarga de relaciones o datos preparados por la vista.

## Verificación y entrega
Dos actualizaciones independientes de Urban Soft y MiDistri, con documentación, manuales PDF, ZIP verificado, comandos completos de cPanel y commits reales en sus respectivos GitHub.
Pruebas con datos sintéticos locales: remito corto, dos/tres páginas, varios vendedores, nombres largos, varias salidas por lote, pedido MiDistri y copias históricas; revisión visual de primeras/intermedias/últimas páginas.
Banners: escritorio/móvil, temas, una/múltiples fotos, vídeos, clics rápidos, movimiento reducido, sesión por pestaña y ausencia de desbordamiento.
No enviar campañas ni hacer pruebas en producción. Sin cambios económicos ni de permisos.
