# Acceso MiDistri por Email y perfiles Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ingresar sólo con Email, código y selección posterior de perfil cuando sea necesaria.
**Architecture:** Contrato aditivo versionado para desafíos de Email, entregas por tienda y perfiles tipados. Se conserva el contrato anterior y el pase administrativo autenticado en Urban Soft. MiDistri sólo presenta las identidades que verifica Urban.
**Tech Stack:** Django 5.2/Python3.10 en Urban; Django3.2/Python3.7 en MiDistri. Pruebas locales, sin SMTP ni producción.
**Spec:** docs/superpowers/specs/2026-10-24-midistri-acceso-email-perfiles-design.md (aprobado por el usuario 24/10/2026).

## Global Constraints
- Código de 30 minutos, seis cifras, un solo uso; selector después de validarlo.
- Cada distribuidora usa su remitente efectivo. No se cambian SMTP, WhatsApp ni vínculos existentes.
- Sesión por pestaña existente; administración sigue autenticada en Urban y limitada a una tienda autorizada.
- Compatibilidad con desafíos anteriores; migración sólo aditiva; ningún cambio económico o de históricos.
- Entrega Urban598 y MiDistri14 separadas, con documentación, PDF principal, ZIP, comandos y commits GitHub. No enviar campañas.

## Review Focus
- Email compartido por distintas tiendas: nunca completar un envío usando el remitente de otra.
- Entrega parcial o por conciliar: sólo perfiles con entrega aceptada; reenvío invalida desafío viejo.
- Cuenta administrativa distinta en navegador: no canjear el perfil seleccionado con otra cuenta.
- Perfil deshabilitado después del código: se revalida al seleccionar y en cada operación.
- Cliente antiguo y código anterior: no convertirlo en autorización global ni romper su sesión.

## Task 1: Contrato Email, entregas e identidades en Urban
**Files:** Crear midistri_bridge/ingreso_email.py, ingreso_email_entrega.py, ingreso_email_models.py; migración0015_ingreso_email; consignaciones/tests_midistri_email_v598.py. Modificar models.py y api.py.
**Interfaces:** Acciones login-code-email-request/verify/select consumen conexion y desafío hash; request devuelve versión2/solicitud/mensaje genérico. Verify devuelve ticket opaco e identidades [{seleccion,nombre,distribuidora,tipo}]. Select devuelve sesión vendedor actual o continuación administrativa opaca.
- [ ] Escribir pruebas RED: dos tiendas con mismo Email, respuesta genérica, vencimiento1800/1799s, cinco intentos, cupos60s/3por15min, entrega fallida/aceptada y revocaciones.
- [ ] Ejecutar pruebas contra implementación anterior y observar fallos de función/contrato ausente.
- [ ] Implementar flujo independiente usando DesafioIngreso con marcador versionado, registro de entregas por tienda, tickets y continuación administrativa con hash; sólo callbacks on_commit, nunca SMTP con una transacción abierta.
- [ ] Resolver vendedor mediante candidatos_contacto vigente y administrador mediante cuenta activa/contexto_operador; verificar misma identidad después de OTP. No crear permisos por coincidencia de Email.
- [ ] Entregar cada alcance usando resolver_remitente y configuración vigente; registrar fallido/aceptado/por_conciliar sin código en claro; cancelar trabajos aún no iniciados de desafíos consumidos.
- [ ] Ejecutar regresión de código legado y nueva, check y makemigrations --check; guardar resultados y commit funcional.

## Task 2: Continuación administrativa autenticada
**Files:** Crear midistri_bridge/ingreso_email_views.py y template ingreso_email_admin.xhtml; modificar urls.py, seguridad_rutas.py y operadores.py; ampliar tests_midistri_email_v598.py.
**Interfaces:** Continuación opaca ligada a usuario/tienda/conexión/browser challenge, vence120s y sólo se consume por POST autenticado; produce pase existente para el callback del portal.
- [ ] RED: anónimo pide login, cuenta incorrecta rechazada, tienda ajena denegada, replay rechazado y permisos revocados denegados.
- [ ] Implementar confirmación autónoma con datos de una sola identidad, sin navbar de otras tiendas; crear pase sólo para esa cuenta y esa tienda revalidadas. Mantener CSRF, no cambiar selección ni cerrar sesiones silenciosamente.
- [ ] GREEN: pruebas del pase, rutas y alcance, incluyendo la cuenta superusuario y una cuenta sin permisos. Commit.

## Task 3: Entrada única en MiDistri
**Files:** Modificar acceso_views.py, acceso_codigo.html, acceso.js, catalogo_inicial.html, catalogo_productos.html, operadores_views.py, urls.py; crear test_acceso_email_v14.py.
**Interfaces:** Capacidad login_email_perfiles=1 habilita el contrato nuevo. Selección vendedor conserva crear_sesion_pestana; selección administrativa conserva token en sesión de servidor y continúa por desafío/cookie del pase existente.
- [ ] RED: no combo en ingreso/portada, inicia con varias tiendas sólo Email, única identidad directa, selección múltiple tipada y sin secretos; acción administrativa inicia pase en misma pestaña; capacidades incompatibles informan actualización necesaria.
- [ ] Implementar formulario único y selector posterior. Parámetros públicos de tienda no restringen silenciosamente este ingreso. Antiguas llamadas con tienda explícita permanecen en contrato legado por compatibilidad, sin selector nuevo visible.
- [ ] Reutilizar entrada administrativa con continuación guardada del lado servidor y cookie browser-bound; no exponer bearer Urban a JavaScript. Verificar tipos, límites y destinos fijos.
- [ ] GREEN suite completa midistri_portal en Django3.2 y revisión sintaxis3.7; JS syntax y QA navegador local con datos sintéticos. Commit.

## Task 4: Entrega y revisión
**Files:** Scripts de paquete/instalación Urban598 y MiDistri14, tests de paquetes, documentos técnicos/manuales/versiones/changelogs/checklists/PDF.
**Interfaces:** Instalar Urban598 (base597, migración0015) antes de MiDistri14 (base13, sin migración propia); no cambiar banderas ni envíos.
- [ ] Revisar los ocho documentos obligatorios de cada proyecto que existan; registrar comportamiento integrado y límites comprobados.
- [ ] Crear instaladores con hashes de base exacta, preflight sin escritura, migraciones objetivo exclusivas y respaldo privado de archivos. Bloquear reversión del código tras migración; recuperación hacia adelante y desactivar código si es necesario.
- [ ] Ejecutar pruebas de instalación/ZIP sobre bases reales, suites adecuadas, checks y migraciones. El intento de suite histórica completo se informa con sus fallos reproducibles, sin ocultarlos.
- [ ] Actualizar manual PDF principal mediante capítulo vigente y verificar portada/unión visualmente, manteniendo páginas anteriores.
- [ ] Revisión independiente final de ambos repositorios; corregir hallazgos importantes con RED/GREEN. No delegar implementación.
- [ ] Commits, push de ramas y PRs separados; registrar commits reales. Construir ZIP contra commit final, comprobar CRC/hashes/contenido, copiar sólo ZIP a Downloads y entregar comandos completos por separado.

## Estado
Plan escrito e implementación autorizada conjuntamente por el usuario. Sin cambios productivos. Avance y decisiones en .superpowers/sdd/2026-10-24-midistri-acceso-email-perfiles/progress.md.
