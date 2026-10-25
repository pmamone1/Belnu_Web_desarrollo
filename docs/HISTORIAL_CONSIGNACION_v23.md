# MiDistri-Pedidos v23

## Guía de uso
1. Más vendidos se calcula por importe histórico de venta neta de consignaciones cerradas y debitadas de la distribuidora. No incluye pedidos firmes, incluidos los del portal.
2. Se conservan las ampliaciones consignadas, devoluciones y ajustes, así como precios y evidencia congelada. No se alteran saldos, históricos, clasificación, stock o documentos.
3. La pantalla Analítica general conserva todas sus fuentes y filtros. El ranking del portal usa sólo su componente consignado y todo el período histórico.
4. El cache anterior incluía pedidos: se descarta para ranking hasta renovar indicadores. Stock y plazos se conservan. Recalcular y sincronizar tras ambas instalaciones; el cron existente no cambia.
5. Un producto sin venta consignada positiva no aparece al ordenar por Más vendidos. Sigue disponible por Nombre o Precio. El precio de venta actual del catálogo no se usa para revalorizar el ranking.
6. En Mis pedidos y detalle se muestra Entregado cuando Urban Soft informa remito emitido. Es la convención operativa pedida; no registra una nueva recepción física ni un cargo.
7. Una emisión parcial se muestra Entregado parcialmente y conserva las cantidades retiradas. Una cancelación posterior se sigue mostrando cancelada. Los estados Recibido y OK no pasan a Entregado antes de la emisión.
8. LIN y la descripción de línea no se muestran en historial/detalle del vendedor. Nombre, número VV, referencia, importes, fotos y acceso al remito se conservan; el catálogo mantiene su identidad habitual.
9. El estado se consulta al abrir o actualizar historial/detalle. Si falla la red se indica que es la última información guardada; no se presenta una actualización inexistente.

## Detalle técnico
Compatibilidad: Urban606 sobre605 y portal23 sobre22. Sin nuevo modelo, campo, permiso, ruta, variable, dependencia o migración. La API conserva emitido/recibido/ok/cancelado; no se cambia el contrato ni la identidad. El parámetro incluir_pedidos=False del servicio compartido sólo se usa para ranking del portal. Cache privado criterio_ventas=importe_consignacion; API pública sigue exponiendo posiciones, sin costos ni importes históricos.

## Compatibilidad y rollback
El instalador verifica base y plan antes de copiar, respalda archivos y rechaza pendientes ajenas. Rollback de archivos mediante respaldo propio; recalcular indicadores y sincronizar con el productor restaurado. No revertir saldos, esquema ni históricos. Conservar respaldo de base vigente según política30 instalaciones/15días; el ZIP o un reintento no cuentan como instalación. Sin campaña ni prueba en producción.
