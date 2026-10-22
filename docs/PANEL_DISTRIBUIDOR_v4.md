# MiDistri-Pedidos v4 - Panel de Distribuidor

Estado: código preparado; instalación productiva pendiente. Requiere base Urban v582
y contraparte MiDistri v4. Dos repositorios, paquetes, bases y entornos separados.

## Uso

Salidas / Anuncios > Pedidos > Administrar MiDistri-Pedidos abre la aprobación de
entrada con la identidad actual. Revisar conexión y distribuidoras y entrar.
El portal tiene Productos, Pedidos y Mi tienda, según los permisos disponibles.
Cada petición vuelve a verificar usuario, pertenencia, permisos y conexión en Urban.

Productos admite publicación individual, seleccionada o de todo el catálogo activo,
con proveedor explícito para altas y revisión previa. Mantiene proveedores ya
asignados y precios maestros. Precio vendedor no positivo, inactivos o proveedor
no habilitado se excluyen con motivo. Máximo 10.000 publicaciones por conexión;
las publicaciones anteriores y nuevas comparten bloqueo y control de capacidad.
20 incluye 65 sólo en la intersección autorizada por usuario y conexión.
La copia del catálogo de vendedores se sincroniza después de confirmar; si falla,
se ofrece reintentar únicamente la sincronización.

Pedidos reutiliza el circuito nativo: Recibido -> OK -> Preparado/remito.
Revisar y Excel no generan cargos. Preparar exige revisión de 15 minutos,
confirmación explícita, permiso pedidos.remitos, pedidos.gestionar y autorización
financiera. El cargo/documento es idempotente y conserva precios e identidad
congelados. Cancelar por falta de stock sólo antes de emitir.

Mi tienda guarda logo, contacto, bienvenida e instrucciones públicos por
distribuidora. No cambia SMTP ni maestros. El logo se valida, recodifica a PNG y
adapta a 768 píxeles. Máximo original 2 MiB / 8 megapíxeles; rechaza SVG y archivos
corruptos. Cambios con revisión concurrente y UUID idempotente; historial local
y referencia confirmada en Urban. Si falta el acuse, no se repite el guardado.

Campañas > Enviar accesos a MiDistriPedidos permite todos, líneas o vendedores
puntuales. Un contacto habilitado por vendedor: principal o primer adicional;
se puede elegir otro en la selección individual de la página actual. La vista
previa permite revisar el destino efectivo. Las bajas se conservan y los que
no tienen Email se excluyen. No se habilitan contactos por inferencia.

Cada vendedor recibe su enlace; Email compartido no deduplica vendedores.
La invitación se genera sólo al procesar la cola y vence a las 48 horas.
Se guarda cifrada, nunca en texto común, exportaciones o logs. Un reintento
reutiliza la invitación del envío; si vence requiere nueva acción deliberada.
Una invitación nueva reemplaza las anteriores sin usar del mismo vendedor;
no revoca una sesión activa hasta activar la nueva invitación.
Aceptado significa aceptación SMTP, no prueba de entrega o lectura.
Por conciliar nunca se reenvía automáticamente. Reutiliza procesar_campanas;
no agregar otra tarea para el mismo procesamiento.

## Permisos y acceso entre aplicaciones

Se añaden midistri.catalogo_gestionar y midistri.tienda_configurar a Usuarios.
Un Distribuidor requiere permisos explícitos; no se migran ni amplían accesos
guardados. SuperUsuario funcional habilitado conserva su excepción. Urban Point
sin esa excepción conserva el límite privado actual. No se crean staff ni
superusuarios en MiDistri. La sesión de vendedor y la administrativa son distintas.

Protocolo de operador v1: desafío firmado en cookie breve del portal; código de
un uso por POST, vinculado a navegador, usuario, conexión y alcance, dura 120 s.
Credencial administrativa máxima 8 h / 30 min inactiva, hash en Urban y sesión
privada de servidor en Portal. La clave de aplicación no pasa al navegador.
El receptor del intercambio verifica Origin exacto y cookie/desafío antes del
canje privado; los demás formularios conservan CSRF.
Sólo la respuesta de traslado de Urban usa Referrer-Policy:origin para evitar
Origin:null en el POST entre aplicaciones; sólo revela el origen, sin rutas ni
consultas. Las demás pantallas conservan same-origin.

API existente snapshot/profile/orders sigue compatible. Operaciones operator-*
usan X-Midistri-Operator, independiente de X-Midistri-Session, y además la clave
privada de aplicación existente. Cada ID y permiso se revalida en Urban.

## Migraciones e instalación

Nuevas: midistri_bridge0005_operadores y consignaciones0122_midistri_campanas_acceso;
Portal midistri_portal0003_tienda_presentacion. Adiciones de tablas/columnas;
reemplazo de unicidad de envíos por unicidad condicional de promoción y vendedor.
No se reescriben filas antiguas, precios históricos, documentos, saldos ni stock.
No editar ni eliminar la migración histórica0015 registrada sin archivo.

Instaladores verifican hashes de la base real y plan exacto antes de reemplazar
código mediante grafo de migraciones superpuesto sólo en memoria; no modifican
la base durante la comprobación sin --apply. Repiten control después de copiar, respaldan archivos de
forma privada y reinician sólo la aplicación de ese paquete.
Urban migra consignaciones0122 incluyendo su dependencia bridge0005.

Después de instalar ambos: MIDISTRI_ADMIN_ENABLED=True en las dos aplicaciones.
Conservar MIDISTRI_BRIDGE_ENABLED=True en Urban y MIDISTRI_ENABLED=True en Portal.
Para invitaciones: MIDISTRI_EMAIL_ENABLED=True en Urban además de flags generales
COMUNICACIONES_ENVIOS_HABILITADOS/COMUNICACIONES_CAMPANAS_HABILITADAS, remitentes
válidos y COMUNICACIONES_CLAVE_FILE privada preparada. No cambiar ni publicar
URBAN_API_TOKEN existente. No generar una conexión distinta para resolver permisos.

La instalación mantiene los flags apagados por defecto si no se configuraron,
no publica productos ni crea accesos o envía Email por sí sola.
La sincronización de catálogo puede programarse cada cinco minutos en MiDistri;
revisar si ya existe antes de agregarla. La cola de campañas sigue en Urban.

Respaldo comprobado de referencia 21/10/2026; tres instalaciones Urban confirmadas
posteriores (v580-v582). Esta entrega no cuenta como instalada ni exige otro
respaldo completo por versión; política 30 instalaciones o 15 días. Siempre
respalda el código que reemplaza.

## Recuperación segura

Antes de cualquier recuperación, desactivar MIDISTRI_ADMIN_ENABLED en ambas
aplicaciones y pausar la cola de campañas para evitar nuevos trabajos.
El instalador --restore consulta MigrationRecorder ANTES de detener o reemplazar
archivos: si está aplicada cualquiera de las migraciones de esta entrega,
rechaza la restauración completa. Se debe preparar una corrección hacia adelante
sobre el esquema vigente; nunca devolver modelos anteriores sobre columnas nuevas.

Sólo se permite recuperar una copia parcial fallida ANTES de aplicar esas
migraciones, verificando respaldo y hashes. Los archivos nuevos de migraciones
se conservan incluso en esa recuperación. No revertir tablas, migraciones,
créditos, cargos, documentos ni Email. Si hubo acceso/campañas nuevos, conservar
sesiones, auditoría y resultados para conciliación; no dejar que un worker de una
versión anterior procese invitaciones como promociones. No fusionar repositorios
ni usar el ZIP de un proyecto en el otro.

## Validación

Ver VALIDACION_v4.md. Pruebas en bases sintéticas y Email simulado; producción
no se usa como entorno de prueba. La instalación y activación reales siguen pendientes.
