# Disponibilidad de proveedor · MiDistri-Pedidos v43

## Guía de uso

### Consultar el catálogo
La ficha separa «Disponible en proveedor» de «Disponible en depósito». Cuando existe una consulta al proveedor, se muestra su fecha y hora. La distribuidora confirma la disponibilidad al recibir el pedido.

### Revisar el carrito
Cuando el proveedor está sin disponibilidad, se pueden pedir las unidades informadas por el depósito. Si se agotan, el artículo sigue en el catálogo con la compra deshabilitada. Si la disponibilidad cambia con el carrito abierto, quitá el artículo o bajá la cantidad antes de volver a enviar.

### Ver fotos y reseña
Abrí la galería del producto para ver las fotos públicas y la reseña que haya cargado la distribuidora. Las imágenes incorporadas al catálogo se sirven desde Urban Soft.

### Actualizar
Primero se instala Urban Soft v1.18.660 y luego MiDistri-Pedidos v43. Después se sincroniza el catálogo. Esta guía describe la nueva versión. La instalación productiva se confirma por separado.

## Detalle técnico

El snapshot completo de Urban acepta en cada publicación una extensión opcional con las únicas claves siguientes.

| Clave | Valor |
| --- | --- |
| origen | Texto fijo proveedor |
| disponible | Booleano calculado por Urban según el estado y vigencia de la fuente |
| actualizado | Fecha y hora ISO 8601 con zona, o null |
| stock_local_disponible | Entero de 0 a 1.000.000.000 |

El portal guarda la extensión como JSON en Publicacion.abastecimiento. Si el campo falta o vale {}, la publicación usa los indicadores previos. La siguiente copia completa limpia los datos de proveedor si desaparece la extensión. Cualquier campo, tipo o fecha inválidos rechazan el snapshot completo antes de modificar la copia. Urban es la fuente de las fotos públicas y sanea el material importado. MiDistri recibe sólo las URLs ya admitidas del catálogo. El contrato público excluye costos, impuestos, credenciales y nombres internos de proveedor.

El relevamiento informado para el PDF v2 encontró fotos en 855 de 1.054 productos y en 220 de los 271 disponibles. Son conteos del material de origen. La publicación depende de las selecciones de Urban, su distribuidora y los filtros habituales de precio y foto. El portal no procesa el PDF.

Las fichas, destacados y productos promocionados muestran el estado del proveedor. Si la extensión está presente, se muestran estados separados y se omite la estimación de entrega anterior. El portal valida un pedido nuevo al agregar cantidades y al enviar. Si el proveedor está sin disponibilidad, comprueba que la cantidad no supere el stock local de la última copia. Urban vuelve a validar disponibilidad con sus datos vigentes. Los intentos de envío existentes conservan su referencia y su tratamiento de reintentos. Este circuito no genera pedidos automáticos al proveedor.

## Compatibilidad, migración y restauración

El paquete contiene la entrega acumulada de las bases revisadas 39, 40, 41 y 42. La migración base requerida es 0014_dispositivo_recordado. El único destino del comando de migración es 0016_publicacion_abastecimiento. Si falta 0015_publicacion_descripcion, Django la aplica antes como dependencia. Ambas son aditivas. Se conservan la copia anterior de pedidos, la autorización por distribuidora y los importes y documentos históricos. Se utiliza el entorno Python 3.7 existente de MiDistri.

La comprobación previa verifica hashes, archivo y registro de migración, y la coherencia de las columnas descripcion y abastecimiento. El instalador permite en el plan únicamente 0015 y 0016. Respalda los archivos reemplazados y registra el estado de migraciones previo. Si 0015 ya constaba en la base antes de instalar v43, se conserva su archivo y se puede restaurar el código respaldado mientras 0016 siga pendiente. Si la actualización aplicó 0015 o 0016, la restauración automática queda bloqueada y corresponde una corrección hacia adelante. No se revierten migraciones ni datos históricos.

## Instalación en cPanel

Aplicar primero el paquete Urban Soft v1.18.660. Subir el ZIP del portal a /home/mcollini y hacer la comprobación inicial.

```bash
cd /home/mcollini &&
MIDISTRI43_DIR="$(mktemp -d /home/mcollini/midistri43.XXXXXX)" &&
unzip -q /home/mcollini/midistri_pedidos_v43_abastecimiento_proveedor.zip -d "$MIDISTRI43_DIR" &&
/home/mcollini/virtualenv/belnuweb/3.7/bin/python "$MIDISTRI43_DIR/instalar.py" --root /home/mcollini/belnuweb
```

Si informa «DESTINO VERIFICADO» y «Solo comprobación», ejecutar en la misma terminal.

```bash
/home/mcollini/virtualenv/belnuweb/3.7/bin/python "$MIDISTRI43_DIR/instalar.py" --root /home/mcollini/belnuweb --apply &&
cd /home/mcollini/belnuweb &&
/home/mcollini/virtualenv/belnuweb/3.7/bin/python manage.py midistri_sincronizar
```

Confirmar que se mostró «CÓDIGO INSTALADO» antes de sincronizar. Guardar la salida y la ruta de respaldo de código. Verificar la tienda habilitada siguiendo las pruebas de lectura del [checklist manual](19_PRUEBAS_MANUALES_CRITICAS.md). La evidencia automatizada y los pendientes figuran en [VERIFICACION_v43.md](VERIFICACION_v43.md).
