# Instalación MiDistri25

Sólo portal, acumulativo sobre23/24. Urban606 se conserva. Verificar SHA256 de entrega.

```bash
(
set -e
umask 077
cd /home/mcollini
unzip -t midistri_pedidos_v25_saludo_solo_nombre.zip
STAGING_M25=$(mktemp -d /home/mcollini/staging_m25_XXXXXX)
unzip -oq midistri_pedidos_v25_saludo_solo_nombre.zip -d "$STAGING_M25"
/home/mcollini/virtualenv/belnuweb/3.7/bin/python "$STAGING_M25/instalar.py" --root /home/mcollini/belnuweb
/home/mcollini/virtualenv/belnuweb/3.7/bin/python "$STAGING_M25/instalar.py" --root /home/mcollini/belnuweb --apply
head -n 3 /home/mcollini/belnuweb/VERSION_DOCUMENTADA.txt
)
```

Respaldo automático de archivos y reinicio por instalador; no cambiar cron ni sincronizar. Sin migraciones nuevas ni envíos. Recargar navegador. Instalación productiva pendiente.
