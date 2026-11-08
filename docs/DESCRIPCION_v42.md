# Reseña del producto en la galería · MiDistri42

## Guía de uso
### Cargar y actualizar
La descripción se escribe en la ficha del producto de la administración distribuidora y llega al portal con la sincronización habitual. Es opcional, texto plano de hasta2.000caracteres. No se genera una reseña automáticamente.
### Ampliar una foto
Abrir la foto del catálogo muestra la reseña bajo el material ampliado. Sigue visible al pasar entre fotos del mismo producto. Al abrir otro producto muestra su propio texto; si no tiene descripción no aparece un espacio vacío. Conserva controles de foto/video y analítica. La alternativa sin JavaScript muestra texto escapado.
### Instalar la pareja
Primero Urban659 y después MiDistri42. Sólo portal0015 agrega la copia de descripción. Las versiones39/40/41 con0014 se admiten mediante paquete acumulativo de41 más esta mejora. No se modifican pedidos ni remitos, importes, remitentes o cron. No se envían campañas al instalar.

## Detalle técnico
Publicacion.descripcion TextField blank/default vacío/max_length2000. validar_snapshot admite descripcion ausente como vacío y rechaza tipos no string, más de2000oNUL antes de aplicar, dentro de atomic, preservando la copia anterior. Contextos de catálogo y vista previa incluyen descripcion en json_script. El visor usa textContent y oculta el bloque vacío. CSS respeta saltos de línea, palabras largas y desplazamiento del diálogo. Versionado de estáticos42 para refrescar el navegador.

El snapshot completo GET JSON tiene límite128MiB (antes16), validado por lectura acotada; el resto de solicitudes/media conserva16MiB. Urban659 emite este snapshot en UTF8 sin expandir cada carácter a escape ASCII. El contrato sigue hasta10.000publicaciones y2.000caracteres por descripción. Catálogos cercanos al máximo necesitan memoria/tiempo suficiente y futura paginación si se exceden; no se quita el control de tamaño. Instalar la pareja en orden y sin demorar si el catálogo es grande.

## Compatibilidad, migración y rollback
Portal0015_publicacion_descripcion es aditiva sin relleno de negocio; conserva datos previos y no afecta analítica/intervalos. Requiere0014yUrban659para recibir la reseña. Snapshots anteriores siguen aceptados con texto vacío. Las nuevas descripciones públicas no habilitan contactos de vendedores ni cambian acceso por tienda.

Una vez aplicada0015, el instalador bloquea rollback: corregir hacia adelante para preservar texto y copia. Se respalda código. No se tocan claves, cron, venv, remitentes ni WhatsApp. El archivo local templates/accounts/forgotPassword.html estaba modificado antes y queda excluido del inventario y del commit. Los textos de marca y funciones41 se conservan con el paquete acumulativo.

## Validación
RED inicial de contrato de descripción; pruebas de recepción y borrado, viejo snapshot, rechazo atómico, escape JSON/HTML, capturas del visor y transporte grande. Sin pruebas productivas ni mensajes reales. Ver checklist con resultados ejecutados.
