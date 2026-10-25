# Instalación MiDistri21
Base exacta20 y esquema0010. Instalar Urban604 primero. Verificar SHA256 informado en la entrega; si no coincide, detenerse. Este paquete sólo instala belnuweb con Python3.7. Se respalda el código reemplazado, sin tocar credenciales ni venv. No ejecutar el paquete de Urban en esta carpeta.

```bash
(
set -e
umask 077
cd /home/mcollini
unzip -t midistri_pedidos_v21_clasificacion.zip
STAGING_MIDISTRI21=$(mktemp -d /home/mcollini/staging_midistri21_XXXXXX)
unzip -oq midistri_pedidos_v21_clasificacion.zip -d "$STAGING_MIDISTRI21"
/home/mcollini/virtualenv/belnuweb/3.7/bin/python "$STAGING_MIDISTRI21/instalar.py" --root /home/mcollini/belnuweb
/home/mcollini/virtualenv/belnuweb/3.7/bin/python "$STAGING_MIDISTRI21/instalar.py" --root /home/mcollini/belnuweb --apply
cd /home/mcollini/belnuweb
/home/mcollini/virtualenv/belnuweb/3.7/bin/python manage.py midistri_sincronizar
head -n 3 VERSION_DOCUMENTADA.txt
)
```

Conservar el cron actual5min y los remitentes propios. Después de0011 no hacer rollback ciego del código: corrección hacia adelante. No cambiar esquema histórico ni enviar campañas. Aceptación productiva pendiente.
