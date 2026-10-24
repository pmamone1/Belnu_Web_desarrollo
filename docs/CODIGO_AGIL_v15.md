# MiDistri-Pedidos v15: acceso y código

## Guía de uso

1. Entrá al portal con tu Email y pedí un código nuevo. Vale 30 minutos y se usa una sola vez.
2. En el Email el código aparece grande y en negrita. Copiá sólo sus seis números.
3. Pegalos en el campo o tocá Pegar código. Al completar los seis números, el portal los comprueba automáticamente. Entrar sigue disponible.
4. Si el navegador impide leer lo copiado, usá Ctrl+V o Pegar desde el teléfono. No se lee el portapapeles al enfocar el campo.
5. Si hay varios perfiles, elegí uno. La administración conserva la autenticación de la cuenta de Urban Soft y el alcance de esa distribuidora.
6. Después de instalar, iniciá el acceso de nuevo: un enlace anterior puede estar vencido. No actives DEBUG para corregir un403.

## Instalación y operación técnica

Causa reproducida: Referrer-Policy:no-referrer en el GET administrativo produce Origin:null/Referer ausente en el POST del navegador. Django rechaza la verificación CSRF. Urban usa origin en esta respuesta, conserva csrf_token y la verificación de usuario, desafío, vencimiento y consumo único. Referer contiene sólo esquema/host/puerto, nunca query con credenciales. No se agregan orígenes confiables ni excepciones csrf_exempt. El error de servidor no se convierte en DEBUG.

El transporte unificado de Urban envía multipart/alternative: texto simple conservado y HTML con código36px/negrita; los valores se escapan. Se mantiene cada remitente, Reply-To y aislamiento por distribuidora. El correo de acceso legado conserva su comportamiento anterior.

MiDistri escucha input/autofill y paste. Acepta exactamente seis dígitos, quitando sólo espacios. Impide el pegado de texto arbitrario sin truncarlo a un código. Una solicitud en curso bloquea duplicados. El mismo código no se reintenta automáticamente tras un error; editar o pulsar Entrar permite corregir. Reenviar reinicia el campo. La lectura del clipboard ocurre sólo por clic explícito; si no hay permiso, ofrece pegado manual. No se añade registro de códigos ni envío a servicios externos.

## Compatibilidad e instalación

Urban599 exige base598 y bridge0015 ya aplicada. MiDistri15 exige base14 y portal0009. Paquetes separados, Urban Python3.10 y MiDistri Python3.7. Sintaxis comprobada para esos destinos; pruebas locales en Python3.12 con Django5.2.15/3.2.15 respectivamente. Sin migraciones nuevas ni cambios en settings, permisos, economía, catálogo o documentos. No instala dependencias ni cambia cron/venv/SMTP/WhatsApp. Instalar primero Urban599 y después MiDistri15. El instalador compara hashes, verifica que no haya migraciones pendientes ajenas, respalda archivos reemplazados y reinicia sólo su aplicación.

## Recuperación segura

Ante fallo conservar salida y ruta del respaldo. Al ser una corrección sin esquema nuevo, el instalador admite --restore con el respaldo de esta entrega si los archivos no recibieron modificaciones posteriores. No restaurar bases ni borrar migraciones. Volver a598/14 restaura también el defecto de acceso/pegado; preferir corrección hacia adelante. No pedir un respaldo completo adicional fuera del intervalo acordado.

## Validación

Ver VALIDACION_v15.md. Producción, entrega SMTP real y navegación HTTPS entre ambos dominios quedan pendientes de aceptación tras instalar. No se usa producción como entorno de prueba ni se envía la campaña.
