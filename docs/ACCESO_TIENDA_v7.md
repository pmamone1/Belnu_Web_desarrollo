# MiDistri-Pedidos v7 - Acceso con código y tienda

Implementado localmente; instalación y activación productivas pendientes. La campaña sigue sin enviarse.

## Arquitectura y permisos

Urban es autoridad de identidades, permisos, precios, documentos y SMTP. MiDistri mantiene presentación y sesiones de pestaña; no comparte repositorio, base ni instalación. Cada API administrativa revalida el usuario y su alcance privado. 20/65 sólo se agrupan si ambas están autorizadas.

OTP: hash salteado del código, 1800 segundos, un uso, cinco intentos. Respuesta genérica para Email inexistente. Límite por Email: tres emisiones por ventana móvil de 15 minutos y espera mínima de 60 segundos; IP: veinte solicitudes por ventana. No se confía en X-Forwarded-For. Si el proxy presenta una sola IP compartida, ajustar el despliegue antes de ampliar la audiencia.

El código se entrega después del commit en hasta ocho trabajadores efímeros del proceso. No se guarda el código en claro. Un reinicio del proceso puede interrumpir la entrega; pedir un nuevo código después de 60 segundos. No se reintenta automáticamente una aceptación SMTP incierta. SMTP real de producción no fue probado con destinatarios reales en esta entrega.

La prueba aleatoria de pestaña se guarda en sessionStorage; el token Urban sólo en el servidor. Cookie y prueba son necesarias. Carrito, filtros, revisión y mensajes están aislados. La vida del código no limita la sesión; el acceso remoto mantiene una concesión renovable de 90 días, además de revalidar el contacto. Salir borra la prueba antes de la llamada remota y revoca el acceso local; si no hay red, conserva un cierre pendiente y reintenta al volver la conexión, sin restaurar identidad. El navegador puede copiar/restaurar sessionStorage: no prometer detección infalible del cierre.

Callback administrativo: cookie firmada distinta por desafío, hasta diez, 600 segundos; pase Urban de 120 segundos, un uso y Origin exacto. El fallback de la cookie antigua sólo conserva su plazo de 120 segundos. Logs de fallo: motivo y referencia aleatoria, nunca código ni cookie.

Multimedia: originales y copias siguen fuera de MEDIA/STATIC. La publicación revisada crea copias inmutables con UUID/hash/tamaño. Endpoint GET/HEAD, Range simple, nosniff/noindex/no-store; retira el recurso si medio, producto, publicación o distribuidora dejan de estar activos. Fotos de producto usan derivados públicos ya existentes. Copias promocionales se activan sólo mediante referencia de un bloque autorizado; archivar la última referencia retira el recurso. No se eliminan originales ni auditorías.

MiDistri valida el contrato sin descargar URLs: origen Urban y rutas dedicadas para fotos/MP4; YouTube/Vimeo HTTPS según lista permitida. Nunca se solicitan destinos elegidos por el navegador. Subida P->U al endpoint fijo, 16 MiB más 64 KiB de margen multipart, temporales en Urban y validación real de contenido. requests construye multipart acotado en memoria, no hay dependencia nueva de video en P. CPanel/Passenger/servidor web deben admitir el tamaño; un 413 externo exige revisar ese límite, sin aumentar el límite JSON de 1 MiB.

Cambios comerciales con revisión/UUID y auditoría en Urban; campañas congelan la presentación al guardar/revisar el borrador. El remitente SMTP no se cambia por editar el nombre visible. Reply-To y pie salen de la presentación revisada. Las campañas anteriores conservan su modalidad y huella cuando no tienen la nueva presentación.

## Compatibilidad, migración y rollback

Base mínima: Urban584 / MiDistri6. Instalar P7 primero con flags nuevos apagados, luego U585. Mantener MIDISTRI_LOGIN_CODIGO_ENABLED=False en ambas durante la instalación y MIDISTRI_MULTIMEDIA_ENABLED=False en P. Después de verificar ambos paquetes y capacidades, habilitar login en U y P y multimedia en P, reiniciar ambas aplicaciones y sincronizar. No se instala nada en el venv ni se modifican claves, conexiones, catálogo, pedidos o destinatarios al instalar.

Urban agrega bridge0008_ingreso_codigo,0009_configuracion_tienda,0010_material_publicable,0011_uso_material_promocional y consignaciones0124_midistri_presentacion_campanas. MiDistri agrega portal0004_sesion_pestana,0005_configuracion_comercial,0006_multimedia_publicacion,0007_temas_promociones,0008_recuperacion_promociones. Son tablas/campos aditivos; las migraciones anteriores se conservan. No hay operaciones económicas ni reescritura histórica.

Instalador: verificar inventario/hashes, raíz, runtime, esquema base, dependencias y plan exacto antes de copiar. Sólo hojas finales como destinos y lista blanca de migraciones nuevas; rechaza reversiones/ajenas. Respaldo privado de archivos reemplazados, parada, check/modelos/migraciones/estáticos y arranque. Reintento del mismo paquete acepta archivos idénticos y migraciones aplicadas.

Ante fallo: conservar salida y respaldo. Si no se aplicó ninguna migración nueva, --restore valida todos los archivos antes de restaurar. Si hay migraciones nuevas, se bloquea el rollback de código: apagar funciones nuevas en ambas aplicaciones y corregir hacia adelante. No borrar tablas, accesos, cargos, snapshots o documentos para forzar la instalación.

No se exige otro respaldo completo de BD para esta entrega: respetar 30 instalaciones confirmadas o 15 días; no contar ZIPs, candidatos ni reintentos. El historial local antiguo registra 17/10 y existe un respaldo posterior comunicado en el chat; no se revalidó el archivo en esta ejecución ni se inventan instalaciones. No hay instalación585/7 confirmada.


## Correcciones de la revisión final

La sesión administrativa conserva el identificador del navegador y los ingresos por código pendientes. Su vencimiento remoto no acorta la sesión vendedor. Después de verificar el código, la elección entre vendedores tiene el plazo independiente de120segundos del ticket Urban.
Las promociones guardan una intención local durable antes de la confirmación remota, con UUID, contenido y revisión congelados. Una respuesta perdida se concilia con «Reintentar confirmación pendiente», incluso después de recargar; no se genera otra operación ni se publica contenido distinto. Un operador debe recuperar sus propias operaciones con permisos actuales.
La promoción de material de producto conserva su publicación de origen. Al sincronizar su baja o retirar ese recurso del catálogo, deja de aparecer. Los MP4 privados además se retiran en su origen; un enlace externo puede permanecer disponible fuera del portal. La baja no elimina el historial.
«Revisar promoción sin publicar» muestra título, texto, orden, destino y material antes de confirmar. Los archivos propios reservados se muestran mediante un proxy privado que vuelve a exigir sesión y permiso por distribuidora; el recurso público sigue inaccesible. La revisión firmada vale30minutos.
Las campañas agrupadas conservan las bases congeladas propias de cada distribuidora y distinguen sobreescrituras explícitas; editar título o fecha no copia los datos de20 a65. Vaciar una sobreescritura recupera la base congelada del borrador.
Salir sin red elimina la identidad visible y guarda únicamente un cierre pendiente en sessionStorage. Reintenta al volver la conexión o con el botón de reintento; no restablece la sesión. El cierre local es idempotente.

## Guía de uso

1. El vendedor abre belnu.com.ar/portal/ y toca Entrar con mi Email. Usa un Email habilitado en la agenda de su distribuidora; no se crea una cuenta nueva. El código tiene seis números, dura 30 minutos desde la emisión y se usa una vez. Si ese Email corresponde a varios vendedores, elige el suyo después de validarlo. Reenviar código respeta la espera de 60 segundos y los cupos; Cambiar Email permite corregirlo sin recargar.
2. La sesión se conserva mientras usa la pestaña, incluso después de vencer el código. Salir elimina la prueba local y revoca ese acceso en el servidor. En equipos compartidos usar siempre Salir. Una pestaña nueva no hereda la identidad sólo por tener la cookie; duplicar/restaurar pestañas puede restaurar sessionStorage, por lo que cerrar la pestaña no garantiza revocación.
3. El catálogo muestra Precio vendedor y PVP (precio al público). El pedido se calcula al precio vendedor. Tocando la foto se abre la galería: principal primero, miniaturas, anterior/siguiente y Cerrar. Escape cierra y devuelve el foco. Los MP4 tienen controles y no se reproducen solos; YouTube/Vimeo se abren en el origen.
4. La distribuidora entra desde Urban Soft > Salidas / Anuncios > Pedidos > Administrar MiDistri-Pedidos. Cada intento de entrada tiene su propia validación durante diez minutos; el pase final dura dos minutos. Si vence, iniciar un acceso nuevo desde Urban Soft. No reutilizar la dirección del resultado.
5. Mi tienda permite logo, contacto alternativo, bienvenida, instrucciones y siete temas. Nombre comercial y Email de respuesta se editan en Nombre comercial y mensajes de Email y se guardan en Urban. La preferencia de apariencia del visitante se guarda por tienda y no contiene identidad.
6. En Productos > Fotos y videos, seleccionar hasta diez videos existentes del producto, revisar y confirmar su publicación para esa distribuidora. Los originales privados no se publican al instalar. Sincronizar la copia del catálogo después de confirmar. Las fotos publicables se conservan y ordenan con la principal primero, hasta veinte.
7. En Mi tienda > Carruseles, fotos, videos y promociones, subir un archivo opcional, completar título, texto, enlace HTTPS, orden y Publicar en la tienda. Revisar promoción sin publicar muestra el material y el mensaje. Confirmar promoción revisada realiza la publicación. Hasta diez promociones activas, texto de hasta 1000 caracteres. Para archivar, abrir Editar, quitar Publicar, revisar y confirmar; conserva historial. Fotos hasta 5 MiB/20 megapíxeles; MP4 H.264/AAC hasta 16 MiB. No se publican hasta confirmar la revisión. Si se pierde la respuesta, usar Reintentar confirmación pendiente; se conserva la misma operación.
8. En Campañas elegir Acceso MiDistri y modalidad Portal con Email y código para enviar una URL general. Se pueden configurar nombre comercial, asunto, mensaje, entrega y Email de respuesta. Revisar la vista previa completa y destinatarios antes de confirmar. La modalidad de enlaces personales anteriores se conserva. Esta actualización no envía la campaña existente.
9. La bandeja MiDistri muestra el número de avisos pendientes y un acceso separado al historial, con filtros y páginas. Los avisos enviando o por conciliar exigen revisar el resultado antes de reenviar. Se mantienen contactos adicionales habilitados, deduplicación y bajas.
10. La preparación parcial conserva el circuito anterior: revisar por producto y cantidad, cancelar el resto por falta de stock, confirmar una vez y obtener el cargo y el mismo PDF para imprimir y compartir. No se reescriben pedidos, precios, remitos ni cargos históricos.
