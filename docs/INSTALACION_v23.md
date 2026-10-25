# Instalación 23

Base22. Instalar Urban606 y luego portal23; sin cambiar cron ni canales. Sin nuevas migraciones; preflight exige plan vacío. Producción pendiente.

```bash
(
set -e
umask 077
cd /home/mcollini
unzip -t midistri_pedidos_v23_historial_consignacion.zip
STAGING_V23=$(mktemp -d /home/mcollini/staging_v23_XXXXXX)
unzip -oq midistri_pedidos_v23_historial_consignacion.zip -d "$STAGING_V23"
/home/mcollini/virtualenv/belnuweb/3.7/bin/python "$STAGING_V23/instalar.py" --root /home/mcollini/belnuweb
/home/mcollini/virtualenv/belnuweb/3.7/bin/python "$STAGING_V23/instalar.py" --root /home/mcollini/belnuweb --apply
)
```

Tras instalar ambos: sistema7000/manage.py midistri_actualizar_indicadores con Python3.10, y belnuweb/manage.py midistri_sincronizar con Python3.7. Verificar SHA256 de entrega antes de extraer. El instalador verifica base y plan antes de copiar, respalda archivos y rechaza pendientes ajenas. Rollback de archivos mediante respaldo propio; recalcular indicadores y sincronizar con el productor restaurado. No revertir saldos, esquema ni históricos. Conservar respaldo de base vigente según política30 instalaciones/15días; el ZIP o un reintento no cuentan como instalación. Sin campaña ni prueba en producción.
