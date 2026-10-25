# Instalación 22

Verificar SHA256 de entrega. Base21. Instalar Urban605 primero y luego MiDistri22. No cambiar cron, remitentes, WhatsApp o venv. Sin nuevas migraciones; preflight rechaza pendientes ajenas. Instalación productiva pendiente.

```bash
(
set -e
umask 077
cd /home/mcollini
unzip -t midistri_pedidos_v22_ranking_analitica.zip
STAGING_MIDISTRI22=$(mktemp -d /home/mcollini/staging_22_XXXXXX)
unzip -oq midistri_pedidos_v22_ranking_analitica.zip -d "$STAGING_MIDISTRI22"
/home/mcollini/virtualenv/belnuweb/3.7/bin/python "$STAGING_MIDISTRI22/instalar.py" --root /home/mcollini/belnuweb
/home/mcollini/virtualenv/belnuweb/3.7/bin/python "$STAGING_MIDISTRI22/instalar.py" --root /home/mcollini/belnuweb --apply
head -n 3 /home/mcollini/belnuweb/VERSION_DOCUMENTADA.txt
)

(
set -e
cd /home/mcollini/sistema7000
/home/mcollini/virtualenv/sistema7000/3.10/bin/python manage.py midistri_actualizar_indicadores
cd /home/mcollini/belnuweb
/home/mcollini/virtualenv/belnuweb/3.7/bin/python manage.py midistri_sincronizar
)
```

Rollback coordinado de archivos verificados, seguido de renovación de cache y sincronización bajo el código restaurado. Sin revertir datos económicos ni históricos.
