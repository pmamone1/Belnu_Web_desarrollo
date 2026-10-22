# Instalar MiDistri Pedidos Online v2 - contraparte de Urban v580
Repositorio Belnu_Web_desarrollo. Sólo /home/mcollini/belnuweb,
Python /home/mcollini/virtualenv/belnuweb/3.7/bin/python.
Base revisada10b49c4; no usar el ZIP ni el entorno de Urban Soft.
Guardar respaldo propio de la base MiDistri antes de la primera instalación; Urban tiene otra base.
Subir midistri_pedidos_online_v2_urban580.zip, verificar SHA256 del chat y CRC y extraer en staging nuevo.

```bash
(
set -e
umask 077
PAQUETE_MIDISTRI="/home/mcollini/midistri_pedidos_online_v2_urban580.zip"
unzip -t "$PAQUETE_MIDISTRI"
STAGING_MIDISTRI=$(mktemp -d /home/mcollini/staging_midistri_v2_XXXXXX)
unzip -q "$PAQUETE_MIDISTRI" -d "$STAGING_MIDISTRI"
/home/mcollini/virtualenv/belnuweb/3.7/bin/python "$STAGING_MIDISTRI/instalar.py" --root /home/mcollini/belnuweb
/home/mcollini/virtualenv/belnuweb/3.7/bin/python "$STAGING_MIDISTRI/instalar.py" --root /home/mcollini/belnuweb --apply
head -n 3 /home/mcollini/belnuweb/VERSION_DOCUMENTADA.txt
)
```

Valida store0017 aplicada y requests existente. Sólo migra midistri_portal0001–0002.
No instala dependencias, no sustituye media/.env ni configura cron/credenciales.
Conservar MIDISTRI_ENABLED=False hasta tener Urban v580, conexión y publicaciones.
Variables sólo en este cPanel: URBAN_API_BASE=https://sistema7000.belnu.com.ar/midistri/api/
URBAN_API_TOKEN=clave privada mostrada en Urban. No compartirla en el chat ni GitHub.
Urban debe tener MIDISTRI_BRIDGE_ENABLED=True para sincronizar.
Con portal aún apagado:
```bash
cd /home/mcollini/belnuweb
/home/mcollini/virtualenv/belnuweb/3.7/bin/python manage.py midistri_sincronizar
```
Revisar catálogo completo desde gestión staff /portal/gestion/ luego de habilitar MIDISTRI_ENABLED=True,
y autorizar un piloto concreto. Sin stock, reservas ni pago online.
Cron opcional independiente:
```cron
*/5 * * * * cd /home/mcollini/belnuweb && /home/mcollini/virtualenv/belnuweb/3.7/bin/python manage.py midistri_sincronizar >> /home/mcollini/midistri_catalogo.log 2>&1
```
No instalar el cron de Urban aquí.

## Recuperación
Conservar respaldo de código impreso. Apagar MIDISTRI_ENABLED y cron propio antes de restaurar
con python STAGING/instalar.py --root /home/mcollini/belnuweb --restore RUTA_RESPALDO.
Conserva tablas y pedidos; no restaurar base antigua ni revertir cargos Urban por volver atrás.
La restauración de código puede volver al portal anterior: revisar visibilidad antes de abrirlo.
