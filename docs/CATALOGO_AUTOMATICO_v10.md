# MiDistri v10 - Catálogo coordinado con Urban Soft

## Guía de uso

El catálogo se actualiza mediante un cron cada cinco minutos. Las altas se preparan en Urban Soft v588; MiDistri utiliza su sincronizador existente para copiar productos, fotos públicas, categorías, precio vendedor y PVP.
Se incluyen las distribuidoras expresamente habilitadas en MiDistri, también las que se autoricen después. Los productos ocultados o excluidos conservan esa decisión.
La regla general se configura en Urban con proveedor revisado y exclusiones. Las cuatro Esferas 328, 329, 330 y 331 permanecen excluidas.
Dar de baja un producto en Urban lo retira del catálogo; los pedidos anteriores conservan sus datos y precios. El pedido nuevo se calcula al precio vendedor.
Tocá la foto para ampliarla. Con un solo recurso no aparecen flechas; con varias fotos o videos publicados sí hay navegación. Los enlaces de YouTube/Vimeo abren el sitio de origen.
Una subida de video privada no se publica automáticamente: sigue requiriendo revisión y confirmación. Alma Chocolate141 tiene publicadas las dos fotos y el enlace de video para20/65, confirmado por el usuario y lectura del portal el23/10/2026.
Si hay un error, el portal conserva la última copia válida. Revisá su fecha de última sincronización y el registro del cron. No se envía ninguna campaña durante esta actualización.

## Instalación y operación técnica

Paquete exclusivo belnuweb, Python3.7. Acumulativo sobre archivos exactos v8/v9; sin migraciones nuevas, nuevas dependencias ni cambios en conexiones/SMTP. Conserva la galería v9.
La API snapshot y midistri_sincronizar no cambian: se prueba su contrato de actualización y preservación de pedidos. El coordinador se instala exclusivamente en Urban.
Configurar una única tarea en cPanel con el comando documentado en Urban v588. Reemplazar un cron de sincronización simple si ya existía; no duplicarlo.
Si las altas se bloquean, el coordinador igualmente intenta copiar publicaciones actuales, incluyendo bajas y cambios de precios. Si falla la copia, se conserva la última copia válida y se reintenta en el siguiente ciclo.
Para detener automatización de altas, deshabilitar la regla/cron en Urban. La restauración de este paquete sólo devuelve archivos de MiDistri verificados por hash, no datos.
No utilizar producción como prueba. Validación local: altas repetidas y distribuidora futura, actualización de nombre/fotos/categoría/precios, bajas conservando pedidos y rechazo íntegro de snapshot inválido. Ver VALIDACION_v10.md.
