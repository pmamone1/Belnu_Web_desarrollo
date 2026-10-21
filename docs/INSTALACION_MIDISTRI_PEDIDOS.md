# Instalar SOLO en MiDistri - Pedidos Online

Repositorio pmamone1/Belnu_Web_desarrollo. Raíz /home/mcollini/belnuweb. Python App 3.7, entorno /home/mcollini/virtualenv/belnuweb/3.7. No instalar este ZIP en sistema7000/Urban Soft.

La entrega coordinada 20261021-midistri-v1 tiene un paquete distinto para Urban Soft. Instalar primero Urban y configurar conexión/publicaciones; luego este portal. No contiene bases, .env ni fotografías. No reemplaza el enlace media existente, aunque el nuevo catálogo utiliza exclusivamente fotos publicables de Urban.

1. Subir MiDistri_Pedidos_Online_Integracion_v1.zip y extraer fuera de public_html, en /home/mcollini/actualizaciones/MiDistri_Pedidos_Online_Integracion_v1.
2. Comprobar sin modificar:

```bash
source /home/mcollini/virtualenv/belnuweb/3.7/bin/activate
python /home/mcollini/actualizaciones/MiDistri_Pedidos_Online_Integracion_v1/instalar.py --root /home/mcollini/belnuweb
```

Comprueba base revisada 10b49c4267fb234cd02791dfcdbac9f578da8a6c (mismo código publicado anteriormente), schema store/0017 y huellas de código. Si difiere, detener y adaptar antes de copiar. No configurar MIDISTRI_ENABLED=True todavía.

3. Respaldar de forma completa y consistente la base MySQL de MiDistri desde cPanel; conservar respaldo separado del de Urban/PostgreSQL.
4. Aplicar con el entorno de MiDistri:

```bash
python /home/mcollini/actualizaciones/MiDistri_Pedidos_Online_Integracion_v1/instalar.py --root /home/mcollini/belnuweb --apply
```

Respalda archivos reemplazados fuera de public_html, comprueba Django/modelos, aplica migración de app midistri_portal, procesa estáticos y reinicia. No cambia .env ni borra fotos/productos/pedidos históricos. No instala dependencias nuevas en este proyecto: usa Django3.2/requests existentes y Python compatible3.7. Pruebas de esta entrega ejecutadas con Django3.2.14 sobre Python3.12 y análisis de sintaxis3.7; repetir controles en Python3.7 real de cPanel.

5. En belnuweb/.env o variables de SU Python App, configurar privadamente:

```dotenv
MIDISTRI_ENABLED=False
URBAN_API_BASE=https://sistema7000.belnu.com.ar/midistri/api/
URBAN_API_TOKEN=CLAVE_PRIVADA_MOSTRADA_EN_URBAN
```

No copiar settings.py/.env de Urban a MiDistri. Conservar SECRET_KEY, DATABASE_* y EMAIL_* actuales. No compartir URBAN_API_TOKEN ni incluirlo en GitHub.
6. Ejecutar `python manage.py midistri_sincronizar`. Debe informar publicaciones completas para las distribuidoras habilitadas. Si falla, conserva última copia; no habilitar portal vacío por intuición. Definir cron de MiDistri cada5min:

```cron
*/5 * * * * cd /home/mcollini/belnuweb && /home/mcollini/virtualenv/belnuweb/3.7/bin/python manage.py midistri_sincronizar >> /home/mcollini/midistri_catalogo.log 2>&1
```

7. Cambiar MIDISTRI_ENABLED=True y reiniciar Python App para comenzar el piloto autorizado. /store/, carrito, pedidos y registro antiguos redirigen al nuevo portal. Las URLs legacy no muestran el catálogo anterior; archivos e históricos se conservan. Catálogo público muestra PVP; vendedor identificado ve precio vendedor y PVP de su distribuidora. Cabecera MiDistri - Pedidos Online - {nombre distribuidora}. Gestión móvil de sync en /portal/gestion/ con usuario staff existente. Alta/enlaces/publicación/preparación se gestionan desde Urban /midistri/.
8. Abrir enlace personal por email/WhatsApp, tocar Entrar, elegir cantidades, revisar y enviar. Comprobar nombre/línea, reintentos, cancelación y remito/correo con un pedido expresamente autorizado. No hay pago online, reserva ni plazo automático por stock.

## Restauración
Desactivar MIDISTRI_ENABLED y cron. Restaurar SOLO archivos con:

```bash
python /home/mcollini/actualizaciones/MiDistri_Pedidos_Online_Integracion_v1/instalar.py --root /home/mcollini/belnuweb --restore /home/mcollini/RESPALDO_INDICADO
```

Sustituir por respaldo exacto impreso. El programa no modifica base ni revierte cargos en Urban. No restaurar una base antigua para deshacer código si ya ingresaron pedidos. Conservar app/tablas hasta reconciliar solicitudes locales pendientes y recibidas. Reiniciar app.

## Límites conocidos de esta primera entrega
Hasta100 pedidos recientes al actualizar estados; catálogo hasta10.000 publicaciones por snapshot completo y 24 productos/página. Reenvío de solicitud pendiente manual desde Mis pedidos; sync automático requiere configurar cron. Invitaciones WhatsApp se comparten con el botón; no se activa un envío masivo ni una API de WhatsApp. Correo de estados/remitos sale desde Urban y requiere transporte real configurado. La administración de productos/precios/fotos sigue siendo de Urban, con sus permisos existentes. Probar concurrencia en motores reales antes de apertura general.
