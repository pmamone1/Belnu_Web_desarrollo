# MiDistri-Pedidos v33 · Editor y pedidos

## Guía de uso

1. Para administrar, entrar en Urban Soft → MiDistri → Configurar MiDistri. El vendedor deja de ver Acceso Distribuidor en el encabezado público; los permisos de administración se conservan.
2. En el editor, seleccionar una promoción y pulsar Eliminar bloque. Deshacer y Rehacer permiten recuperarla. Catálogo y contacto están protegidos. El cambio queda en borrador hasta revisar y publicar.
3. En Diseño y mensajes, cada mensaje tiene tamaño, fuente, color de letra y fondo propios. Restablecer estilo recupera la apariencia heredada sin borrar el texto. Los estilos de encabezado y botón Catálogo están también en esa sección; sus textos se editan en Encabezado y logo. El resultado se ve en la previa AJAX.
4. Si una foto/producto fue retirado, el aviso indica bloque y diapositiva; tocar el aviso selecciona ese bloque. Se puede corregir el borrador sin perder otros cambios. Reemplazar/quitar la diapositiva, ocultar o eliminar el bloque antes de publicar. Las fuentes retiradas nunca se rehabilitan por esta actualización.
5. Mis pedidos muestra número, fecha, importe solicitado/vigente y estado. Ver detalle abre la fila en la misma pantalla; muestra SKU y unidades solicitadas, aceptadas/completadas y sin completar. Pendiente significa no confirmado; cero significa cantidad confirmada en cero. El remito sigue disponible en pedidos emitidos.
6. En celular los campos se distribuyen verticalmente para no cortar los importes ni los botones. Sin JavaScript los detalles siguen visibles. Cuando no se pueden actualizar estados se avisa que se muestra la última información guardada.
7. Las sugerencias semanales conservan su programación y estado; instalar estos paquetes no habilita ni envía campañas. La previa requiere siete días completos de medición por distribuidora. No hay reconstrucción de visitas previas al inicio.

## Detalle técnico

Estilos opcionales en datos.estilos_mensajes: mapa cerrado de claves a tamano14..56 entero, fuente de lista permitida y colores hex #RRGGBB. Sin CSS/HTML arbitrario. Los textos conservan autoescape. La clave se conserva sólo si existe para mantener la normalización/huella de páginas antiguas. Sin migraciones ni reescrituras de VersionPagina o EdicionPagina.
Guardar/render de borrador valida estructura, enlaces y estilos con fuentes=False; revisar/publicar mantiene validación estricta local/remota y control de revisión/firma. Advertencias locales incluyen id de bloque y diapositiva; edición y recursos permanecen limitados a la tienda autorizada. Material propio retirado sigue sujeto al control remoto existente.
La tabla usa sólo PedidoLocal del vendedor/distribuidora actual y snapshots validados por pedido_valido. No consulta precios actuales ni emite cambios de pedido. Anulación y revisión mantienen sus estados; no se afirma entrega sin estado emitido. Hasta100 pedidos como antes, sin solicitudes extra por expansión. El detalle completo conserva refresco remoto y aviso de copia desactualizada.

## Compatibilidad y reversión

Bases: Urban624 y MiDistri32. Urban625 no cambia el contrato remoto (hash opaco y fuentes autorizadas); el portal33 es compatible con Urban624. Se entregan ambos paquetes para documentación coordinada. Nuevas versiones preparadas, instalación productiva pendiente.
Rollback: usar el respaldo de archivos generado por el instalador de ESTA versión. No hay migraciones nuevas. Coordinar que no haya publicación de página pendiente; no restaurar datos/snapshots ni eliminar las claves JSON de estilos. Antes de retroceder el portal, exportar el borrador JSON y coordinar que nadie edite ni publique con32: ese código descarta los estilos al guardar. Las versiones publicadas previas se conservan; recuperar código33 no recupera estilos que hayan sido eliminados por una edición con32. Para recuperarlos usar el JSON exportado mediante una revisión técnica autorizada, sin reescribir históricos. Los documentos y pedidos históricos no se modifican.
No solicitar respaldo completo adicional por este paquete: conservar la política30 instalaciones confirmadas/15 días. El instalador respalda sólo archivos reemplazados; no inferir instalaciones de marcadores o commits.

## Comando vigente del preparador semanal

Conservar la misma tarea cada15 minutos, sin duplicarla. Debe entrar en la carpeta del proyecto; no usar --skip-checks. Esta actualización no edita el cron.

```bash
/bin/sh -c 'umask 077; cd /home/mcollini/belnuweb && /home/mcollini/virtualenv/belnuweb/3.7/bin/python manage.py midistri_incentivos_preparar >> /home/mcollini/midistri_incentivos_preparar.log 2>&1'
```

## Revisión final

Pedidos históricos emitidos sin desglose muestran No informado y remito disponible, nunca preparación pendiente. Tabla compatible con los cuatro temas. Catálogo y contacto existentes están protegidos también en servidor; páginas antiguas sin contacto no reciben bloques inventados. Campo legado de acceso administrativo oculto también en el editor clásico, conservado sólo para compatibilidad del formulario.
