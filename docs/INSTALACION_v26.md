# Instalación MiDistri26

Acumulativo sobre23/24/25. Sólo portal; Urban606 se conserva. Verificar SHA256 de entrega antes de extraer.

```bash
(
set -e
umask 077
cd /home/mcollini
unzip -t midistri_pedidos_v26_catalogo_presentacion.zip
STAGING_M26=$(mktemp -d /home/mcollini/staging_m26_XXXXXX)
unzip -oq midistri_pedidos_v26_catalogo_presentacion.zip -d "$STAGING_M26"
/home/mcollini/virtualenv/belnuweb/3.7/bin/python "$STAGING_M26/instalar.py" --root /home/mcollini/belnuweb
/home/mcollini/virtualenv/belnuweb/3.7/bin/python "$STAGING_M26/instalar.py" --root /home/mcollini/belnuweb --apply
head -n 3 /home/mcollini/belnuweb/VERSION_DOCUMENTADA.txt
)
```

El instalador respalda archivos y reinicia la aplicación. Recargar navegador. No modificar cron ni sincronizar catálogo/indicadores por estos cambios. Instalación productiva pendiente; sin campaña.
