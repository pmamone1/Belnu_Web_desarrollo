# MiDistri-Pedidos v60 · Comprobantes de MiDistri

## Guía de uso

### Consultar el movimiento
En Mis remitos, elegí el tipo de comprobante y el rango de fechas. En Mi estado de cuenta, abrí Comprobantes junto al movimiento. Los PDF están disponibles para ver, imprimir o descargar.

### Ver ventas y lotes
Si la venta todavía está pendiente de traslado, la copia de consulta indica ese estado. En un lote de devolución, el documento indica el lote y lista únicamente las salidas y los totales que corresponden al vendedor.

### Consultar cambios y pagos
Los ajustes, ampliaciones, precios, pagos y devoluciones registradas tienen su propia constancia. Cuando falta evidencia para un documento verificado, el movimiento lo indica.

## Detalle técnico

Base MiDistri-Pedidos v59. Requiere Urban Soft v693 y MiDistri v60 para consultar todos los tipos. Usar la actualización de MiDistri primero para que pueda interpretar los tipos ampliados de la API.

El original congelado conserva su ruta y su contenido. Las nuevas copias de consulta se construyen de sólo lectura desde las liquidaciones y los registros del vendedor. Se comprueba el alcance de vendedor y distribuidora en lista, resumen y PDF. Los pagos muestran fecha, medio e importe registrado. Las notas y los archivos de pago adjuntos quedan sujetos a la operación interna de Urban Soft. Los ajustes de precio se autorizan a partir de la existencia con impacto para el vendedor.

Sin migraciones ni envíos. Los instaladores respaldan los archivos y admiten --restore con el respaldo correspondiente. Verificar los casos de una venta cerrada por trasladar, un lote con más de un vendedor y el acceso directo al PDF de otro kiosco.
