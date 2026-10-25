# Instalación MiDistri24

Sólo portal, sobre23. Urban606 no cambia. Verificar SHA256 de entrega antes de extraer.

```bash
(
set -e
umask 077
cd /home/mcollini
unzip -t midistri_pedidos_v24_encabezado_sin_lin.zip
STAGING_M24=$(mktemp -d /home/mcollini/staging_m24_XXXXXX)
unzip -oq midistri_pedidos_v24_encabezado_sin_lin.zip -d "$STAGING_M24"
/home/mcollini/virtualenv/belnuweb/3.7/bin/python "$STAGING_M24/instalar.py" --root /home/mcollini/belnuweb
/home/mcollini/virtualenv/belnuweb/3.7/bin/python "$STAGING_M24/instalar.py" --root /home/mcollini/belnuweb --apply
head -n 3 /home/mcollini/belnuweb/VERSION_DOCUMENTADA.txt
)
```

El instalador respalda archivos y reinicia la aplicación. Sin migraciones nuevas ni cambios de datos/canales/cron. No recalcular indicadores ni sincronizar por este cambio. Recargar navegador después. Instalación productiva pendiente.
