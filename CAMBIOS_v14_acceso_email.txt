# MiDistri-Pedidos v14 - Acceso por Email y perfiles

Implementación local en preparación; instalación productiva pendiente. Campaña no enviada.

## Guía de uso

Entrá al portal y elegí Entrar con mi Email. Escribí un Email habilitado y pedí el código; ya no tenés que elegir distribuidora antes.
El código vale 30 minutos y sólo puede usarse una vez. No compartas el código. Si no llega, revisá correo no deseado y esperá al menos un minuto para solicitar otro.
Si tu Email tiene un solo perfil disponible, entrás directamente. Si tiene varios, elegí el vendedor/kiosco o el perfil administrativo que quieras usar.
Cada distribuidora envía su propio correo de acceso. Si pertenecés a varias, podés recibir varios correos con el mismo código. No se reemplazan los remitentes de las tiendas.
Un perfil administrativo conserva la autenticación de Urban Soft. Si no tenés sesión abierta allí, iniciá sesión con la cuenta elegida; luego confirmá la tienda. Esa confirmación tiene dos minutos de validez.
Si Urban Soft está abierto con otra cuenta, no se concede el acceso; entrá con la cuenta elegida y repetí el ingreso si venció.
Cada perfil permite únicamente las tiendas y tareas autorizadas. Ser contacto de un vendedor no otorga administración. Para terminar, elegí Salir; se conserva la sesión por pestaña de vendedores.
No se cambian catálogo, precios, pedidos, remitos ni configuraciones de Email/WhatsApp. Esta actualización no envía campañas.

## Instalación y operación técnica

Contrato login_email_perfiles=1 y acciones login-code-email-request/verify/select con versión2. El código se guarda como hash y se entrega después del commit, sin red dentro de bloqueos. IngresoEmail guarda desafío, intentos, identidades y ticket; EntregaIngresoEmail registra cada tienda y remitente, con pendiente/enviando/aceptado/fallido/por_conciliar/cancelado. ContinuacionIngresoEmail enlaza cuenta, tienda y desafío del pase administrativo.
Sólo las entregas aceptadas habilitan sus identidades, revalidadas al verificar y seleccionar. Pendientes se cancelan al consumir el código; una entrega ya iniciada puede terminar, pero no amplía las opciones fijadas. Remitentes faltantes o apagados no se sustituyen por los de otra tienda. Los trabajos inciertos no se repiten automáticamente.
Las cuentas administrativas activas se descubren por su Email y permisos actuales; la continuación exige la misma cuenta autenticada, CSRF y POST único. No concede staff ni cambia selección en otras pantallas. Los códigos, tokens y contraseñas no se registran en logs de aplicación.
Compatibilidad: desafíos y enlaces anteriores mantienen su alcance; no se migran a accesos globales. MiDistri14 admite el contrato anterior para formularios antiguos con tienda explícita; su formulario nuevo usa el contrato2. Urban598 debe instalarse antes de MiDistri14. Las banderas y remitentes existentes se conservan.
Migración Urban midistri_bridge0015_ingreso_email, exclusivamente aditiva: tres tablas, índice y unicidad por desafío/tienda. No edita migraciones aplicadas ni históricos. MiDistri14 no tiene migración propia y requiere esquema0009.
Recuperación: no revertir0015 ni restaurar la base sobre actividad posterior. Tras aplicarla, recuperar Urban hacia adelante. Para detener el ingreso con código, apagar MIDISTRI_LOGIN_CODIGO_ENABLED en ambas aplicaciones y reiniciar, conservando tablas/evidencias. MiDistri puede recuperar su código anterior con el respaldo verificado y Urban598 mantiene el contrato legado.
