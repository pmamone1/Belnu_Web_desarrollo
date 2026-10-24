# Acceso único por Email y perfiles de MiDistri

Fecha: 24/10/2026. Estado: diseño aprobado por el usuario el 24/10/2026; implementación local en preparación.
Fuentes inspeccionadas: Urban Soft v1.18.597 y MiDistri v13. No se modificó producción.

## Decisiones del usuario

- La entrada general al portal pide sólo el Email; no pide distribuidora.
- Un perfil habilitado entra directamente después de verificar el código.
- Varios perfiles habilitados muestran un selector después de verificar el código.
- Incluye kioscos/vendedores y las cuentas administrativas de Distribuidor o Urban que ya tengan acceso permitido a MiDistri.
- Los códigos salen de cada distribuidora, sin un nuevo remitente técnico general.
- Se conservan la vigencia de 30 minutos, un solo uso y la sesión por pestaña existente.
- Se conservan los remitentes propios, WhatsApp y la excepción expresamente configurada entre 20 y 65. No enviar campañas.

## Estado actual y motivo del cambio

MiDistri exige seleccionar una distribuidora en acceso_views.iniciar, antes de solicitar el código. Urban Soft sólo resuelve vendedores; acceso_codigo_alcance limita el desafío a una tienda o a su grupo expresamente compartido. La selección posterior de varios vendedores ya existe, pero no abarca cuentas administrativas. Éstas entran por un pase validado por Urban Soft y con permisos revalidados en servidor.

El cambio permite reconocer las pertenencias por Email sin pedir al usuario información que ya tiene el sistema. No basta con retirar el combo: hay que ampliar resolución, entrega y selección coordinadamente en ambos programas.

## Alternativas consideradas

1. Remitente técnico único para acceso: un correo y una sola verificación; requeriría otra configuración de envío. El usuario eligió conservar el remitente de cada distribuidora.
2. Elegir distribuidora antes del Email: reutiliza el circuito actual, pero contradice el ingreso solicitado.
3. Resolver el Email primero y entregar por los remitentes propios: alternativa elegida. Puede producir un correo por distribuidora si el Email pertenece a varias; no se mezcla información comercial entre ellas.

## Flujo propuesto

1. En /portal/ se ofrece Entrar con mi Email. Se retira de la entrada general el combo obligatorio de distribuidoras. Los enlaces públicos directos de una tienda siguen funcionando; abrirlos no determina ni concede una identidad.
2. Se ingresa Email; la respuesta pública es genérica tanto para conocidos como desconocidos. No se muestran nombres, tiendas, coincidencias ni resultados SMTP antes de verificar.
3. Urban Soft resuelve contactos habilitados de vendedores activos y cuentas administrativas activas por Email exacto normalizado, dentro de conexiones y tiendas habilitadas. No se crean cuentas, contactos ni permisos.
4. Se crea un desafío de 30 minutos con un código aleatorio de seis cifras, guardado sólo como hash, vinculado al navegador/pestaña. Se conservan límites por IP/Email e intentos.
5. Tras verificar el código, un perfil disponible continúa automáticamente. Si hay varios se muestra Elegí con qué perfil entrar.
6. Cada opción identifica el tipo de acceso, su nombre y su distribuidora; los vendedores incluyen LIN y VV para distinguir kioscos homónimos. Las opciones sólo aparecen al titular del Email ya verificado.
7. Vendedor abre su catálogo y pedidos. Administración abre la tienda o panel que permitan sus permisos actuales. No se inicia una sesión Django staff ni se concede SuperUsuario en MiDistri.
8. Al elegir un perfil se revalidan estado, contacto, cuenta, conexión, tienda y permisos. El identificador de opción es opaco, temporal y de un solo uso; no se aceptan IDs manipulados del navegador.

## Entrega por distribuidora (propuesta técnica)

- Un mismo desafío utiliza un único código por solicitud. Cada distribuidora destinataria envía un correo separado a ese Email mediante su remitente efectivo; el texto de cada correo sólo menciona esa distribuidora.
- Las pertenencias administrativas y de vendedor se agrupan por distribuidora para evitar duplicar correos de la misma tienda. La excepción 20/65 puede agrupar entrega únicamente cuando exista el vínculo compartido vigente y ambas pertenencias estén autorizadas.
- Se registra el resultado por entrega y su alcance, sin guardar el código en claro. Sólo se ofrecen perfiles cuyo alcance tenga entrega SMTP aceptada; una entrega de otra tienda no suple la entrega fallida de la propia.
- Si una tienda no tiene remitente válido, o falla SMTP, no se utiliza el de otra. Las demás entregas pueden continuar. No se confunde aceptación SMTP con recepción en bandeja.
- Una entrega por conciliar no se reenvía automáticamente. Reenviar crea una solicitud nueva con límites e invalida la anterior; no reproduce un intento SMTP incierto ni reenvía campañas.
- Si entregas de distintas tiendas terminan en momentos distintos, verificar consume el desafío y fija las opciones disponibles en ese momento. Las entregas aún no iniciadas se cancelan; una ya iniciada puede terminar y enviar el mismo código ya consumido, pero no amplía la sesión. El destinatario deberá pedir un código nuevo para cualquier alcance aún no disponible.
- Esta propuesta puede enviar más de un correo de código al titular de un Email compartido por varias tiendas. Es la consecuencia de conservar los remitentes independientes; cada tienda sólo conoce su propia entrega.

## Administración, Urban y permisos (propuesta conservadora)

- El Email validado descubre una cuenta administrativa, pero no sustituye su autenticación en Urban Soft. Al elegirla se reutiliza el pase administrativo existente: si la cuenta ya tiene sesión válida allí, continúa por ese circuito; en otro caso Urban Soft pide iniciar sesión.
- La cuenta que completa el pase debe ser la misma que se eligió tras verificar el código. Una sesión abierta de otra persona no autoriza ese perfil: se explica cómo iniciar con la cuenta correcta sin cerrar ni alterar otras sesiones de forma silenciosa.
- Urban es la pertenencia de origen de la cuenta, no un permiso nuevo. Sólo se ofrece administración de tiendas para las que tenga permisos actuales de MiDistri. Una cuenta Urban sin ese permiso no obtiene acceso por tener un Email conocido.
- Cada opción administrativa fija una distribuidora puntual. No se amplía automáticamente a otras ni a un consolidado por ser SuperUsuario. Cambiar a otra identidad exige regresar al selector o iniciar un acceso nuevo, nunca editar el parámetro distribuidora.
- Si varias cuentas activas comparten un Email, se distinguen por usuario y alcance. Nunca se selecciona por nombre visible ni se fusionan sus permisos. Deben autenticarse como la cuenta elegida.
- La lista inicial de perfiles es una pantalla de identidad del titular, no un listado general de distribuidoras. Una vez seleccionado un perfil puntual, sus pantallas no mencionan ni exponen datos de otros perfiles.

## Sesiones y compatibilidad

Se conservan la vinculación al navegador/pestaña, cierre explícito, protección CSRF y revalidación de permisos. No se modifican credenciales de Urban Soft ni configuraciones SMTP/WhatsApp. El código vence a los 30 minutos, no la sesión ya iniciada. Se conserva la política administrativa vigente de sesión/inactividad; cualquier cambio de duración administrativa queda fuera del alcance.

Los enlaces personales ya emitidos y las rutas de administración desde Urban Soft continúan compatibles. Los parámetros de tienda de campañas o enlaces públicos pueden dar contexto visual, pero no filtran silenciosamente las identidades elegibles del ingreso general ni conceden acceso.

## Componentes y contratos

Urban Soft: resolución de identidades tipadas, entrega con alcance y estado por distribuidora, verificación/selección y vinculación de cuenta al pase administrativo. MiDistri: entrada Email, selector de identidad y continuación al destino de vendedor o administrador. Versionar capacidades/API y activar coordinadamente; si falta soporte de alguna aplicación, indicar indisponibilidad en lugar de volver a pedir una distribuidora sin explicación.

Será necesario un registro aditivo de entregas por alcance: la entrega única actual no acredita un conjunto de tiendas independientes. El plan definirá los modelos y la migración exacta sin editar migraciones aplicadas. Desafíos antiguos conservan su contrato y alcance anterior hasta vencer; no se convierten en accesos globales. Nunca registrar Email completo, OTP, claves o tokens en logs técnicos; la auditoría funcional usa IDs y datos mínimos.

## Validación y entrega futura

Pruebas locales: un vendedor/un perfil; varios kioscos de una tienda; distintas tiendas/remitentes; excepción 20/65; contacto adicional habilitado; duplicados; bajas; vendedor y administrador con mismo Email; múltiples cuentas; Urban sin permisos; sesión administrativa de otra cuenta; manipulación de opción/tienda; contacto o permiso revocado entre pasos; código vencido/reutilizado; límites; SMTP fallido/por conciliar; alcance con aceptación parcial y carrera de entrega/consumo; compatibilidad de desafíos anteriores y enlaces personales; ausencia de datos de otras tiendas dentro del perfil seleccionado.

No usar producción como banco de pruebas. La entrega de implementación incluirá documentación técnica y manual de cada proyecto, versiones, changelogs, checklist, pruebas manuales, PDF principal donde corresponda, revisión final, commits GitHub y ZIP/comandos separados para cPanel. No instalar, cambiar SMTP, publicar productos ni enviar campañas durante preparación.

Rollback: desactivar la función nueva y conservar tablas aditivas y evidencias; no reactivar ni ampliar desafíos previos. No deshacer migraciones sobre actividad posterior, no tocar pedidos ni remitos históricos. Paquetes y activación deben permitir volver al acceso anterior sin borrar datos.

## Aprobación y estado

La decisión de mantener remitentes propios está confirmada. El usuario aprobó el diseño completo y su implementación, incluidas las entregas independientes por tienda y la conservación de la autenticación administrativa de Urban Soft. La migración productiva y aceptación real siguen pendientes; las pruebas locales se informan en la validación de entrega.
