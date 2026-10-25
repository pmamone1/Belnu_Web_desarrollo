## MiDistri-Pedidos v19

Encabezado y botones editables, nueve logos/favicon de comercio y transporte, progreso de publicación, búsqueda flexible/conteo/orden, ranking Urban y marcas de entrega/últimas unidades. Acumulativo16/17/18; portal0010 aditiva. Requiere Urban602 primero; producción pendiente. Sin campaña.

Guía vigente: [Identidad y catálogo](CATALOGO_IDENTIDAD_v19.md).

Validar tienda antigua y moderna; logo/favicondistintos sin duplicación; textosescapadosyURLsintactas; publicar lento/doble clic/error/reintento; búsqueda termos/termo yacentos; contador y ordenprecio+PVP/paginación; ranking sólo propio; entrega24/48-96; últimasunidades1y9frente0y10; snapshot inválido conserva copia; mails sin envío real durante pruebas.

## MiDistri-Pedidos v18

Flechas laterales, navegación de bloques y cabezal/página completa, accesos a banners laterales y elección aleatoria del catálogo en borrador. Precio por unidad y pedidos en múltiplos del display; historial de anulación. Guía: [EDITOR_PEDIDOS_v18.md](EDITOR_PEDIDOS_v18.md). Requiere Urban601; paquete acumulativo16/17. Producción pendiente; sin campaña.

## MiDistri-Pedidos v17 · Fotos completas en banners

Las fotos de productos del catálogo se ajustan completas y centradas dentro del banner, sin deformar ni recortar, incluso si la página conserva el modo «rellenar». La altura elegida se conserva; puede quedar espacio libre a los lados. El material promocional propio conserva su ajuste configurado.

Guía: [BANNERS_v17.md](BANNERS_v17.md). Actualización exclusiva del portal sobre v16, compatible con Urban600; sin migraciones ni cambios de datos. Instalación productiva pendiente; sin campaña.

## MiDistri-Pedidos v16

Editor visual de bloques, alturas y capas con borrador AJAX; encabezado de tienda configurable y saludo con nombre/LIN/VV. Catálogo exige activo, foto pública y precio vendedor/PVP positivos. Bandeja Urban permite reducir/quitar productos con motivo y aviso; faltantes Excel y mensaje interno explícito. MiDistri-Puntos permanece sólo en análisis.

Guía vigente: [EDITOR_VISUAL_v16.md](EDITOR_VISUAL_v16.md). Paquetes coordinados600/16, bases599/15. Instalación productiva pendiente.

Casos críticos: guardado AJAX sin navegar; perder respuesta y reintentar; no editar durante subida/revisión; copy sin precios congelados; publicar sólo revisión confirmada; cruce de tenant rechazado; productos sinfoto/PVP0 ocultos; reducir/cancelar/reintentar pedido sin duplicar; avisar después del commit; faltantes sin doble cómputo; Excel interno sin vendedores/precios; encabezado editable y LIN/VV conservados.

## MiDistri-Pedidos v15 — Acceso y código

Pegar o completar los seis números verifica el código automáticamente una sola vez. Hay botón Pegar código y alternativa Entrar. Se conserva la elección entre perfiles.

Guía vigente: [CODIGO_AGIL_v15.md](CODIGO_AGIL_v15.md). Requiere Urban599 + MiDistri15 sobre bases598/14, sin migraciones nuevas. Instalación productiva pendiente.

Pruebas críticas: confirmación HTTPS mismo origen con CSRF válido; rechazar origen null/ajeno/token ausente y replay; Email HTML y texto con casilla propia; pegado, autocompletado, doble clic, código incorrecto, reenvío, clipboard denegado y selector de perfiles. Usar datos sintéticos locales.

## MiDistri-Pedidos v14 · Ingreso por Email

Email y código30min, selección de perfil sólo después de verificar. Remitentes propios por tienda; administración autenticada en Urban Soft con alcance puntual. Conserva el contrato anterior y configuraciones existentes.

Guía vigente: [ACCESO_EMAIL_v14.md](ACCESO_EMAIL_v14.md). Prevalece para este flujo. Requiere Urban598 + MiDistri14; instalar en ese orden. Producción pendiente; sin campañas.

En datos sintéticos: Email desconocido; un perfil; varios kioscos; tiendas con remitentes distintos; uno apagado; cuenta administrativa equivocada; código vencido/reutilizado y contacto revocado. No conceder administración al contacto vendedor. Conservar la configuración WhatsApp.

## MiDistri-Pedidos v13

Acceso único de Distribuidor, menú MiDistri y guía por tienda con remitentes propios; excepción20/65. Pedidos separados y código30min ligado a tienda. Instalación productiva pendiente; campaña sin enviar.

Guía vigente: [GUIA_v13.md](GUIA_v13.md). Esta sección tiene prioridad para los flujos afectados. Mantener permisos y no usar remitentes ajenos.

## MiDistri-Pedidos v12

Banners de ancho completo, fotos más grandes y fundido accesible. Conserva cuatro diseños/temas, la página anterior y la sesión por pestaña. Sin cambios de catálogo, precios ni permisos; producción pendiente.

Guía vigente: [BANNERS_v12.md](BANNERS_v12.md). Validación: [evidencia](VALIDACION_v12.md).

1. Cuatro diseños y temas, PC/celular: banner al ancho completo sin scroll horizontal.
2. Una foto sin flechas; varias con pausa, teclado y fundido; movimiento reducido sin animación.
3. Volver desde el carrito/pedidos: un solo temporizador y controles funcionando.

## MiDistri v11 — Tienda con borrador y referencias

Cuatro diseños, mensajes y banners de productos con previa PC/celular y publicación completa. Referencia breve de Urban, conservando UUID y originales. Migración0009 preserva página vigente. Requiere Urban591; instalación productiva pendiente; sin campaña ni cambios SMTP.

Guía: [TIENDA_REFERENCIAS_v11.md](TIENDA_REFERENCIAS_v11.md). Evidencia: [VALIDACION_v11.md](VALIDACION_v11.md).

- Verificar referencia común, parciales, permisos por tienda, borrador privado, cuatro diseños, previa/confirmación y recuperación pendiente.
- Probar producto retirado, revisión obsoleta, una foto, teclado, pausa y movimiento reducido; comparar página anterior tras migrar.
- Pendiente: aceptación en HTTPS real después de instalar; no enviar campaña ni crear cargos de prueba en producción.

## MiDistri-Pedidos v10 - Catálogo coordinado

Operación cada cinco minutos con Urban v588: altas autorizadas, cambios y bajas, conservando exclusiones, ocultos y pedidos anteriores. Mantiene sincronizador/API y galería v9; acumulativo v8/v9, sin migraciones nuevas. Instalación v10 y cron productivos pendientes. El video Alma Chocolate141 ya fue publicado/sincronizado para20/65 según confirmación del usuario y lectura del portal23/10/2026. SMTP y campaña sin cambios.

Guía vigente: [CATALOGO_AUTOMATICO_v10.md](CATALOGO_AUTOMATICO_v10.md). Prioridad sobre instrucciones antiguas para este flujo.

En QA: alta, cambio, baja, oculto, exclusiones y distribuidora futura; repetir y simular fallos independientes. Verificar histórico anterior intacto, registro privado y ausencia de comunicaciones.

## MiDistri-Pedidos v9 - Galería sin controles redundantes

Con un recurso se ocultan flechas y miniaturas; con varios se conserva la navegación de fotos y videos. Sin migraciones nuevas, cambios de permisos, precios o pedidos. Instalación productiva pendiente. El diagnóstico confirmó que el video2 de Alma Chocolate no está publicado para19/68 (20/65); requiere publicación expresa y sincronización, no se resuelve sólo instalando esta versión.

Guía vigente: [GALERIA_v9.md](GALERIA_v9.md). Para el resto del portal se mantiene v8.

En QA: ampliar una foto única y comprobar ausencia de Anterior/Siguiente y miniaturas; ampliar dos fotos y comprobar ambas direcciones; con dos fotos más video comprobar selección del tercero. Cerrar/Escape devuelve foco. No publicar originales privados para probar. Caso Alma: comprobar selección publicada por distribuidora y sincronizar antes de atribuirlo al reproductor.

## MiDistri-Pedidos v8 - Fotos, textos y cuatro temas

Vigente sobre v7 r2 confirmada por el usuario; instalación v8 pendiente. Apariencia: Claro, Nocturno, Azul y Verde. Catálogo para el Kiosco, texto de disponibilidad simplificado, fotos en carrito y detalle, y botón «Armar un nuevo pedido». Fotos actuales de la misma distribuidora; cantidades y precios históricos intactos. Sin modelos, migraciones nuevas, cargos ni campañas. No requiere actualización Urban Soft.

Guía vigente: [FOTOS_PRESENTACION_v8.md](FOTOS_PRESENTACION_v8.md). Este capítulo prevalece sobre los temas y textos de versiones anteriores.

En datos sintéticos: comprobar las cuatro opciones en catálogo/Mi tienda; probar tema retirado con tienda Azul y confirmar Claro; alternar Nocturno/Verde. Carrito y detalle deben mostrar fotos ampliables sin deformar, nombres/precios/total correctos; producto sin foto no toma otra distribuidora. Pedido histórico conserva precio aunque cambie Publicacion; vendedor ajeno devuelve 404. Verificar textos en catálogo, carrito y recibido. No enviar pedidos/campañas reales para probar.

## MiDistri-Pedidos v7 r2 · Recuperación de instalación

Corrige el error de configuración que detuvo el v7 en Django check. Usar el ZIP r2 completo para retomar el intento; no editar hashes ni settings a mano. Conserva el circuito aprobado. Instalación r2 productiva pendiente; el intento comunicado no llegó a migrar. Ver [recuperación y compatibilidad](RECUPERACION_MIDISTRI_v7_r2.md).

## MiDistri-Pedidos v7 - Acceso con código, galerías y tienda

Vigente revisión final: promociones con revisión privada y confirmación separada; recuperación durable de respuestas perdidas; retiro por fuente vigente; campañas20/65 conservan sus datos propios. Salir reintenta el cierre sin restaurar identidad. Ver guía de esta versión.


Implementación local integrada; instalación productiva pendiente. Código de30min, sesión por pestaña, recuperación del acceso Distribuidor, campañas configurables, avisos con historial, galerías y siete temas/promociones. Conserva precios, preparación parcial, contactos y permisos. Instalar MiDistri7 primero y Urban585 después con funciones nuevas apagadas; activar coordinadamente. La campaña no se envía.

En QA: código1799válido/1800vencido,5errores, dos identidades, sesión31min, pestaña nueva sin identidad, recarga/Salir; callback simultáneo y Origen falso; foto principal/miniaturas/Escape, recurso retirado/Range; promoción fuera de alcance/revisión vieja/diezmáximo. En producción pendientes: SMTP real, entrada administrativa desde navegador del usuario y subida16MiB a través de cPanel. No probar con pedidos reales ni enviar la campaña para verificar instalación.

Documentación vigente: [ACCESO_TIENDA_v7.md](ACCESO_TIENDA_v7.md). Instrucciones anteriores que siguen son antecedentes y no prevalecen sobre este capítulo.

## Pruebas v6

En datos sintéticos: pedir10 a$25.000 y2 de otro producto; preparar6 del primero y0 del segundo. Esperado: cargo$150.000, canceladas4+2, un PDF sin el segundo, original intacto. Repetir confirmación: sin duplicados. Cero todo: sin cargo/PDF. Alterar cantidades/revisión ajena/caducada: rechazar. Dos contactos activan a la vez sin revocarse; baja de uno lo excluye. Excel: pendientes0 para esa preparación, sin LIN/VV/contactos. Sin autorización65, ni pedidos ni exportación65. Revisar catálogo público y filtros sin acceso a pedidos personales.

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

# Pruebas manuales MiDistri
Comprobar móvil: enlace GET no consume, POST entra y muestra sólo catálogo de su distribuidora/LIN/VV.
Anónimo sólo ve PVP. Cambiar precio antes de envío exige revisar; conexión fallida conserva UUID.
Reintentar mismo pedido no duplica cargo; otro vendedor no ve pedido/remito. HTML de error no se descarga como PDF.
Comprobar cancelación stock y preparación con remito nativo. Flags/Email apagados no envían.


### Contrato v2 y recuperación
SKU80 debe sincronizar y regresar en el pedido recibido sin quedar pendiente. SKU81 se rechaza.
Verificar recuperación de copia parcial y rechazo de respaldo alterado.
Homologación real Python3.7 y motor del servidor pendiente; no se habilitan flags ni envíos al instalar.

### Control posterior de formularios CSRF
1. Obtener un formulario nuevo por GET después de instalar; no reenviar la página403.
2. Guardar con el navegador: catálogo/conexión en Urban y entrada/carrito en Portal.
3. Verificar que misma procedencia+token válido pasa y que sin token u origen externo se rechaza.
4. Revisar que ambos sistemas siguen apagados hasta configurar conexión y autorizar el piloto.
No generar cargos ni enviar Email para comprobar esta corrección.


## Verificación manual de MiDistri operativo (v583 / portal v4)

- Entrar con un Distribuidor autorizado desde Pedidos > Administrar MiDistri-Pedidos.
  Verificar que no aparezcan tiendas ajenas. 20 incluye65 sólo si ambas están autorizadas.
- Quitar un permiso o desactivar al operador durante la sesión: la siguiente acción
  debe bloquearse. Urban Point ordinario no accede a datos privados.
- Publicar catálogo completo: revisar resumen por tienda, proveedor y exclusiones.
  Confirmar una vez; repetir confirmación no debe duplicar publicaciones.
  Ocultar un producto debe preservar pedidos anteriores. Precio cero/negativo se
  muestra para corregir en Urban y no se publica como precio válido.
- Guardar logo/contacto/mensajes y verificar tienda del vendedor. Una edición
  concurrente debe pedir recarga. Una caída del acuse no debe repetir el guardado.
- Pedido: revisar y Excel no generan cargo. Recibido > OK > revisión de preparación >
  confirmación genera un único pedido/cargo/remito. Cancelar sólo antes de emitir.
- Campaña de acceso: todos, líneas y uno; revisar Email, LIN, VV y excluidos.
  Sin confirmar no debe haber invitaciones. Dos vendedores con un mismo Email
  reciben enlaces diferentes; respetar bajas y remitentes por distribuidora.
- Desactivar envío, revocar conexión/contacto/permiso: no debe enviarse el acceso.
  Un SMTP incierto requiere conciliación, sin reenvío automático.
- Verificar con HTTPS real tras instalación: intercambio entre sitios, expiración,
  cookies Secure/HttpOnly, escritorio y móvil. Esto permanece pendiente en cPanel.
- Instalación: los paquetes rechazan destino/base/plan ajenos. --restore después de
  migrar debe detenerse antes de modificar código; usar corrección hacia adelante.

Validación v5: sincronizar un catálogo sintético con Display0, comprobar fotos y ambos precios, ausencia de presentación0, separación20/65 y conservación de copia previa ante texto/booleano/negativo. En cPanel revisar sincronización real después de instalar; no generar pedidos de prueba en producción.

Caso de regresión: abrir vendedor y administración en el mismo navegador; el carrito sigue vigente. Validar código a1799s y elegir después: ticket120s. Perder respuesta al publicar, recargar y reintentar la misma operación. Revisar material propio sin acceso público, confirmar, retirar producto/sincronizar y comprobar retiro de promoción. Cambiar sólo título en campaña20/65 y conservar nombre/Reply-To de cada una. Salir sin red y comprobar revocación al recuperar conexión.

Regresión r2: importar belnuweb/settings.py con valores ficticios; reconocer sólo la huella v7 defectuosa; comprobar sin escritura; retomar archivos v7 exactos; rechazar un cambio desconocido; luego aplicar, cargar configuración instalada real y completar migraciones/estáticos/arranque. No usar producción como banco de pruebas.
