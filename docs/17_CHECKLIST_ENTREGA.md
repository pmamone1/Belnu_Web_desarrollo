## MiDistri-Pedidos v33 vigente · Editor y pedidos

Editor con estilos independientes por mensaje, eliminación reversible de bloques y advertencias localizadas; Mis pedidos en tabla desplegable adaptable. Sin migraciones nuevas ni cambios económicos, históricos, remitentes, WhatsApp, cron o venv. Sin envíos.

Guía: [Edición y pedidos](EDITOR_PEDIDOS_v33.md).

Pruebas de aceptación: quitar Acceso Distribuidor sólo del encabezado público; abrir administración desde Urban. Crear/eliminar/deshacer/rehacer promoción; catálogo protegido. Guardar dos mensajes con estilos diferentes, restablecer uno y publicar sólo tras revisar. Cargar borrador con foto retirada, localizar aviso y reemplazar/ocultar/eliminar sin rehabilitar la foto. Pedidos recibidos/entregados parciales/cancelados: mostrar cantidades y totales del snapshot y nunca confundir pendiente con cero. Probar alcance de otro vendedor, fallo de actualización y pantallas320/390/1440. Instalación no envía campañas ni activa programación.

Verificación actual: [Evidencia32](VERIFICACION_v32.md). Confirmar sesión estable, subcategoría, modo automático y previa sin encolado.

## MiDistri32 vigente: variedad e incentivos

Guía: [Catálogo y preparación](ROTACION_INCENTIVOS_v32.md). catálogo Recomendados estable por sesión, subcategorías, banners automáticos y acceso Continuar; preparación privada de incentivos para Urban624, sin SMTP. Sin migraciones nuevas, activación de cron, cambios de remitentes, WhatsApp o venv. Sin envíos.


## MiDistri-Pedidos v31

Encabezado sin botón de salida; acceso recordado y Cambiar perfil conservados. Paginación grande, filtros conservados y diseño adaptable. Spinner accesible mientras se recupera el acceso. Sin nuevas migraciones ni cambios económicos, credenciales, asignaciones de remitentes, WhatsApp, cron o venv. Sin campañas ni correos de prueba reales.

Guía vigente: [Navegación y espera de acceso](NAVEGACION_v31.md).

Bases Urban622 y MiDistri30 confirmadas instaladas por el usuario. Esta entrega requiere instalación productiva; un commit o ZIP no instala el código. Este apartado prevalece sobre instrucciones históricas incompatibles.

- [ ] Verificar ambas huellas y ejecutar los dos preflight antes de aplicar.
- [ ] Instalar Urban623 y portal31, conservando variables actuales. No requiere activar banderas, sincronizar catálogo ni modificar cron.
- [ ] Comprobar código por remitente compartido, marca pública y paginación/espera. No reenviar campañas.

## MiDistri-Pedidos v30

Acceso de vendedor recordado automáticamente tras el primer código, sin vencimiento propio. Olvido revocable por dispositivo, perfiles acreditados y carritos por pestaña. Sólo portal0014 aditiva; requiere Urban622. Conserva captura e intervalos de analítica. Sin campañas, cambios económicos, históricos, remitentes, WhatsApp, cron o venv.

Guía vigente: [Acceso recordado](ACCESO_RECORDADO_v30.md).

- [ ] En el sitio instalado: primer código, reabrir navegador sin código, perfiles múltiples y carritos separados.
- [ ] Probar baja de contacto, cierre en otra pestaña y olvido sin conexión; ninguna sesión administrativa debe restaurarse como vendedor.
- [ ] Confirmar bases, migración aditiva, estados y dos banderas; conservar analítica activa y canales. No enviar campaña.

## MiDistri-Pedidos v29

Corrige la unicidad de intervalos en MariaDB mediante índice ordinario y coherencia de estado. Sólo nueva 0013; conserva 0012, fechas, eventos y captura activa. Urban 621 se mantiene. No cambia SQLMode, credenciales, remitentes, WhatsApp, cron, catálogo o venv. Sin envíos.

Guía vigente: [Intervalos MariaDB](INTERVALOS_MARIADB_v29.md).

- [ ] Confirmar base 28/0012 y preflight sin cambios; comprobar índice único real y ausencia de W036.
- [ ] Conservar contador/captura y fechas antes/después; duplicados deben detener antes de DDL, sin fusiones.

Validación adicional v28: comprobar filtros HTTP repetidos y selección actual; foto tardía excluida; consulta previa a activación y durante pausa sin falsos ceros; sesión reutilizada y consulta/Excel congelados; contactos inválidos y páginas densas por bytes; encabezado ajeno rechazado salvo bloque20/65.

## MiDistri-Pedidos v28

Analítica privada de vendedores: resumen, grupos sin ingreso/pedidos, ficha, acciones y Excel; precios argentinos inseparables y búsqueda por similitud. Portal0012 aditiva, captura apagada hasta activación coordinada con Urban621. Sin campañas, cambios económicos, remitentes, WhatsApp, cron o venv.

Guía vigente: [Analítica de vendedores](ANALITICA_v28.md).

- [ ] Instalar Urban621 y portal28; confirmar0012 y contrato sin enviar mensajes.
- [ ] Activar medición; probar vendedor, fotos, carrito/pedido y consulta con permisos propios; probar aislamiento, grupos, Excel y móvil. No usar producción como base de prueba.
- [ ] Confirmar precios con miles y $ inseparable, búsqueda coni/koni y ausencia de productos inactivos.

## MiDistri-Pedidos v27

SKU pequeño debajo del nombre, también en destacados; códigos largos ajustados a la tarjeta, controles alineados conservados. Guía: [SKU e ingreso por Email](CATALOGO_SKU_v27.md). Se verificó el ingreso automático existente de vendedores activos de tiendas conectadas; no se activaron otras tiendas ni se modificó autenticación. Acumulativo23/24/25/26, sin migraciones, precios, envíos o cambios de canales/cron. Instalación productiva pendiente.

- [x] Cinco regresiones SKU observadas RED→GREEN; suite202 ejecutadas,201 aprobadas y1omisión heredada.
- [x] Ingreso existente Urban:33 pruebas aprobadas conSMTP simulado, sin envíos reales.
- [x] Instalador/paquete:25pruebas correctas sobre23/24/25/26; faltantes/alteraciones rechazados.
- [x] Cuatro diseños en1440/390px,56SKU visibles,48controles alineados y sin desbordes.
- [x] Manual29páginas, capítulo y unión revisados visualmente;28páginas anteriores conservadas.
- [x] Instrucciones completasv27 en inventario; cambio ajeno forgotPassword excluido.
- [ ] Cotejo ZIP definitivo contra commit y copiaDownloads: se acredita al entregar.
- [ ] Publicación commit/PR: se acredita al entregar.
- [ ] Instalación y comprobaciónHTTPS en producción: pendiente.
- [ ] Activar distribuidoras aún no configuradas: requiere la aclaración pendiente; no se ejecuta con este ZIP.

## MiDistri-Pedidos v26

- [x] Regresión y revisión final.
- [x] QA visual escritorio/móvil y manual PDF/unión.
- [ ] ZIP cotejado contra commit publicado.
- [ ] Instalación y aceptación HTTPS. Sin campaña.

## MiDistri-Pedidos v25

- [x] Regresión y revisión final.
- [x] PDF y unión revisados.
- [ ] ZIP cotejado con commit publicado.
- [ ] Instalación y aceptación HTTPS. Sin campaña.

## MiDistri-Pedidos v24

- [x] Regresión y revisión final.
- [x] Manual PDF y unión revisados.
- [ ] ZIP cotejado contra commit publicado.
- [ ] Instalación y aceptación HTTPS. Sin campaña.

## MiDistri-Pedidos v23

- [x] Regresión y revisión independiente final.
- [x] Manual principal y unión revisados.
- [ ] ZIP cotejado con commit publicado.
- [ ] Instalación cPanel y aceptación HTTPS. Sin campaña.

## MiDistri-Pedidos v22

- [x] Pruebas y revisión independiente final.
- [x] Manual PDF y unión verificados.
- [ ] Paquete cotejado con commit publicado.
- [ ] Instalación cPanel y aceptación. Sin campaña.

## MiDistri-Pedidos v21

- [x] Contrato anterior/nuevo, aislamiento, búsqueda y suite completa.
- [x] Manual PDF y unión comprobados.
- [ ] ZIP cotejado con commit publicado.
- [ ] Instalación y aceptación HTTPS. Sin campaña.

## MiDistri-Pedidos v20

- [x] Pruebas, revisión y QA visual local cerrados.
- [x] Manual PDF y unión revisados.
- [ ] ZIP cotejado contra commit publicado.
- [ ] Instalación cPanel y aceptación HTTPS, sin campaña.

## MiDistri-Pedidos v19

Encabezado y botones editables, nueve logos/favicon de comercio y transporte, progreso de publicación, búsqueda flexible/conteo/orden, ranking Urban y marcas de entrega/últimas unidades. Acumulativo16/17/18; portal0010 aditiva. Requiere Urban602 primero; producción pendiente. Sin campaña.

Guía vigente: [Identidad y catálogo](CATALOGO_IDENTIDAD_v19.md).

- [x] Pruebas locales, revisión final, manualPDF e inventario completo verificados.
- [ ] Cotejo final de ZIP contra commit publicado al entregar.
- [ ] Instalar Urban602 primero; portal19 y sincronización coordinada.
- [ ] VerificarHTTPS sin campaña.

## MiDistri-Pedidos v18

Flechas laterales, navegación de bloques y cabezal/página completa, accesos a banners laterales y elección aleatoria del catálogo en borrador. Precio por unidad y pedidos en múltiplos del display; historial de anulación. Guía: [EDITOR_PEDIDOS_v18.md](EDITOR_PEDIDOS_v18.md). Requiere Urban601; paquete acumulativo16/17. Producción pendiente; sin campaña.

- [x] Pruebas locales dirigidas, concurrencia y revisión independiente cerradas.
- [x] Manual/PDF actualizado y unión con páginas previas revisada.
- [x] Instalador y recuperación probados contra base admitida.
- [ ] Cotejar SHA256 en cPanel e instalar en orden Urban601, portal18.
- [ ] AceptaciónHTTPS y correo real sólo con destinatarios/operaciones autorizados.
- [ ] No enviar campaña ni activar MiDistri-Puntos.

## MiDistri-Pedidos v17 · Fotos completas en banners

Las fotos de productos del catálogo se ajustan completas y centradas dentro del banner, sin deformar ni recortar, incluso si la página conserva el modo «rellenar». La altura elegida se conserva; puede quedar espacio libre a los lados. El material promocional propio conserva su ajuste configurado.

Guía: [BANNERS_v17.md](BANNERS_v17.md). Actualización exclusiva del portal sobre v16, compatible con Urban600; sin migraciones ni cambios de datos. Instalación productiva pendiente; sin campaña.

- [x] Diagnóstico y reproducción visual; foto completa en PC/celular local.
- [x] Suite del portal e instalador aprobados; revisión independiente sin hallazgos importantes.
- [x] Manual actualizado y páginas previas conservadas.
- [ ] Cotejar SHA256 en cPanel e instalar v17 sobre v16.
- [ ] Comprobar en HTTPS tras instalar; no enviar campaña.

## MiDistri-Pedidos v16

Editor visual de bloques, alturas y capas con borrador AJAX; encabezado de tienda configurable y saludo con nombre/LIN/VV. Catálogo exige activo, foto pública y precio vendedor/PVP positivos. Bandeja Urban permite reducir/quitar productos con motivo y aviso; faltantes Excel y mensaje interno explícito. MiDistri-Puntos permanece sólo en análisis.

Guía vigente: [EDITOR_VISUAL_v16.md](EDITOR_VISUAL_v16.md). Paquetes coordinados600/16, bases599/15. Instalación productiva pendiente.

- [ ] Verificar SHA256 de ZIP definitivo antes de instalar.
- [ ] Instalar Urban600 sobre599 y MiDistri16 sobre15. Aceptación productiva pendiente.
- [ ] Verificar SMTP/WhatsApp conservados; no enviar campaña ni activar Puntos.

- [x] Pruebas locales y limitaciones registradas en VALIDACION de esta versión.
- [x] Revisión independiente sin defectos importantes abiertos.
- [x] Manual PDF actualizado y unión con contenido previo revisada visualmente.
- [x] Inventario explícito e instalador probados sobre la base admitida.

## MiDistri-Pedidos v15 — Acceso y código

Pegar o completar los seis números verifica el código automáticamente una sola vez. Hay botón Pegar código y alternativa Entrar. Se conserva la elección entre perfiles.

Guía vigente: [CODIGO_AGIL_v15.md](CODIGO_AGIL_v15.md). Requiere Urban599 + MiDistri15 sobre bases598/14, sin migraciones nuevas. Instalación productiva pendiente.

- [ ] Cotejar SHA256 del ZIP subido en cPanel antes de instalar.
- [ ] Instalar Urban599 sobre598 y MiDistri15 sobre14. Aceptación HTTPS productiva pendiente.
- [ ] Conservar remitentes y WhatsApp; no enviar la campaña.

## MiDistri-Pedidos v14 · Ingreso por Email

Email y código30min, selección de perfil sólo después de verificar. Remitentes propios por tienda; administración autenticada en Urban Soft con alcance puntual. Conserva el contrato anterior y configuraciones existentes.

Guía vigente: [ACCESO_EMAIL_v14.md](ACCESO_EMAIL_v14.md). Prevalece para este flujo. Requiere Urban598 + MiDistri14; instalar en ese orden. Producción pendiente; sin campañas.

- [x] Pruebas dirigidas, revisión independiente y PDF verificados localmente.
- [ ] En cPanel, cotejar el SHA256 del ZIP subido con el informado en la entrega antes de instalar.
- [x] Suite histórica general comparada contra597: mismas732incidencias, documentadas sin afirmar aprobación global.
- [ ] Confirmar instalación y aceptación real del ingreso sin enviar campañas.

## MiDistri-Pedidos v13

Acceso único de Distribuidor, menú MiDistri y guía por tienda con remitentes propios; excepción20/65. Pedidos separados y código30min ligado a tienda. Instalación productiva pendiente; campaña sin enviar.

Guía vigente: [GUIA_v13.md](GUIA_v13.md). Esta sección tiene prioridad para los flujos afectados. Mantener permisos y no usar remitentes ajenos.

## MiDistri-Pedidos v12

Banners de ancho completo, fotos más grandes y fundido accesible. Conserva cuatro diseños/temas, la página anterior y la sesión por pestaña. Sin cambios de catálogo, precios ni permisos; producción pendiente.

Guía vigente: [BANNERS_v12.md](BANNERS_v12.md). Validación: [evidencia](VALIDACION_v12.md).

- [x] Verificar paquete, hashes, instalador y manual PDF.
- [ ] Instalar en su aplicación y comprobar impresión/vista previa sin operaciones económicas.
- [ ] Mantener campaña sin enviar; no contar instalación sin recibo.

## MiDistri v11 — Tienda con borrador y referencias

Cuatro diseños, mensajes y banners de productos con previa PC/celular y publicación completa. Referencia breve de Urban, conservando UUID y originales. Migración0009 preserva página vigente. Requiere Urban591; instalación productiva pendiente; sin campaña ni cambios SMTP.

Guía: [TIENDA_REFERENCIAS_v11.md](TIENDA_REFERENCIAS_v11.md). Evidencia: [VALIDACION_v11.md](VALIDACION_v11.md).

- Verificar referencia común, parciales, permisos por tienda, borrador privado, cuatro diseños, previa/confirmación y recuperación pendiente.
- Probar producto retirado, revisión obsoleta, una foto, teclado, pausa y movimiento reducido; comparar página anterior tras migrar.
- Pendiente: aceptación en HTTPS real después de instalar; no enviar campaña ni crear cargos de prueba en producción.

## MiDistri-Pedidos v10 - Catálogo coordinado

Operación cada cinco minutos con Urban v588: altas autorizadas, cambios y bajas, conservando exclusiones, ocultos y pedidos anteriores. Mantiene sincronizador/API y galería v9; acumulativo v8/v9, sin migraciones nuevas. Instalación v10 y cron productivos pendientes. El video Alma Chocolate141 ya fue publicado/sincronizado para20/65 según confirmación del usuario y lectura del portal23/10/2026. SMTP y campaña sin cambios.

Guía vigente: [CATALOGO_AUTOMATICO_v10.md](CATALOGO_AUTOMATICO_v10.md). Prioridad sobre instrucciones antiguas para este flujo.

- [x] Diseño aprobado, código/contratos y documentación revisados localmente.
- [ ] Confirmar instalación, regla y cron productivos sin duplicar tareas.

## MiDistri-Pedidos v9 - Galería sin controles redundantes

Con un recurso se ocultan flechas y miniaturas; con varios se conserva la navegación de fotos y videos. Sin migraciones nuevas, cambios de permisos, precios o pedidos. Instalación productiva pendiente. El diagnóstico confirmó que el video2 de Alma Chocolate no está publicado para19/68 (20/65); requiere publicación expresa y sincronización, no se resuelve sólo instalando esta versión.

Guía vigente: [GALERIA_v9.md](GALERIA_v9.md). Para el resto del portal se mantiene v8.

- [x] Revisión independiente y navegación verificadas en navegador con datos sintéticos.
- [x] 114 pruebas del proyecto y 17 del instalador; PDF y revisión visual verificados. Ver entrega para ZIP/hash/commit finales.
- [ ] Confirmación de instalación productiva y publicación/sincronización del video informado.

## MiDistri-Pedidos v8 - Fotos, textos y cuatro temas

Vigente sobre v7 r2 confirmada por el usuario; instalación v8 pendiente. Apariencia: Claro, Nocturno, Azul y Verde. Catálogo para el Kiosco, texto de disponibilidad simplificado, fotos en carrito y detalle, y botón «Armar un nuevo pedido». Fotos actuales de la misma distribuidora; cantidades y precios históricos intactos. Sin modelos, migraciones nuevas, cargos ni campañas. No requiere actualización Urban Soft.

Guía vigente: [FOTOS_PRESENTACION_v8.md](FOTOS_PRESENTACION_v8.md). Este capítulo prevalece sobre los temas y textos de versiones anteriores.

- [x] Suite del proyecto: 114 pruebas; instalador: 17 pruebas; cinco escenarios JS de preferencias.
- [x] Revisión visual y PDF verificados; inventario cerrado. Ver entrega para hash ZIP y commit publicados.
- [ ] Usuario confirma instalación de belnuweb y verifica catálogo, carrito y detalle.

## MiDistri-Pedidos v7 r2 · Recuperación de instalación

Corrige el error de configuración que detuvo el v7 en Django check. Usar el ZIP r2 completo para retomar el intento; no editar hashes ni settings a mano. Conserva el circuito aprobado. Instalación r2 productiva pendiente; el intento comunicado no llegó a migrar. Ver [recuperación y compatibilidad](RECUPERACION_MIDISTRI_v7_r2.md).

## MiDistri-Pedidos v7 - Acceso con código, galerías y tienda

Vigente revisión final: promociones con revisión privada y confirmación separada; recuperación durable de respuestas perdidas; retiro por fuente vigente; campañas20/65 conservan sus datos propios. Salir reintenta el cierre sin restaurar identidad. Ver guía de esta versión.


Implementación local integrada; instalación productiva pendiente. Código de30min, sesión por pestaña, recuperación del acceso Distribuidor, campañas configurables, avisos con historial, galerías y siete temas/promociones. Conserva precios, preparación parcial, contactos y permisos. Instalar MiDistri7 primero y Urban585 después con funciones nuevas apagadas; activar coordinadamente. La campaña no se envía.

- [x] Pruebas locales de acceso, sesión, medios, permisos, precios y preparaciones.
- [x] Instaladores16/16 por proyecto.
- [ ] Revisión independiente final y resolución de hallazgos.
- [ ] Verificar PDF principal y ZIP/commit final.
- [ ] Instalación y activación funcional en cPanel por el usuario.

Documentación vigente: [ACCESO_TIENDA_v7.md](ACCESO_TIENDA_v7.md). Instrucciones anteriores que siguen son antecedentes y no prevalecen sobre este capítulo.

## Checklist v6

- [ ] Usuario confirma instalación P6 y luego U584 en sus runtimes y raíces separados.
- [ ] Confirmar check/reinicio y ausencia de migraciones nuevas de MiDistri; no inferir instalación de VERSION.
- [ ] Validar catálogo público con precio vendedor/PVP y filtro; permisos de20/65.
- [ ] Validar preparación parcial, cero, reintento, PDF y resumen sin identidad en entorno de pruebas.
- [ ] Controlar remitente/bajas por contacto sin enviar campaña existente.
- [ ] ZIP/commit, manualPDF y validación incluidos; ningún secreto, base, media o venv.
- [ ] Registrar instalación y contador de respaldos sólo después del recibo productivo.

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

# Checklist MiDistri v2
- [ ] Tests portal/instalador, sintaxis3.7 y paquete verificados.
- [ ] Comunicación HTTP sintética revisada.
- [ ] ZIP sin credenciales/DB/media/venv y commit publicado.
- [ ] Instalación productiva y piloto: pendientes de ejecución autorizada.

QA22/10: pruebas focalizadas y recuperación de instalador verificadas; ver documento de validación. Publicación del código no confirma instalación. Flags, cron, SMTP y validación en motores/runtime productivos siguen pendientes.

Corrección de referencia: RED reproducido, GREEN focalizado e instalador9/9. Manual PDF y unión revisados. Instalación productiva y piloto pendientes; no declarar publicaciones ni claves creadas.


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
