# MiDistri: acceso único y puesta en marcha por distribuidora

Fecha: 24/10/2026. Aprobación: el usuario aprobó este esquema e indicó implementarlo en este chat, con revisión final y paquetes separados; no enviar la campaña.
Base Urban eb8ed364eb31c3a1b6de4c0195faeba8c8844752; MiDistri 98a89a9cee5571ee54258cef2cf1af705487e8d1.

## Objetivo y enfoque
Un menú MiDistri independiente en Urban reúne configuración, catálogo y comunicación; los pedidos permanecen en Salidas / Pedidos. Un botón Acceso Distribuidor en el portal usa el ingreso de Urban y vuelve a Configurar MiDistri, sin copiar contraseñas ni crear usuarios de MiDistri. Se reutiliza la delegación actual con alcance y permisos vigentes.
Alternativas descartadas: otro login local duplicaría cuentas y permisos; cambiar el texto Pedidos sin cambiar destino engañaría al usuario. Se adopta el acceso único aprobado.

## Guía
Panel por distribuidora autorizada, seis pasos retomables: conexión, sitio, catálogo, Email, WhatsApp, revisión. Mostrar conexión no habilitada, permisos pendientes, configuración incompleta, datos completos pero conexión externa sin verificar, y enlaces concretos para completar. No afirmar entrega real por tener campos completos. Email es requisito de ingreso con código; WhatsApp es opcional para el sitio y requiere proveedor oficial y plantillas para envíos. Remitos y campañas conservan revisión, contactos habilitados y bajas.
La conexión técnica la habilita un administrador autorizado en la conexión existente; la guía explica el requisito y no activa de golpe todas las distribuidoras. Los responsables de distribuidora con vendedores.gestionar podrán configurar sus propios canales mediante un formulario acotado; otros usuarios ven instrucciones y motivo de falta de permiso. No se otorga un rol, conexión ni permiso automáticamente.

## Acceso
Entrada tanto desde Urban como desde el portal. Tras autenticación Urban normal, elegir la distribuidora cuando hay varias; no pedir elegir una conexión técnica si es única. Confirmación POST protegida inicia pase de un uso. Mantener origen, cookie firmada por desafío, expiración y permisos revalidados; no autoemitir pases mediante GET.
No mostrar checkbox de distribuidoras ajenas a la conexión elegida. Una conexión ausente muestra guía y explicación, no un selector vacío con botón habilitado.
El panel muestra Configurar MiDistri, Banners y promociones, Productos y Ver mi sitio según permisos. Pedidos conserva su destino y texto. Sin permiso de configurar, explicación visible de qué debe habilitar el responsable, sin eludir backend. La tienda elegida viaja firmada con el desafío; rechazar destinos externos y cualquier distribuidora ajena. Entradas paralelas no se pisan.

## Identidad de envío
Por defecto cada distribuidora usa su propio Email/WhatsApp. Única excepción autorizada: 20 - Belgrano y 65 - Barracas comparten explícitamente un remitente; mantener vínculos y credenciales existentes sin copiarlos ni alterarlos. Otras centralizaciones y la reutilización efectiva de la misma identidad entre distribuidoras independientes quedan bloqueadas con mensaje accionable. Validar tanto configuración como resolución/transporte; no recurrir a remitentes de otras distribuidoras ni al correo global. No exponer secretos ni lista de cuentas de otras distribuidoras.
Los permisos globales de administración y la auditoría se conservan; los responsables locales editan sólo su cuenta propia. No pueden crear remitentes centrales, reasignar identidad, leer secretos guardados ni usar claves de configuración del servidor. Las bajas y envíos inciertos siguen requiriendo sus circuitos actuales.

## Código de vendedor
El código conserva vigencia de 30 minutos, uso único y sesión por pestaña. Asociar el ingreso a la tienda pública elegida; desde el acceso general elegir una tienda del listado público antes de solicitar el código. Filtrar identidades por esa tienda y, únicamente si el remitente está compartido expresamente y validado, por 20/65. El Email sale del remitente de la tienda elegida, nunca del primer vendedor coincidente de otra tienda.
Guardar el alcance autorizado en el desafío (migración aditiva Urban). Revalidarlo al transportar, verificar y seleccionar; no ampliar por cambios de contacto/conexión. Compatibilidad antigua: solicitudes sin tienda sólo pueden enviarse y verificarse si todas sus identidades pertenecen a un único grupo permitido; ante ambigüedad pedir nuevo ingreso por tienda. Las sesiones ya emitidas mantienen su revalidación y duración. MiDistri antiguo puede pedir sin tienda sólo con esta regla segura; el nuevo portal negociará capacidad y explicará incompatibilidad.

## Límites y entrega
No modificar pedidos, cargos, precios, históricos, sincronización cada cinco minutos, campañas ni credenciales productivas. No hacer pruebas de envío en producción. Dos proyectos, ZIP e instaladores separados, Urban Python3.10 y MiDistri Python3.7. Instalar Urban primero y MiDistri después. Respaldo privado de archivos reemplazados; migración aditiva sin reversión automática de datos y corrección hacia adelante si hubo aplicación.
Actualizar manuales, PDF principal con capítulo vigente y verificación visual de unión, documentos y versiones; probar aislamiento, CSRF, usuarios sin permiso, alcance cambiado, dos pestañas, tienda ajena, canales incompletos, excepción20/65 y entregas existentes. Publicar commits reales y PR separados, sin merge ni instalación productiva.
