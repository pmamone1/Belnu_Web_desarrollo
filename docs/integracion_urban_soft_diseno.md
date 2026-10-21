# Integración Urban Soft / MiDistri — diseño aprobado en conversación

Fecha: 21/10/2026. Autorización de ejecución: «realizarlo».

## Objetivo y límites
Dos proyectos, dos repositorios y dos instalaciones. Urban Soft es la fuente de productos activos, fotos, PVP, precio vendedor (único para todos), distribuidoras, líneas y vendedores. El portal se denomina «MiDistri - Pedidos Online - {distribuidora}». Catálogo antiguo retirado de publicación al habilitar la integración, sin borrar archivos ni históricos. Sin cobro online, stock, reservas ni promesas de entrega en esta versión.

## Contrato y seguridad
API privada v1 separada de la API pública de catálogo existente, reutilizando credenciales de aplicación de Urban Soft. Conexión habilitada explícitamente con distribuidoras permitidas; publicaciones producto/distribuidora/proveedor. Datos privados de vendedores nunca se incluyen en el catálogo público. Sesión de vendedor propia, revocable y validada en Urban Soft en cada operación; no crea usuarios administrativos. Invitación por email o enlace para WhatsApp, token aleatorio almacenado como hash, vence a las 48 horas, un uso mediante POST (GET no consume). Sesión 90 días, cierre explícito y revocación. Los transportes de email/WhatsApp no se ejecutan durante instalación/pruebas.

## Catálogo y pedidos
Copia local del catálogo sincronizada por comando programable y botón de gestión móvil; reemplazo atómico solo tras respuesta completa válida. Solo fotos del catálogo Urban Soft; no usar Producto/ProductoGallery antiguos. Ofertas por distribuidora explícitas; nunca compartir existencias ni inferir pertenencia por nombre. Un pedido tiene UUID del portal, vendedor y distribuidora inmutables, detalle/precios congelados. El servidor valida publicaciones activas, identidad, precios, cantidades y distribuidora, no confía en importes del navegador. Reintento con mismo UUID/contenido devuelve el pedido original, contenido distinto se rechaza.

Recibido -> OK -> Preparado/emitido; Recibido u OK -> Cancelado por falta de stock. Recepción y Excel no generan saldo. Confirmar preparado crea Pedido/PedidoProducto/PedidoAsignacion nativos y aplica el servicio económico existente bajo transacción, bloqueando vendedor y solicitud. Se divide por proveedor si hay productos de varios proveedores. RI congelado en cero: precio vendedor común aprobado, no introducir recargos diferentes. Conservar snapshot del documento, sin recalcular históricos con maestros. Solo remitentes autorizados por backend y distribuidora pueden aprobar, exportar, cancelar, emitir y comunicar.

## Comunicaciones y depósito
Email recibido y cancelado, email preparado con PDF de remito(s), cola persistente reintentable independiente del resultado comercial. Descargar Excel OK con hojas Detalle por pedido y Totales por producto, línea y vendedor sin matrícula; neutralizar fórmulas en texto de Excel. Repetir pedido revalida catálogo/precios y requiere confirmación.

## Publicación
Dos ramas/PR y paquetes distintos con manifiesto de destino; probar ambos con datos sintéticos. Instalar Urban primero y MiDistri después, integración desactivada hasta configurar conexión y validar catálogo. Respaldar código y bases antes de migraciones; rollback económico no revierte cargos por restaurar archivos. No instalar secretos, media, bases ni entornos. Producción se instala con comandos separados luego de revisión.
