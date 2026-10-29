# Instalación MiDistri-Pedidos v27

Paquete acumulativo para archivos exactos de las versiones 23,24,25 o26. Usar sólo en /home/mcollini/belnuweb con el entorno Python 3.7 existente. No instalar en Urban Soft. No requiere nuevas migraciones ni cambiar cron.

1. Subir midistri_pedidos_v27_catalogo_sku.zip a /home/mcollini.
2. Calcular SHA256 y compararlo con la huella real de la entrega antes de continuar:

```bash
cd /home/mcollini
sha256sum midistri_pedidos_v27_catalogo_sku.zip
```

3. Si la huella coincide, pegar el bloque completo. El chat de entrega incluye además la comprobación automática con la huella concreta.

```bash
(
set -e
umask 077
cd /home/mcollini
unzip -t midistri_pedidos_v27_catalogo_sku.zip
STAGING_M27=$(mktemp -d /home/mcollini/staging_m27_XXXXXX)
unzip -oq midistri_pedidos_v27_catalogo_sku.zip -d "$STAGING_M27"
/home/mcollini/virtualenv/belnuweb/3.7/bin/python "$STAGING_M27/instalar.py" --root /home/mcollini/belnuweb
/home/mcollini/virtualenv/belnuweb/3.7/bin/python "$STAGING_M27/instalar.py" --root /home/mcollini/belnuweb --apply
head -n 3 /home/mcollini/belnuweb/VERSION_DOCUMENTADA.txt
)
```

El primer paso es sólo comprobación: valida los archivos base, el paquete y el plan vacío de migraciones. Si se detiene, conservar el mensaje y no forzar la copia. Al aplicar se hace respaldo privado de los archivos reemplazados y se reinicia sólo MiDistri. No se envían campañas ni se cambian remitentes, WhatsApp, precios o pedidos.

Verificar después: SKU debajo del nombre y en destacados, códigos largos dentro de tarjeta, cantidades alineadas y carrito habitual. La consulta de ingreso existente requiere vendedor activo, Email asociado, tienda activa conectada y remitente propio disponible; esta instalación no activa otras tiendas.

Restauración segura de archivos con el respaldo anunciado por este instalador, sin borrar base ni históricos:

```bash
/home/mcollini/virtualenv/belnuweb/3.7/bin/python "$STAGING_M27/instalar.py" --root /home/mcollini/belnuweb --restore /home/mcollini/RUTA_DEL_RESPALDO_ANUNCIADO
```

Sustituir la ruta del respaldo por la que informó esta instalación. La restauración comprueba integridad y sólo restaura sus archivos; no revierte datos ni esquema. Conservar el respaldo completo vigente según la frecuencia acordada, sin generar uno nuevo por esta presentación.
