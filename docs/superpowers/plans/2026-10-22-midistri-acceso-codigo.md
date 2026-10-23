# MiDistri: código y sesión por pestaña — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Implementa el agente principal en este chat; revisión final según plan principal.

**Goal:** Permitir ingreso con Email/código de 30 minutos y sesión por pestaña, corrigiendo primero la recuperación del acceso administrativo.

**Architecture:** Urban valida identidad, códigos, cupos y acceso vigente. MiDistri gestiona pantallas públicas y un puente autenticado por prueba de pestaña más cookie; nunca entrega su clave de conexión ni el token Urban al navegador.

**Tech Stack:** Python3.10/Django5.2/PostgreSQL U; Python3.7/Django3.2/MariaDB P; sessionStorage, fetch y CSRF.

**Spec:** `docs/superpowers/specs/2026-10-22-midistri-acceso-codigo-y-tienda-design.md`, apartados A–C,G–H.

## Global Constraints

- Código válido exactamente 1800 segundos desde su emisión; un uso, cinco errores, reenvío mínimo 60 segundos.
- Tres solicitudes por Email/conexión en 15 minutos; veinte por IP en 15 minutos; hashes con clave, contadores persistentes.
- Cookie sola no autoriza datos de vendedor. No cortar sesión por los 30 minutos del código ni por timeout heredado de una hora.
- Salir revoca inmediatamente; cierre/restauración de pestaña no permite garantía de detección infalible. No usar pagehide como logout.
- Permisos actuales, contactos activos, secretos sólo en servidor, no SMTP real en tests ni campaña enviada.

## Review Focus

1. El mismo error administrativo tiene causas distintas: no etiquetar una hipótesis como causa confirmada (tarea 0).
2. Un Email puede corresponder a varias identidades; contacto puede cambiar entre verificación y selección (tareas 1–2).
3. DOS por reenvío, comparación de respuesta/timing y carreras al consumir código (tareas 1–2).
4. Cookie heredada, pestaña duplicada, renovación y logout no deben compartir o resucitar identidad (tareas 3–4).
5. Red caída al salir, restauración y suspensión móvil: explicar estado y no perder un pedido ya recibido (tarea 4).

---

## Mapa de archivos

U nuevos: `midistri_bridge/acceso_codigo.py` (identidad/OTP), `acceso_codigo_email.py` (outbox), `acceso_codigo_api.py` (contrato), `acceso_codigo_models.py` (desafío/cupo/entrega), `consignaciones/tests_midistri_codigo_v585.py`, `tests_midistri_codigo_pg_v585.py`, `tests_midistri_handoff_v585.py`.

U existentes: `midistri_bridge/models.py` importa nuevos modelos, `api.py`, `services.py`, `operadores.py`, `operadores_views.py`, `templates/midistri_bridge/operador_acceso.xhtml`, `sistema7000/settings.py`. Migración bridge aditiva nueva después de 0007; nombre exacto al generarla.

P nuevos: `midistri_portal/acceso_views.py` (Email/OTP), `sesion_pestana.py` (sesión y prueba), `sesion_views.py` (puente), `templates/midistri_portal/acceso_codigo.html`, `sesion_shell.html`, `operador_acceso_error.html`, `static/midistri_portal/acceso.js`, `sesion.js`, `test_codigo_v7.py`, `test_sesion_v7.py`, `test_handoff_v7.py`.

P existentes: `models.py`, `urls.py`, `views.py`, `client.py`, `middleware.py`, `operadores_views.py`, `templates/midistri_portal/base.html`, `activar.html`, `belnuweb/settings.py`; migración portal aditiva después de 0003. No tocar login de accounts ajeno al portal.

Comandos de test: U `python manage.py test consignaciones.tests_midistri_handoff_v585 consignaciones.tests_midistri_codigo_v585 --settings=settings585_pg --keepdb --noinput`; P `python manage.py test midistri_portal.test_handoff_v7 midistri_portal.test_codigo_v7 midistri_portal.test_sesion_v7 --settings=midistri_portal.test_settings --noinput`. Crear settings585_pg **sólo local tmp**, siguiendo settings584_focal y comprobando host local. No usar settings productivos para tests.

## Task 0: Evidencia y recuperación del acceso Distribuidor

**Files:** U/P operadores indicados arriba y tests de handoff; no migración necesaria para esta corrección.

**Interfaces:** `clasificar_desafio(request) -> (nonce: str | None, motivo: str | None)` en P; motivos exactamente los cinco del spec. `nombre_cookie_desafio(nonce: str) -> str` deriva nombre acotado por SHA256, nunca contiene nonce. Produce callback válido con permisos actuales y error recuperable sin intercambiar código inválido.

- [ ] Escribir `test_expirado_missing_cookie_origin_y_nonce_no_se_confunden`: afirmar razón interna correcta y cero llamadas a `operator-exchange`. `test_dos_desafios_no_se_pisan`: iniciar dos entradas y completar cada una con su cookie. `test_reinicio_no_reenvia_pase`: botón inicia nuevo flujo sin reutilizar códigos. Error sigue siendo 403, Origin ajeno falla y ningún log incluye token/nonce/cookie completos.
- [ ] Ejecutar tests de handoff y observar RED. Registrar condición exacta del fallo reportado si se consigue reproducir; conservar como pendiente si sólo se prueban causas posibles.
- [ ] Implementar cookie firmada por desafío, vigencia 600 segundos y máximo diez cookies de desafío por navegador (expirar antiguas en nuevas entradas); conservar pase Urban de 120 segundos y panel de ocho horas. Urban muestra plazo y acción de reinicio; P muestra error específico recuperable sin listar secretos. No quitar Origin/firma/CSRF ni convertir cookie ausente en autorización.
- [ ] Ejecutar GREEN y regresión `midistri_portal.test_operadores`/`consignaciones.tests_midistri_operadores_v583`; verificar clic completo local, demora y dos pestañas. En producción sólo validar navegación autorizada; no crear órdenes de prueba.
- [ ] Commit U/P con cambios explícitos: `fix: recover distributor browser handoff safely`.

## Task 1: Desafíos, identidad y cupos Urban

**Files:** U nuevos modelos/servicio/tests y `models.py`; migración aditiva.

**Interfaces:** `identidades_email(conexion, email: str) -> list[dict]` devuelve sólo internamente asociaciones con vendedor_id,distribuidora_id,contacto_id,version_contacto. `solicitar_codigo(conexion, email: str, desafio_hash: str, ip_hmac: str, *, ahora=None) -> dict` devuelve siempre `{version:1,solicitud:str,mensaje:str}`, sin identidad. `verificar_codigo(conexion, solicitud: str, codigo: str, desafio_hash: str, *, ahora=None) -> dict` produce ticket de selección y opciones opacas sólo tras verificar.

**Models:** `DesafioIngreso` (UUID,conexión,Email normalizado,desafio_hash,codigo_hash,creado,vence,intentos,usado/invalidado), `CupoIngreso` (clave HMAC,ventana,contador,unicidad), `EntregaCodigo` (desafío,estado,reclamado,resultado sin código/log). Para no persistir código en outbox, crear y enviar en la solicitud; el código sólo vive en memoria y en el transporte SMTP.

- [ ] Escribir tests `test_codigo_1799_valido_1800_vencido`, `test_cinco_errores_bloquean`, `test_reenvio_60s_y_cupos`, `test_email_inexistente_respuesta_generica`, `test_normalizacion_y_multiples_identidades`, `test_baja_campana_no_bloquea_login_contacto_inactivo_si`. Afirmar hash salado, ausencia de código/Email/IP en logs y ninguna alta de vendedor.
- [ ] Ejecutar RED con comando U; implementar consultas acotadas por conexión activa, normalización existente y validación de contacto sin política de marketing. Bloqueos select_for_update sólo sobre filas propias, no lado nullable de outer join. Cupos se incrementan incluso para Email sin asociación.
- [ ] Verificar GREEN. Añadir TransactionTestCase PostgreSQL: dos consumos concurrentes dan un único ticket; dos reenvíos no superan cupos; un desafío no invalida sesiones anteriores de otra pestaña.
- [ ] Commit U: `feat: add scoped one-use seller login codes`.

## Task 2: Email y API privada Urban

**Files:** U `acceso_codigo_email.py`, `acceso_codigo_api.py`, `api.py`, `services.py`, settings y tests anteriores.

**Interfaces:** `entregar_codigo(desafio_id, codigo: str) -> str` devuelve aceptado/fallido/por_conciliar, tras reclamación transaccional, sin guardar código. `seleccionar_identidad(conexion, ticket: str, seleccion: str, desafio_hash: str) -> dict` devuelve perfil y token sólo al servidor P. `responder_codigo(conexion, accion: str, data: dict) -> dict` implementa las tres acciones privadas del spec y se integra después de autenticación/cuota de aplicación existente.

- [ ] Escribir tests `test_codigo_no_depende_flag_campanas`, `test_smtp_incierto_no_se_reintenta_solo`, `test_seleccion_ticket_120s_un_uso_y_contacto_cambiado`, `test_conexion_ajena_no_canjea`, `test_api_no_expone_clave_y_capabilities`; simular SMTP. Afirmar que un ticket verificado no permite seleccionar un vendedor ajeno al Email.
- [ ] Ejecutar RED. Implementar SMTP posterior a commit con conexión de 15 segundos y remitente elegible determinista; no invocar procesar_campanas. Si no puede entregar, no conceder sesión. Selección revalida contacto vigente, vendedor, distribuidora y conexión, y audita ingreso sin código/Email completo. Agregar modo OTP y vínculo a identidad del contacto en AccesoVendedor de manera aditiva; validación continua no exige estar suscrito a marketing.
- [ ] Añadir capacidades `login_codigo:1`, `sesion_pestana:1` sin quitar contrato_pedido:2. Flag Urban `MIDISTRI_LOGIN_CODIGO_ENABLED=False`. Renovar límite de 90 días sólo para sesiones OTP vigentes en peticiones autorizadas, nunca una sesión revocada.
- [ ] Ejecutar GREEN y regresiones contactos/avisos de v584; commit U: `feat: expose transactional seller code login API`.

## Task 3: Pantallas de Email/código y sesión P

**Files:** P acceso_views, sesion_pestana, modelos, urls, acceso.js/plantillas, settings y test_codigo_v7.

**Interfaces:** `iniciar(request)`, `verificar(request)`, `seleccionar(request)` manejan POST con CSRF y devuelven JSON tipado, sin token Urban. `crear_sesion_pestana(request, perfil: dict, token_urban: str, tab_id: str, prueba: str) -> dict`; `resolver_sesion_pestana(request) -> SesionVendedorPortal | None`; `cerrar_sesion_pestana(request) -> None`. Nuevo modelo P `SesionVendedorPortal`: ID UUID, hash de prueba, hash de identificador de navegador, token Urban sólo en servidor, vendedor/distribuidora, creado/actividad/revocado. Carrito e idempotencia del pedido pertenecen a esta fila, no a la sesión compartida del navegador.

- [ ] Escribir `test_otp_30min_no_es_timeout_sesion`, `test_cookie_sola_no_identifica`, `test_seleccion_sin_ticket_no_entra`, `test_contactos_ajenos_no_se_revelan`, `test_api_caida_no_hace_login_legacy`. Afirmar que JSON/HTML/URL no contienen token Urban. Prueba tab de 32 bytes requerida y comparación constante de hashes.
- [ ] Ejecutar RED P. Implementar ingreso con seis dígitos y ceros iniciales, mensajes genéricos y selección sólo después de verificar. Flag P `MIDISTRI_LOGIN_CODIGO_ENABLED=False`; comprobar capacidades antes de ofrecer botón. Guardar tab_id/prueba sólo en sessionStorage y limpiar desafío después del canje. No usar localStorage ni token en query.
- [ ] Rotar sesión Django al autenticar sin borrar identificador de navegador ni otras filas de pestaña; cookie Secure/HttpOnly. El inicio P no crea usuario staff ni cambia sesión de distribuidor a vendedor silenciosamente.
- [ ] Ejecutar GREEN y pruebas de contrato; commit P: `feat: add email code sign-in with tab-bound sessions`.

## Task 4: Todo el flujo personal usa prueba de pestaña

**Files:** P sesion_views, sesion.js, views, urls, middleware, client y plantillas personales/activar; test_sesion_v7 y test_flujo_v7.

**Interfaces:** `datos_sesion(request, accion: str) -> HttpResponse` sirve perfil/carrito/pedidos/detalle/remito usando `resolver_sesion_pestana`; cabeceras `X-Midistri-Tab` y `X-Midistri-Tab-Proof`. Acciones permitidas son enum fijo, nunca URL externa. Servicios de carrito reciben una SesionVendedorPortal explícita. GET HTML personal devuelve shell neutro; fetch autorizado carga datos. POST valida CSRF, Origin y prueba.

- [ ] Escribir `test_recarga_y_navegacion_conservan_tab`, `test_tab_nueva_cookie_sola_no_ve_identidad`, `test_salir_revoca_solo_esa_tab`, `test_no_recupera_credencial_cookie_legacy`, `test_cierre_red_caida_limpia_cliente_y_no_restaura`, `test_remito_no_fuga_por_url`, `test_doble_click_pedido_conserva_idempotencia`, `test_suspendido_no_pierde_pedido_recibido`. Probar intento de cambiar UUID de pestaña/pedido y pertenencia a otra distribuidora.
- [ ] Ejecutar RED. Extraer lógica personal existente a servicios que aceptan estado de pestaña y conservan precios, revisión, PedidoLocal e idempotencia v6. Añadir cliente fetch, navegación interna y restauración de carrito por pestaña. Descarga PDF usa Blob y revoca URL temporal; login desde invitación antigua también crea sesión de pestaña mediante POST explícito. No importar cookies legacy automáticamente.
- [ ] Implementar Salir local inmediato y revocación servidor; si red falla, borrar prueba local, informar y no reabrir la sesión. No asegurar revocación remota hasta que se confirme; revocación pendiente se reintenta sin guardar la prueba en almacenamiento persistente. Mantener sesión de operador y otra pestaña. No usar beforeunload/pagehide para cortar recargas.
- [ ] Ejecutar GREEN y regresión portal completa. Validar browser local: recarga, pestaña nueva, enlace noopener, prueba modificada, 31 minutos simulados y restauración. Documentar el caso navegador que restaura sessionStorage; Salir es la garantía. Sin JS se consulta catálogo público y se explica cómo habilitar ingreso, nunca se muestra PII por cookie.
- [ ] Commit P/U si corresponde: `feat: isolate seller orders and logout by browser tab`.

## Handoff

Este subplan no activa funciones productivas ni publica paquetes por sí solo. Registrar migraciones reales, ejecutar subplan de comunicaciones y galería, y completar D1–D3 del plan principal.
