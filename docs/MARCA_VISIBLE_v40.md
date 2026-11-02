# MiDistri-Pedidos v40 - Marca visible

## Guía de uso

### Acceso
Usá el Email asociado a tu vendedor o a tu cuenta de la distribuidora. No necesitás registrarte ni crear contraseña. Se conservan el código, los perfiles autorizados, el acceso recordado y los pedidos existentes.

### Administración
Las pantallas muestran MiDistri y la distribuidora. Para reiniciar un acceso vencido, usá el botón que vuelve a la administración de la distribuidora. El destino real y los controles de origen y permisos se conservan. El responsable sigue administrando precios, productos, fotos y permisos en su sistema de gestión.

### Catálogo y operaciones
La gestión, editor, promociones, materiales, campañas, estadísticas y pedidos usan términos de distribuidora. El botón de abastecimiento descarga el mismo Excel con nombre MiDistri_abastecimiento.xlsx. Preparación, remitos y Email mantienen las funciones y restricciones existentes. El nombre y logo propios de la tienda siguen vigentes.

## Detalle técnico

Cambio de presentación sobre MiDistri39 (824f5da3b7f8fdb11a9b567e5ffa0c21f031ffe9). Se retiraron menciones estáticas de Urban Soft y Urban Point de todas las plantillas activas del portal, y de mensajes propios que pueden llegar al usuario. ApiError adapta exclusivamente ocho mensajes heredados conocidos por coincidencia exacta; conserva estado HTTP, origen y contenido de mensajes desconocidos. Al presentar errores persistidos de sincronización/pedido usa el mismo mapa sin modificar su almacenamiento. No reescribe productos, nombres de tiendas, documentos históricos ni payloads del servicio. Las marcas que un operador haya cargado como contenido propio conservan su texto.

URBAN_API_BASE, URBAN_API_TOKEN, contratos DTO, rutas, destinos HTTPS, cabeceras de sesión y autorización se conservan. No se editan datos, modelos, migraciones, precios, snapshots, remitos históricos ni acceso por distribuidora. No se transforma el contenido del Excel ni del PDF remoto. Referencias de integración en documentación técnica e historial del manual se conservan por trazabilidad; esta guía prevalece para los textos visibles actuales.

## Compatibilidad, instalación y recuperación

Paquete incremental sobre código revisado v39; requiere la migración portal0014 ya aplicada. No ejecuta migraciones nuevas, campañas ni envíos. El instalador heredado comprueba huellas, entorno, esquema y plan vacío antes de reemplazar; una personalización no revisada detiene sin copiar. El archivo ajeno templates/accounts/forgotPassword.html se conserva y queda excluido.

Se crea respaldo automático privado de archivos reemplazados. Restaurar con el instalador v40 y ese respaldo sólo revierte código, con sus controles de integridad; conserva el esquema0014 y los datos. No restaurar bases ni modificar históricos por este cambio. Respaldo SQL sujeto al intervalo acordado (30 instalaciones confirmadas o 15 días); este paquete no acredita otra instalación ni solicita un respaldo completo por sí mismo.

## Validación y estado

Ver VERIFICACION_v40.md. Publicación, copia a Downloads y aceptación/instalación productiva se registran por separado. Esta guía no acredita producción ni activación de cron. Sin SMTP real ni campañas durante QA.

La limpieza incluye referencias abreviadas estáticas a Urban en avisos de guardado/publicación pendiente y ayuda de comandos; sin modificar datos propios ni destinos reales.
