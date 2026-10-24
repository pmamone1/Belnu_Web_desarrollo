# Instalación v15 — belnuweb

Instalar Urban599 primero y MiDistri15 después. Requiere base exacta598/14; el instalador se detiene ante diferencias. Sin nuevas migraciones ni variables. ConservaSMTP/WhatsApp/cron/venv. No enviar la campaña. El respaldo automático es de archivos; se conserva la frecuencia de respaldo de base acordada.

1. Subir midistri_pedidos_v15_codigo_agil.zip a /home/mcollini y cotejar su SHA256 con el informado junto al ZIP definitivo en la entrega del chat. No ejecutar un ZIP con hash diferente.
2. Tras verificar la huella, ejecutar este bloque sólo para esta aplicación:

```bash
(
set -e
umask 077
cd /home/mcollini
unzip -t /home/mcollini/midistri_pedidos_v15_codigo_agil.zip
STAGING_CODIGO=$(mktemp -d /home/mcollini/staging_codigo_v15_XXXXXX)
unzip -oq /home/mcollini/midistri_pedidos_v15_codigo_agil.zip -d "$STAGING_CODIGO"
/home/mcollini/virtualenv/belnuweb/3.7/bin/python "$STAGING_CODIGO/instalar.py" --root /home/mcollini/belnuweb
/home/mcollini/virtualenv/belnuweb/3.7/bin/python "$STAGING_CODIGO/instalar.py" --root /home/mcollini/belnuweb --apply
head -n 3 /home/mcollini/belnuweb/VERSION_DOCUMENTADA.txt
)
```

3. Si falla, conservar error y ruta del respaldo; no forzar hashes ni migraciones. Para recuperar únicamente archivos de esta entrega, revisar previamente el respaldo y usar el mismoinstalar.py con --root /home/mcollini/belnuweb --restore /ruta/del/respaldo. El instalador valida que no haya modificaciones posteriores y no revierte datos.
4. Después de ambos paquetes, cerrar la pantalla anterior e iniciar acceso con Email y código nuevo. La validación administrativa conserva la misma cuenta de Urban Soft y su alcance puntual. Verificar pegado, perfiles, ambos remitentes y devolución de error clara sin cambiar configuraciones. No usar producción para generar pedidos de prueba.
