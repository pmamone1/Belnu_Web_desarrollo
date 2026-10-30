# MiDistri-Pedidos v30 · Acceso recordado

## Guía de uso

Después de verificar el primer código de Email, MiDistri recuerda este dispositivo automáticamente, sin casilla para marcar ni vencimiento absoluto o por inactividad impuesto por la aplicación. El código inicial conserva sus treinta minutos y un solo uso.
Al volver en el mismo navegador entra directamente al perfil acreditado. Si hay varios kioscos acreditados, permite elegir uno. Cada pestaña conserva su carrito independiente. Cambiar perfil no concede nuevas distribuidoras por coincidencia de Email.
El botón «Salir y olvidar este dispositivo» cierra todas las pestañas de vendedor del dispositivo. Si no hay conexión, deja el olvido pendiente y lo confirma al reconectar, incluso después de cerrar y abrir el navegador.
El navegador debe conservar sus cookies: borrarlas, usar otro navegador o modo privado exige un nuevo código. La cookie se renueva con el uso dentro del límite del navegador (hasta 400 días); no se puede garantizar permanencia si el navegador la elimina.
La administración de distribuidoras continúa requiriendo la validación de Urban Soft. El bloque 20/65 sigue unido y las demás distribuidoras conservan su aislamiento.

## Detalle técnico

La credencial de dispositivo es UUID.secreto de 256 bits. Sólo su huella se guarda en ambos registros; el valor completo vive en cookie Secure, HttpOnly, SameSite=Lax y path /portal/. El token operativo de Urban permanece en el servidor. No se publica en HTML, JSON de respuesta ni localStorage. Hay una marca persistente de olvido sin secretos y un aviso entre pestañas.
Urban congela las identidades de vendedor verificadas por OTP y revalida habilitación, contacto y versión en cada uso. No incluye administración ni perfiles agregados posteriormente. El acceso origen admite un solo dispositivo; la repetición con la misma credencial es idempotente. Una credencial distinta o un registro revocado no se reactiva. El dispositivo no tiene campo de vencimiento; sólo la sesión operativa se renueva a 90 días subordinada al dispositivo vigente.
Contrato privado seller_device=1: POST seller-device-remember, seller-device-profiles, seller-device-resume y seller-device-revoke. Las opciones incluyen vendedor_id, distribuidora_id y selección opaca para validar la respuesta exacta. Las rutas de restauración/olvido del portal exigen POST y CSRF. La cookie no sirve para acceder a administración.
Las revocaciones locales pendientes se concilian oportunistamente (hasta tres por intento); no se agrega cron. Ante 503 se conserva la confianza y se ofrece reintentar; las revocaciones y bajas se respetan aun al apagar la bandera. Registrar un nuevo acceso por OTP sustituye el dispositivo anterior. Los accesos recordados nuevos se distinguen como ingreso_recordado en analítica; refrescar la misma pestaña no duplica el ingreso.
El secreto es estable hasta revocación o sustitución, sin rotación temporal que interrumpa pestañas concurrentes. Si se roba, seguirá siendo necesario revocarlo; la protección HttpOnly/HTTPS y las comprobaciones de autorización siguen siendo obligatorias. Una cookie perdida requiere OTP y no se reconstruye a partir de una invitación antigua.

## Compatibilidad, instalación y recuperación

Instalar Urban622 sobre621 y luego MiDistri30 sobre29. Ambos paquetes se verifican antes de aplicar. Cada instalador valida carpeta, venv, hashes y plan exacto, respalda sólo archivos reemplazados y detiene/reinicia su propia aplicación. Las banderas nuevas se entregan apagadas.
Después de ambas instalaciones, agregar MIDISTRI_ACCESO_RECORDADO_ENABLED=True en las variables de AMBAS Python Apps de cPanel y reiniciarlas. No borrar ni reemplazar otras variables. La bandera existente de códigos debe seguir habilitada. Ejecutar manage.py midistri_acceso_recordado_estado en ambos entornos: el portal comprueba también el contrato remoto, sin envíos ni cambios de datos. --local en el portal omite la llamada remota.
Para desactivar, poner la nueva bandera False en ambas y reiniciar. Conservar tablas y registros; no revertir migraciones ni borrar revocaciones. Antes de aplicar la nueva migración, --restore sólo admite los archivos verificados de su respaldo. Después de aplicar la migración o ante DDL parcial, corregir hacia adelante: el instalador bloquea restaurar código incompatible. En MariaDB se verifica coherencia entre la tabla del dispositivo, la FK de pestaña y el registro de migración; una creación parcial exige diagnóstico, no repetir a ciegas.

Migración aditiva: midistri_portal/0014_dispositivo_recordado. No modifica migraciones anteriores, pedidos, precios ni snapshots. Los registros anteriores quedan con dispositivo nulo; la confianza sólo se adopta desde un acceso OTP válido.

## Validación

Validación local: navegador Chromium por HTTPS con datos sintéticos; OTP inicial, cookie HttpOnly, sesión Django nueva, reinicio de contexto, selector de perfiles, dos carritos, fallo temporal y olvido sin conexión entre reinicios. Cuatro suites JavaScript aprobadas. Suite completa del portal: 261 pruebas, dos omisiones de compatibilidad documentadas; MariaDB 10.11 con SQLMode sin alterar. Urban: pruebas de contrato, autorización y concurrencia en PostgreSQL 17 local. La lectura del cliente real del portal se cruzó con JSON del endpoint real Urban mediante RequestFactory; no fue una prueba de red entre servidores productivos.
Las migraciones hacia adelante y su repetición conservaron los registros anteriores: acceso Urban sin dispositivo, carrito del portal, captura, intervalos y eventos. Los tests no envían correos reales ni campañas. El despliegue y la comprobación final del sitio real quedan pendientes de instalación.

## Estado de entrega

Bases Urban621 y MiDistri29 confirmadas instaladas por el usuario. El log de MiDistri29 confirma0013, captura activa y cuatro intervalos abiertos; respaldo de código81zg6eue. Esta versión nueva requiere instalación y activación en cPanel; publicar GitHub o crear ZIP no la instala.
