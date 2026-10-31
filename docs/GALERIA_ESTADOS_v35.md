# MiDistri-Pedidos v35 · Fotos ampliadas y estados de pedidos

## Guía de uso

1. Al tocar una foto del catálogo, el visor utiliza el espacio disponible también cuando el archivo original es pequeño. Se mantiene la imagen completa y proporcionada, sin recorte ni deformación. En celular se ajusta a la pantalla.
2. Una foto original de baja resolución puede verse menos nítida al ampliarla. Para mejorar su detalle hay que cargar una foto original de mayor resolución en Urban Soft; esta actualización no inventa detalles ni modifica los archivos.
3. En Mis pedidos, los pendientes de envío y recibidos se identifican con ámbar; OK para preparar con azul; entregados con verde; cancelados con rojo. Los casos que necesitan revisión usan violeta. El texto siempre permanece visible.
4. Entregado parcialmente conserva esa aclaración. Los colores no cambian el estado real del pedido, sus cantidades ni su remito. Se puede desplegar cada fila para consultar el detalle como antes.

## Detalle técnico

Causa reproducida: el recurso público indicado para el SKU57401 mide218x141 píxeles. La tarjeta estiraba la foto a274px mientras el visor usaba width/height auto con sólo máximos, por lo que conservaba218x141. galeria.css asigna a la imagen width100% y alto60vh (48vh en celular), manteniendo object-fit:contain y sus límites. No se cambian videos, URLs, medición de eventos o archivos originales. Se actualiza la referencia de caché de esta hoja en base.html.
pedidos.html añade clases de estado a la etiqueta existente y pedidos_tabla.css define colores y contraste independientes del tema. Estados nuevos/desconocidos conservan Necesita revisión, en violeta. No se interpreta el color como una transición de negocio.

## Compatibilidad, validación y rollback

Exclusiva del portal, sobre MiDistri34 confirmado instalado el31/10/2026. Urban626 se conserva sin actualización. Sin cambios de modelos, rutas, permisos, migraciones, importes, snapshots, históricos o credenciales. Sin campañas, SMTP ni cambios de cron. Los ocho documentos obligatorios y el manual PDF principal incluyen esta guía vigente.
Prueba de navegador reproducida antes de corregir: foto218x141 menor que la tarjeta. Después: ampliación y foto completa, recursos grandes y verticales,1440/390/320, cierre con teclado y ausencia de errores JavaScript. Estados con texto y contraste mínimo4.5:1 en claro, nocturno, azul y verde. El instalador verifica base por huellas, respalda archivos y permite restaurar su respaldo de código; no revierte datos ni se deben tocar migraciones.
Instalación productiva de v35 pendiente. Pruebas locales sintéticas; no se usa producción para probar. Reutilizar respaldo de base según política vigente30 instalaciones confirmadas/15 días, sin inferir conteos a partir de versiones publicadas. Esta actualización no genera un respaldo nuevo de la base.
