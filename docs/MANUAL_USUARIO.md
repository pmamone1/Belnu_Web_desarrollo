## MiDistri-Pedidos v15 — Acceso y código

Pegar o completar los seis números verifica el código automáticamente una sola vez. Hay botón Pegar código y alternativa Entrar. Se conserva la elección entre perfiles.

Guía vigente: [CODIGO_AGIL_v15.md](CODIGO_AGIL_v15.md). Requiere Urban599 + MiDistri15 sobre bases598/14, sin migraciones nuevas. Instalación productiva pendiente.

## MiDistri-Pedidos v14 · Ingreso por Email

Email y código30min, selección de perfil sólo después de verificar. Remitentes propios por tienda; administración autenticada en Urban Soft con alcance puntual. Conserva el contrato anterior y configuraciones existentes.

Guía vigente: [ACCESO_EMAIL_v14.md](ACCESO_EMAIL_v14.md). Prevalece para este flujo. Requiere Urban598 + MiDistri14; instalar en ese orden. Producción pendiente; sin campañas.

## MiDistri-Pedidos v13

Acceso único de Distribuidor, menú MiDistri y guía por tienda con remitentes propios; excepción20/65. Pedidos separados y código30min ligado a tienda. Instalación productiva pendiente; campaña sin enviar.

Guía vigente: [GUIA_v13.md](GUIA_v13.md). Esta sección tiene prioridad para los flujos afectados. Mantener permisos y no usar remitentes ajenos.

## MiDistri-Pedidos v12

Banners de ancho completo, fotos más grandes y fundido accesible. Conserva cuatro diseños/temas, la página anterior y la sesión por pestaña. Sin cambios de catálogo, precios ni permisos; producción pendiente.

Guía vigente: [BANNERS_v12.md](BANNERS_v12.md). Validación: [evidencia](VALIDACION_v12.md).

## MiDistri v11 — Tienda con borrador y referencias

Cuatro diseños, mensajes y banners de productos con previa PC/celular y publicación completa. Referencia breve de Urban, conservando UUID y originales. Migración0009 preserva página vigente. Requiere Urban591; instalación productiva pendiente; sin campaña ni cambios SMTP.

Guía: [TIENDA_REFERENCIAS_v11.md](TIENDA_REFERENCIAS_v11.md). Evidencia: [VALIDACION_v11.md](VALIDACION_v11.md).

## MiDistri-Pedidos v10 - Catálogo coordinado

Operación cada cinco minutos con Urban v588: altas autorizadas, cambios y bajas, conservando exclusiones, ocultos y pedidos anteriores. Mantiene sincronizador/API y galería v9; acumulativo v8/v9, sin migraciones nuevas. Instalación v10 y cron productivos pendientes. El video Alma Chocolate141 ya fue publicado/sincronizado para20/65 según confirmación del usuario y lectura del portal23/10/2026. SMTP y campaña sin cambios.

Guía vigente: [CATALOGO_AUTOMATICO_v10.md](CATALOGO_AUTOMATICO_v10.md). Prioridad sobre instrucciones antiguas para este flujo.

## MiDistri-Pedidos v9 - Galería sin controles redundantes

Con un recurso se ocultan flechas y miniaturas; con varios se conserva la navegación de fotos y videos. Sin migraciones nuevas, cambios de permisos, precios o pedidos. Instalación productiva pendiente. El diagnóstico confirmó que el video2 de Alma Chocolate no está publicado para19/68 (20/65); requiere publicación expresa y sincronización, no se resuelve sólo instalando esta versión.

Guía vigente: [GALERIA_v9.md](GALERIA_v9.md). Para el resto del portal se mantiene v8.

1. Tocá la foto del producto para ampliarla. Si tiene un solo recurso, la ventana muestra la foto y Cerrar, sin flechas ni miniaturas para repetir la misma imagen.
2. Si hay varias fotos o videos publicados, aparecen Anterior, Siguiente y las miniaturas para elegir. Las fotos se mantienen con la principal primero.
3. Los videos MP4 publicados tienen controles de reproducción. Los enlaces de YouTube y Vimeo muestran un botón para abrir el video en su sitio de origen.
4. Que un video figure en Productos de Urban Soft no significa que ya esté publicado en MiDistri. En Administrar MiDistri-Pedidos > Productos > Fotos y videos, elegir el video, revisar y confirmar su publicación para la distribuidora correspondiente.
5. Después de publicar, sincronizar el catálogo de MiDistri para recibir el material. Si todavía no aparece, revisar publicación y última sincronización antes de volver a subirlo.


## MiDistri-Pedidos v8 - Fotos, textos y cuatro temas

Vigente sobre v7 r2 confirmada por el usuario; instalación v8 pendiente. Apariencia: Claro, Nocturno, Azul y Verde. Catálogo para el Kiosco, texto de disponibilidad simplificado, fotos en carrito y detalle, y botón «Armar un nuevo pedido». Fotos actuales de la misma distribuidora; cantidades y precios históricos intactos. Sin modelos, migraciones nuevas, cargos ni campañas. No requiere actualización Urban Soft.

Guía vigente: [FOTOS_PRESENTACION_v8.md](FOTOS_PRESENTACION_v8.md). Este capítulo prevalece sobre los temas y textos de versiones anteriores.

1. En Apariencia quedan Claro, Nocturno, Azul y Verde, tanto para visitantes como en Mi tienda del Distribuidor. Preferencias retiradas se muestran como Claro; no se borra la configuración guardada.
2. El catálogo encabeza «Elegí los productos para tu Kiosco!». Debajo dice «Portal para realizar pedidos. La distribuidora confirma disponibilidad.»
3. Al abrir Ver mi pedido se muestra la foto de cada producto junto a su nombre, cantidades, precio vendedor y PVP. Tocando la foto se abre ampliada. Si no hay foto disponible, aparece «Foto pendiente».
4. Antes de enviar se informa: «Este pedido queda sujeto a disponibilidad y aceptación por parte de la distribuidora.» El pedido se sigue calculando al precio vendedor.
5. El detalle del pedido recibido también muestra las fotos. El botón se llama «Armar un nuevo pedido» y abre la revisión del nuevo carrito antes de enviarlo. Revisar siempre cantidades y precios allí.


## MiDistri-Pedidos v7 r2 · Recuperación de instalación

Corrige el error de configuración que detuvo el v7 en Django check. Usar el ZIP r2 completo para retomar el intento; no editar hashes ni settings a mano. Conserva el circuito aprobado. Instalación r2 productiva pendiente; el intento comunicado no llegó a migrar. Ver [recuperación y compatibilidad](RECUPERACION_MIDISTRI_v7_r2.md).

## MiDistri-Pedidos v7 - Acceso con código, galerías y tienda

Vigente revisión final: promociones con revisión privada y confirmación separada; recuperación durable de respuestas perdidas; retiro por fuente vigente; campañas20/65 conservan sus datos propios. Salir reintenta el cierre sin restaurar identidad. Ver guía de esta versión.


Implementación local integrada; instalación productiva pendiente. Código de30min, sesión por pestaña, recuperación del acceso Distribuidor, campañas configurables, avisos con historial, galerías y siete temas/promociones. Conserva precios, preparación parcial, contactos y permisos. Instalar MiDistri7 primero y Urban585 después con funciones nuevas apagadas; activar coordinadamente. La campaña no se envía.

## Pasos actuales

1. El vendedor abre belnu.com.ar/portal/ y toca Entrar con mi Email. Usa un Email habilitado en la agenda de su distribuidora; no se crea una cuenta nueva. El código tiene seis números, dura 30 minutos desde la emisión y se usa una vez. Si ese Email corresponde a varios vendedores, elige el suyo después de validarlo.
2. La sesión se conserva mientras usa la pestaña, incluso después de vencer el código. Salir elimina la prueba local y revoca ese acceso en el servidor. En equipos compartidos usar siempre Salir. Una pestaña nueva no hereda la identidad sólo por tener la cookie; duplicar/restaurar pestañas puede restaurar sessionStorage, por lo que cerrar la pestaña no garantiza revocación.
3. El catálogo muestra Precio vendedor y PVP (precio al público). El pedido se calcula al precio vendedor. Tocando la foto se abre la galería: principal primero, miniaturas, anterior/siguiente y Cerrar. Escape cierra y devuelve el foco. Los MP4 tienen controles y no se reproducen solos; YouTube/Vimeo se abren en el origen.
4. La distribuidora entra desde Urban Soft > Salidas / Anuncios > Pedidos > Administrar MiDistri-Pedidos. Cada intento de entrada tiene su propia validación durante diez minutos; el pase final dura dos minutos. Si vence, iniciar un acceso nuevo desde Urban Soft. No reutilizar la dirección del resultado.
5. Mi tienda permite logo, contacto alternativo, bienvenida, instrucciones y siete temas. Nombre comercial y Email de respuesta se editan en Nombre comercial y mensajes de Email y se guardan en Urban. La preferencia de apariencia del visitante se guarda por tienda y no contiene identidad.
6. En Productos > Fotos y videos, seleccionar hasta diez videos existentes del producto, revisar y confirmar su publicación para esa distribuidora. Los originales privados no se publican al instalar. Sincronizar la copia del catálogo después de confirmar. Las fotos publicables se conservan y ordenan con la principal primero, hasta veinte.
7. En Mi tienda > Carruseles, fotos, videos y promociones, subir un archivo opcional, completar título, texto, enlace HTTPS, orden y Publicar en la tienda. Hasta diez promociones activas. Para archivar, abrir Editar, quitar Publicar y guardar; conserva historial. Fotos hasta 5 MiB/20 megapíxeles; MP4 H.264/AAC hasta 16 MiB. No se publican hasta guardar el bloque.
8. En Campañas elegir Acceso MiDistri y modalidad Portal con Email y código para enviar una URL general. Se pueden configurar nombre comercial, asunto, mensaje, entrega y Email de respuesta. Revisar la vista previa completa y destinatarios antes de confirmar. La modalidad de enlaces personales anteriores se conserva. Esta actualización no envía la campaña existente.
9. La bandeja MiDistri muestra el número de avisos pendientes y un acceso separado al historial, con filtros y páginas. Los avisos enviando o por conciliar exigen revisar el resultado antes de reenviar. Se mantienen contactos adicionales habilitados, deduplicación y bajas.
10. La preparación parcial conserva el circuito anterior: revisar por producto y cantidad, cancelar el resto por falta de stock, confirmar una vez y obtener el cargo y el mismo PDF para imprimir y compartir. No se reescriben pedidos, precios, remitos ni cargos históricos.

Documentación vigente: [ACCESO_TIENDA_v7.md](ACCESO_TIENDA_v7.md). Instrucciones anteriores que siguen son antecedentes y no prevalecen sobre este capítulo.

## Manual vigente v6 · pedidos de MiDistri

1. Abrir **Salidas / Anuncios > Pedidos > Pedidos web de MiDistri** y marcar OK lo recibido.
2. **Confirmar preparación** abre una revisión. Desmarcar productos sin stock o cambiar sus cantidades. Los precios no se cambian.
3. **Revisar cantidades e importe**, comprobar preparados y cancelados y confirmar. Lo no preparado se cancela; no queda en espera.
4. **Abrir remito para imprimir**. El mismo documento queda para la cola de Email; consultar su estado, no confirmar de nuevo para enviarlo.
5. **Mercadería necesaria > Excel para Urban Point** resume productos sin datos de vendedores. Para preparar reparto se conserva el Excel privado de depósito.
En Campañas, los accesos se preparan para todos los Email habilitados por vendedor; se puede elegir uno. Revisar siempre la audiencia. Esta actualización no manda la campaña existente.

## MiDistri-Pedidos v5 — presentación opcional del catálogo

La sincronización admite Display0 de Urban como presentación no informada.
Se conservan fotos, precios, PVP y permisos. Sin nuevas migraciones ni cambios
en Urban. Después de instalar v5, actualizar la copia del catálogo desde el panel.
Instalación productiva pendiente. Ver [guía v5](DISPLAY_CERO_v5.md).

## MiDistri-Pedidos v4 - Panel de Distribuidor
Instalación pendiente; requiere Urban Soft v583. Entrada desde Urban Soft con
permisos y alcance actuales, sin cuenta staff adicional. Productos y pedidos,
publicación completa con previa y presentación propia por tienda. Precio vendedor
y PVP desde Urban. Migración aditiva0003. Habilitación administrativa explícita;
no publica catálogo ni envía Email al instalar.
Ver [guía vigente](PANEL_DISTRIBUIDOR_v4.md) y [validación](VALIDACION_v4.md).

## MiDistri Pedidos Online v3 - corrección de formularios MiDistri
Corrige el403 CSRF provocado por Referrer-Policy:no-referrer en formularios.
Se usa same-origin: conserva la referencia interna, sin enviarla a otros sitios.
CSRF, autenticación, alcance y permisos se conservan. No hay migraciones,
cambios de importes, datos históricos, claves, venv, cron ni habilitación de envíos.
Instalación productiva pendiente. Requiere MiDistri v2 instalada.
Ver [detalle](CSRF_PORTAL_v3.md) y [validación](VALIDACION_v3.md).

# MiDistri: guía de operación
## Urban Point
1. En Urban Soft, Urban Point > MiDistri · Catálogo, crear una conexión y elegir distribuidoras.
2. Guardar la clave mostrada una sola vez en el cPanel de MiDistri, no en mensajes ni planillas.
3. Buscar productos, elegir proveedor y distribuidora, marcar y publicar. Elegir20/65 incluye ambos
   dentro del alcance permitido. Retirar una publicación no elimina productos ni pedidos anteriores.
4. Pedidos y datos personales sólo aparecen en el ámbito privado autorizado, con excepción de SuperUsuario.

## Distribuidora
1. Comunicaciones > MiDistri · Pedidos online. Buscar y elegir vendedor.
2. Elegir conexión. Crear enlace para copiar/WhatsApp, o seleccionar un contacto Email habilitado,
   escribir el Email exacto y enviar. Enlace personal válido48h; no publicarlo.
3. Pedido recibido: revisar detalle. Marcar OK permite incluirlo en Excel para depósito con LIN/VV.
   Estos pasos no cobran al vendedor. Si falta stock, cancelar antes de confirmar preparación.
4. Cuando esté preparado, un usuario con autorización financiera pulsa
   Confirmar preparación, generar cargo y remito. No hace falta repetir ante doble clic.
5. Abrir el remito emitido; es copia del documento nativo. Reenvíos de Email no debitan otra vez.
6. Revisar avisos: pendiente puede procesarse; aceptado significa aceptación SMTP, no lectura.
   Por conciliar/enviando exige revisar proveedor. Si un proceso fue interrumpido, esperar15min.
   Conciliar con motivo permite registrar aceptación o dejar pendiente sólo si consta que no se envió.
   La conciliación no envía Email ni altera la cuenta.

## Vendedor
Abrir enlace y tocar Entrar. El portal muestra su distribuidora, LIN/VV, productos activos,
precio vendedor y PVP. Elegir cantidades, revisar precios y enviar. No se paga en el portal.
Consultar Mis pedidos, estados y remito al estar preparado. Ante fallo de conexión, reintentar
el pedido guardado; no volver a armarlo para evitar solicitudes distintas.
Si cambió precio o se retiró un producto, revisar nuevamente antes de confirmar.
No se necesita cuenta administrativa ni registro público. El acceso puede revocarlo su distribuidora.
