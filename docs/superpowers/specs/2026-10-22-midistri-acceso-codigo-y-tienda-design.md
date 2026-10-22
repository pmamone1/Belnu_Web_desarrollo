# MiDistri: ingreso con código, comunicaciones y tienda

Fecha: 22/10/2026, Argentina. Estado: diseño conversacional aprobado; documento y planes preparados para revisión. **Sin implementación ni instalación de estas funciones.**

## Intención y decisiones confirmadas

El vendedor debe poder abrir la URL pública o un enlace general de una campaña, escribir su Email y recibir un código. No depende de que la distribuidora genere previamente una invitación. El distribuidor debe administrar la presentación del portal, enviar campañas cuyo aspecto pueda revisar y consultar un historial ordenado de comunicaciones.

El usuario aprobó el diseño en este chat y pidió documentarlo y preparar el plan para ejecución por el agente principal en este mismo chat, con revisión final. Modificó la vigencia del código a **30 minutos**. La sesión iniciada debe permanecer al utilizar el portal; los 30 minutos no son un límite de sesión. Se busca terminar el acceso al salir o cerrar la pestaña, con la limitación de restauración del navegador explicada más abajo.

No enviar todavía la campaña existente ni invitaciones nuevas. Urban Soft y MiDistri conservan repositorios, instaladores, paquetes, claves y entornos separados. El sistema es un portal para pedidos, sin pago online; la distribuidora confirma disponibilidad. Mantener preparación parcial, cargo/remito idempotentes, precios históricos, contactos múltiples y permisos actuales.

## Base inspeccionada y evidencia

- Urban: commit `0c8fb003a03fc9383da0f7b2df160111b0b7fae1`, candidato v1.18.584, Python productivo 3.10 / Django 5.2.
- MiDistri: commit `6734ce86aced5cc199fd8320231eaffb80774c72`, candidato v6, Python productivo 3.7 / Django 3.2.
- La página pública actualizada mostró categorías, precio vendedor y PVP. Ejemplo observado: Lamborghini Parlante Blue, vendedor $43.700 y PVP $55.000. No se emitió pedido para comprobarlo.
- El código del carrito multiplica cantidad por `Publicacion.precio`, recibido de `Producto.precio_vendedor`; PVP se recibe de `pvp_sugerido` y no calcula el cargo.
- Pasaron 22 pruebas locales de contactos/envíos y 11 de catálogo/delegación en la investigación previa. No prueban la nueva funcionalidad, aún inexistente.
- El usuario volvió a informar el error «El acceso no pertenece a este navegador». Dos accesos nuevos desde Urban funcionaron en el navegador de este chat. Esto **no identifica la causa del fallo del navegador del usuario**.
- El callback administrativo actual reúne en el mismo 403: Origin incorrecto, cookie ausente, firma vencida y desafío distinto. La cookie única dura 120 segundos y otra entrada puede reemplazarla. Son condiciones comprobadas del código, no una causa productiva confirmada.
- No inferir instalación exacta ni contar instalaciones de una pantalla o de VERSION_DOCUMENTADA.txt. Conservar el cambio ajeno `templates/accounts/forgotPassword.html` de MiDistri fuera de este trabajo.

## A. Corregir primero el acceso administrativo

El error reiterado es la primera tarea de implementación. Diferenciar internamente `origin_invalid`, `cookie_missing`, `challenge_expired`, `signature_invalid` y `challenge_mismatch`, con referencia aleatoria y sin registrar cookies, códigos, secretos, Email ni URLs con desafío. El mensaje de usuario debe permitir **Iniciar de nuevo desde Urban Soft**, conservando las comprobaciones de servidor.

Reproducir localmente cada rama, dos pestañas, demora, atrás y reenvío del formulario. Usar una cookie firmada por desafío, cuyo nombre derive del hash del desafío, con Secure/HttpOnly, SameSite y ruta delimitada. El desafío de navegador durará 10 minutos; el pase emitido por Urban seguirá siendo de un uso y válido 120 segundos. No confundir esas duraciones con el código del vendedor. Una pantalla vencida debe iniciar un desafío nuevo, nunca conceder acceso con uno inválido. El panel delegado sigue durando hasta ocho horas y no crea usuarios staff ni amplía alcance.

Si el fallo no puede reproducirse fuera del navegador del usuario, entregar diagnóstico con referencias seguras y mantener explícito ese límite; no declararlo resuelto sólo por un acceso exitoso del agente. No desactivar comprobación de Origin, firma, vinculación al navegador ni CSRF del panel.

## B. Ingreso de vendedores con código

### Experiencia

1. Abrir `/portal/` y elegir **Entrar con mi Email**. Sólo el Email es obligatorio.
2. Mostrar siempre: «Si ese Email está habilitado, recibirás un código para ingresar». No revelar identidades ni existencia de contactos antes de verificarlo.
3. Enviar código numérico de seis dígitos, con ceros iniciales admitidos, de un uso y válido exactamente **1800 segundos desde su emisión**. Mostrar ingreso de código con pegado y autocompletado OTP.
4. Si hay una única identidad habilitada, entrar directamente. Si el Email está asociado a varios vendedores/distribuidoras, mostrar únicamente esas identidades después de verificar el código. Nunca elegir el primer resultado arbitrariamente.
5. Tras entrar, mostrar vendedor y distribuidora actuales y botón **Salir**. Cambiar de identidad requiere una elección autorizada, vacía el carrito anterior y no mezcla pedidos.

Se aceptan Email principal y contactos adicionales activos con Email habilitado, normalizados y sin duplicados. No usar nombre, LIN o VV como contraseña. Un Email no asociado no genera alta ni registro. La baja de campañas comerciales no impide un código solicitado por el titular; contacto desactivado, vendedor inactivo/depósito, distribuidora inactiva o conexión fuera de alcance sí impiden el acceso.

### Autoridad, seguridad y entrega

Urban resuelve identidades y emite el acceso; MiDistri presenta las pantallas. La clave entre aplicaciones permanece en servidor. El navegador no recibe el token de Urban ni listas de contactos ajenos. Cada desafío queda ligado a conexión, Email normalizado y prueba aleatoria de la pestaña. Guardar el código con hash de contraseña salado, nunca en texto ni en logs.

Cinco errores bloquean ese desafío. Reenvío mínimo cada 60 segundos, máximo tres solicitudes por Email/conexión en 15 minutos y veinte por IP en 15 minutos. Persistir contadores y reclamaciones en base para que funcionen entre procesos. No confiar en X-Forwarded-For sin proxy expresamente confiable. Contadores registran hashes con clave de Email/IP, no PII en logs. Reenviar invalida el código anterior de esa misma pestaña; no corta otras sesiones ya verificadas.

El Email de código se envía como comunicación transaccional mediante el remitente configurado de una asociación elegible del Email (selección determinista por ID de distribuidora). Un código cubre sus identidades autorizadas dentro de la conexión. Si ningún remitente elegible funciona, no se concede acceso; registrar fallo operativo seguro. SMTP se ejecuta después de confirmar la transacción, con estado reclamado y tiempo de espera limitado; un resultado incierto no se reenvía automáticamente. No reutilizar la cola de campañas ni exigir su habilitación. No depende de esperar un cron de cinco minutos. Tests usan transporte simulado, nunca destinatarios reales.

Endpoints privados entre servidores: `login-code-request`, `login-code-verify`, `login-code-select`; anuncio explícito de capacidades. Una aplicación antigua o una conexión caída deben dar indisponibilidad, nunca acceso alternativo menos seguro. Selección usa un ticket de verificación de un uso, válido dos minutos y ligado al desafío; revalida vendedor, contacto y alcance al consumirlo.

## C. Sesión ligada a pestaña

El código vence a los 30 minutos aunque no se use. Consumirlo antes del vencimiento inicia una sesión distinta: no cerrarla cuando venza el código ni por la regla heredada de inactividad de una hora.

MiDistri conserva el token de Urban sólo en servidor. La pestaña conserva en `sessionStorage` un ID aleatorio y una prueba aleatoria de 32 bytes; nunca en URL, localStorage ni enlaces. Cada consulta personal y mutación requiere cookie del navegador **y** prueba de pestaña. Una cookie sola no puede mostrar identidad, carrito, pedidos o remitos. El HTML público es neutro; los datos personales se cargan por peticiones autenticadas de esa pestaña. POST conserva CSRF y verificación de origen. Remitos se solicitan autenticados y se abren mediante un Blob temporal; no poner credenciales en la URL.

Recargar y navegar en la misma pestaña conserva la sesión. Una pestaña nueva ordinaria no hereda identidad; usar `noopener` en enlaces que abran otra pestaña. No emitir un cierre por `pagehide`/`beforeunload`: también ocurren al recargar y navegar. **Salir** revoca inmediatamente la sesión de esa pestaña en servidor y borra su identificación local, sin cerrar otras pestañas ni el panel del distribuidor. Acceso revocado, vendedor/contacto desactivado o fuera de alcance se rechazan en cada petición.

Cerrar normalmente la pestaña elimina su `sessionStorage`; el servidor no puede detectar de forma infalible ese cierre. Algunos navegadores restauran sessionStorage al reabrir/restaurar pestañas. Documentar que **Salir es el cierre garantizado**, y no prometer revocación inmediata al cerrar físicamente una pestaña. El secreto sin usar conserva el límite técnico vigente de 90 días; sesiones OTP activas renuevan ese límite al validarse, sin un corte diario mientras se usan. Esto no vuelve persistente el inicio en el navegador.

Los accesos antiguos por invitación siguen disponibles, pero al activarlos pasan al mismo mecanismo por pestaña. Una cookie heredada no se convierte silenciosamente en acceso nuevo: pedir código una vez, sin borrar pedidos. No modificar credenciales ni sesión administrativa de las otras aplicaciones.

## D. Campañas y mensajes configurables

Urban administra una configuración MiDistri por distribuidora: nombre comercial visible (150 caracteres), Email de respuesta/contacto (254), asunto (150), texto de presentación (3000) y texto de entrega opcional (500). Todo texto es plano y escapado; rechazar CR/LF en cabeceras. Respetar `midistri.tienda_configurar` y alcance privado.

Los valores predeterminados de campañas se guardan en Urban, para evitar depender de una llamada inversa al portal durante SMTP. Cada campaña permite sobreescribir nombre visible, asunto, texto y Email de respuesta; la vista previa muestra cabecera, cuerpo, botón/enlace y pie exactos. Congelar estos valores al confirmar. Cambiarlos luego exige nueva revisión, no reescribe envíos pasados.

Nueva modalidad **Invitar a pedir en MiDistri con Email y código** usa URL pública general, con distribuidora sugerida, sin tokens personales ni vencimiento ficticio del enlace general. Mantener modalidad de enlace personal para compatibilidad y nombrarla de forma distinta. El código sólo se manda cuando el vendedor lo solicita en el portal. Mostrar: «Portal para realizar pedidos. La distribuidora confirma disponibilidad. Sin pago online». No prometer 48 horas salvo texto que la distribuidora configure y revise.

`Reply-To` usa el Email configurado y coincide con el pie visible. La dirección SMTP `From` sigue siendo la autorizada del remitente; el nombre visible puede personalizarse. Una cuenta SMTP compartida entre 20/65 no obliga a compartir nombre comercial o Email de respuesta. Sin configuración específica se usa el responsable del remitente actual.

Seleccionar un vendedor en una campaña MiDistri incluye todos sus destinos Email activos/habilitados, con opción explícita de elegir uno. Mantener deduplicación y bajas por destino; nunca reactivar bajas por este cambio. El aviso de pedido preparado usa el mismo PDF congelado para sus contactos. La campaña existente permanece borrador: no confirmar, encolar ni enviar durante implementación, instalación o revisión.

## E. Bandeja e historial de avisos

En Urban, sustituir párrafos sueltos por tabla con fecha, vendedor, distribuidora, pedido, tipo de aviso, estado, destinatarios y acción. Predeterminar pendientes/errores; pestaña separada de historial, búsqueda, filtros de estado/tipo/fecha y paginación de 25 filas. Detalle muestra el resultado por destinatario; ver el registro no envía ni resuelve.

Conservar permisos de vendedor y alcance privado antes de filtrar/paginar y en URLs directas. Estados aceptados/cancelados son consultables; ocultar historial no borra auditoría. Estados enviando/por conciliar nunca se reenvían automáticamente; se conserva la conciliación explícita existente y sus requisitos. Enlazar detalle de envío cuando corresponda, sin mostrar códigos de ingreso ni secretos de invitación.

## F. Galerías de producto y tienda

### Productos

Tocar la foto abre un visor con foto principal primero, resto por orden, miniaturas, anterior/siguiente, cierre, Escape, foco restaurado y controles grandes. Teléfono y PC; mantener filtros y posición del catálogo al cerrar. Mostrar precio vendedor y **PVP (precio al público)**. Videos MP4 con controles, sin reproducción automática ni audio inesperado; enlaces YouTube/Vimeo se muestran con vista previa/botón y origen autorizado. Si un recurso falla, conservar los demás y mostrar indisponibilidad puntual.

Hoy el snapshot ya incluye imágenes publicables, pero no los videos privados de producto. Ampliar el contrato con multimedia tipada, ordenada y acotada: hasta 20 fotos y 10 videos por producto, texto de hasta 300 caracteres. Publicar sólo productos activos publicados para esa distribuidora. La publicación de videos requiere selección/revisión visible por el distribuidor; instalar no vuelve públicos archivos privados existentes.

Los MP4 privados de Urban permanecen privados. Crear una copia publicable validada e inmutable sólo de los seleccionados, sin exponer rutas del disco ni la URL autenticada de Urban. Endpoint público dedicado valida publicación activa/consentimiento multimedia y hash en cada acceso, incluyendo peticiones Range; al retirar el material deja de servirse. Nunca incluir rutas internas, credenciales o contacto en el snapshot. MiDistri valida origen HTTPS y rutas exactas; rechazar URL arbitraria/redirect/SSRF. No descargar enlaces externos desde servidor. La copia publicable y los originales se excluyen de los ZIP.

### Presentación de cada distribuidora

Ampliar **Mi tienda** con nombre comercial, logo, contacto, bienvenida/instrucciones y tema: claro, nocturno, azul, verde, terracota, violeta pastel y ámbar pastel. Tema predeterminado por tienda y cambio local de preferencia del visitante sin alterar otra tienda. Mantener contraste legible y controles accesibles.

Promociones: hasta diez bloques activos por tienda; cada uno permite título (150), texto (1000), enlace HTTPS opcional y un recurso (foto, MP4 o enlace YouTube/Vimeo). Ordenar, previsualizar, activar/archivar. Carrusel con navegación manual, sin avance automático. Preferir reutilizar material publicable de productos; también permitir subir material propio de la tienda. Fotos JPG/PNG/WebP hasta 5 MiB y 20 megapíxeles; MP4 H.264/AAC hasta 16 MiB. Validar contenido real, metadatos, dimensiones/tamaño e integridad antes de guardarlo; SVG, HTML y ejecutables no se aceptan.

Las subidas propias desde el panel MiDistri se transfieren a un endpoint privado fijo de Urban que revalida permiso/alcance y reutiliza los validadores v579 de su runtime Python3.10. MiDistri Python3.7 no necesita instalar otro validador de video. Limitar multipart a 16 MiB de archivo más margen fijo de formulario; no ampliar el límite JSON general de la API ni seguir destinos elegidos por el cliente. Archivos privados/pendientes no se publican por el alias MEDIA. Auditoría por operador, tienda y revisión; una edición concurrente obsoleta debe rechazarse.

## G. Compatibilidad, migración y entrega

Tres subplanes independientes, en este orden: acceso (incluye error administrativo), comunicaciones, galerías/presentación. Coordinación y entrega conjunta en el plan principal. Candidatos previstos Urban v1.18.585 y MiDistri v7; no son releases implementadas ni instaladas.

Migraciones exclusivamente aditivas en ambas bases: desafíos/cupos/sesiones y sus vínculos; configuración/campos congelados; material publicable y presentación. No editar migraciones aplicadas ni introducir unicidad retroactiva sobre contactos existentes. Determinar nombres siguientes contra hojas reales durante implementación y fijarlos en manifiestos/instaladores. No cambiar importes, stock, pedidos ni documentos históricos.

Mantener los runtimes y raíces productivas: Urban `/home/mcollini/sistema7000`, Python3.10; MiDistri `/home/mcollini/belnuweb`, Python3.7. Para esta entrega la base mínima será U584/P6, validada por archivos y esquema; no instalar sobre versiones viejas por aproximación. Instalación P7 primero con funciones nuevas apagadas, U585 después; activar ingreso por código sólo al comprobar capacidades compatibles de ambas. Catálogo actual continúa disponible durante despliegue mixto. Variables nuevas `MIDISTRI_LOGIN_CODIGO_ENABLED=False` en ambos y `MIDISTRI_MULTIMEDIA_ENABLED=False` en MiDistri, apagadas por defecto.

Rollback: apagar flags nuevos, conservar datos y esquema aditivo y corregir hacia adelante si hay sesiones/material nuevo. Nunca deshacer créditos/cargos ni borrar migraciones para forzar reinstalación. Respaldo privado automático del código reemplazado; no pedir backup completo nuevo fuera de la frecuencia acordada. Último backup confirmado 21/10/2026; no inventar instalaciones nuevas por estas verificaciones.

Actualizar documentación obligatoria, manuales Markdown y PDF principales con capítulo vigente y revisión visual de unión. ZIPs independientes, SHA256, comandos cPanel completos, commits reales publicados y PRs separados. No incluir credenciales, bases, archivos privados, entornos ni cambios ajenos.

## H. Criterios de aceptación y revisión

- Fronteras de 1800 segundos, un uso concurrente, cinco errores, reenvío/cupos, Email no existente sin filtración; ningún SMTP real en pruebas.
- Varios vendedores para un Email; varios Email para un vendedor; bajas de campaña separadas del acceso solicitado; cambio/desactivación/revocación actual bloquea acceso.
- Permanecer más de 30 minutos, navegar/recargar, pestaña nueva sin acceso, Salir con red perdida y posterior rechazo/reintento; restauración documentada sin promesas falsas.
- Callback delegado con expiración, cookie ausente, Origin falso, pestañas simultáneas, repetición y API caída, sin debilitar permisos.
- Cabecera, Reply-To y pie coinciden con lo aprobado; campaña borrador intacta; historial/conciliación por destino sin reenvío implícito.
- Foto principal, resto de galería, MP4/enlaces, recurso faltante, Range, producto/material retirado y enlaces maliciosos; ningún acceso a archivos privados.
- Temas legibles en celular, teclado, carga lenta y JavaScript desactivado: catálogo público consultable y explicación para ingreso; sin fuga de identidad por cookie.
- Regresión de preparación parcial, precios congelados, remito idempotente y reporte agregado sin identidad. Pruebas reales de concurrencia en PostgreSQL local, compatibilidad Python3.7 y ensayo MariaDB para migraciones MiDistri.
- Revisión final independiente después de implementar y verificar. La suite histórica Urban tiene fallos previos documentados en v584: comparar cualquier fallo relevante, sin afirmar que toda la suite está verde.
