# MiDistri-Pedidos v9 - Galería sin navegación innecesaria

Corrección visual sobre v8. Instalación v9 productiva pendiente.

## Guía de uso
1. Tocá la foto del producto para ampliarla. Si tiene un solo recurso, la ventana muestra la foto y Cerrar, sin flechas ni miniaturas para repetir la misma imagen.
2. Si hay varias fotos o videos publicados, aparecen Anterior, Siguiente y las miniaturas para elegir. Las fotos se mantienen con la principal primero.
3. Los videos MP4 publicados tienen controles de reproducción. Los enlaces de YouTube y Vimeo muestran un botón para abrir el video en su sitio de origen.
4. Que un video figure en Productos de Urban Soft no significa que ya esté publicado en MiDistri. En Administrar MiDistri-Pedidos > Productos > Fotos y videos, elegir el video, revisar y confirmar su publicación para la distribuidora correspondiente.
5. Después de publicar, sincronizar el catálogo de MiDistri para recibir el material. Si todavía no aparece, revisar publicación y última sincronización antes de volver a subirlo.

## Diagnóstico del caso informado
Consulta pública del 23/10/2026: Alma de Campeon (Chocolate), producto Urban141, muestra dos fotos y ningún video recibido en el portal20. El catálogo indica sincronización 23/10/2026 02:11. No se determinó todavía si falta publicar el enlace YouTube XLi-hLJLm0A o volver a sincronizar; se solicitó diagnóstico de sólo lectura de ProductoVideo y MaterialPublicable.
No se cambió la reproducción ni se asegura que el video haya quedado publicado en producción. No se publican automáticamente originales privados al instalar. El cambio v9 elimina únicamente controles redundantes de la galería.

## Implementación y validación
galeria.js crea controles y miniaturas sólo para más de un recurso. Las flechas de teclado no recargan un recurso único. Cerrar/Escape/foco, controles MP4 y enlaces YouTube/Vimeo se conservan.
QA en navegador con datos sintéticos: una foto sin controles; tres recursos (dos fotos y YouTube) conservan Anterior/Siguiente/miniaturas y el enlace exacto en el tercero. No se descargó ni modificó el video de YouTube. Revisión independiente puntual sin hallazgos.
Ver VALIDACION_v9.md para pruebas y límites.

## Compatibilidad y rollback
Requiere MiDistri v8, base951bd038f818400d88aabb5b6924400809801c80. Sólo /home/mcollini/belnuweb, Python3.7. Sin modelos ni migraciones nuevas, nuevas variables, contratos, permisos, precios, pedidos o movimientos.
El instalador valida hashes, genera respaldo privado del código reemplazado, comprueba Django y ausencia de migraciones nuevas, ejecuta collectstatic y reinicia belnuweb. No requiere actualización de Urban Soft.
Rollback sólo código con instalar.py --root /home/mcollini/belnuweb --restore RUTA_RESPALDO; valida originales antes de detener. No revertir base ni migraciones. No se solicita otro respaldo completo dentro del intervalo vigente.
Sin envío de campañas. El diagnóstico del remitente confirmó cuentas Belnu2/3; Gmail no está configurado. Su alta y selección siguen pendientes, sin cambiar las cuentas actuales ni las colas.
