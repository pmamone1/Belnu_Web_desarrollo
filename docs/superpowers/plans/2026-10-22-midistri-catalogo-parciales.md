# Catálogo público y pedidos parciales de MiDistri — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Método ya elegido por el usuario: implementación por el agente principal en este chat y revisión independiente final; no delegar tareas de implementación.

**Goal:** Publicar precio vendedor y categorías; preparar pedidos parciales sin cobrar faltantes; enviar a todos los contactos habilitados y exportar abastecimiento agregado para Urban Point.

**Architecture:** Urban conserva la autoridad de permisos, solicitud original, preparación, saldo, remito y contactos. MiDistri muestra catálogo público y el detalle validado de la preparación mediante un contrato aditivo. Una revisión transaccional común sirve al panel nativo y al Distribuidor delegado; los Emails usan las colas existentes.

**Tech Stack:** U Python 3.10 / Django 5.2 / PostgreSQL; P Python 3.7 / Django 3.2 / MariaDB; Decimal, openpyxl, PDF nativo, unittest/Django tests existentes. Sin dependencias nuevas previstas.

**Spec:** ../specs/2026-10-22-midistri-catalogo-parciales-design.md

## Global Constraints
- U base 3d6aedd7e452bcf9370eb4d31748490a2695c2b6, v1.18.583; entrega v1.18.584.
- P base dd4478782c4f1e341c6345743a86af289948e35f, v5; entrega v6.
- U y P mantienen repos, paquetes, instalaciones y runtimes separados; SIB2 y venv intactos.
- Precio vendedor también público; total a precio vendedor. PVP nunca se usa para cobrar.
- Preparadas enteras de 0 a solicitadas; el resto se cancela, sin saldo pendiente de entrega.
- Solicitud.items/huella y documentos históricos se conservan.
- Misma confirmación no duplica cargo, pedido, PDF, aviso ni invitación.
- Email sólo a destinos habilitados y respetando bajas; no confirmar/enviar campaña d3c5dbbc-6d01-4f89-a017-1bb91d4f74c5.
- Todos los destinos válidos de MiDistri; preferencias de otros circuitos sin cambios.
- Excel a Urban Point sin nombres, LIN, VV, Emails ni teléfonos de vendedores.
- QA local ficticia; no conectar tests ni fixtures a producción.
- ZIPs explícitos con manuales/PDF, documentación, migraciones, hashes, comandos completos y commits publicados reales.
- Instalación escalonada: P6 primero, U584 después; no usar parcial hasta que Urban anuncie la capacidad.

## Review Focus
- Precio público no habilita pedidos, identidad ni PDF sin sesión: test de T6.
- Confirmaciones concurrentes o PDF fallido no dejan dos cargos ni una preparación huérfana: T2 y T9.
- Dos contactos del mismo vendedor pueden activar sus enlaces; una baja de campañas no borra una sesión válida: T3/T4.
- Un histórico emitido sin nueva preparación mantiene el total/PDF original; respuesta v2 malformada no se interpreta como total: T1/T7.
- Un faltante cancelado no reaparece como pendiente de abastecimiento ni el Excel mezcla datos privados de vendedores: T5/T8.

## Mapa de repos y archivos
U local: C:/Users/pmamo/.codex/worktrees/urban-ayuda-curso-v556/repo-v496.
P local: C:/Users/pmamo/.codex/worktrees/midistri-pedidos-integracion.
Rutas prefijadas U/ o P/ se resuelven dentro de cada repo.
Crear módulos pequeños: U/midistri_bridge/preparacion.py para cantidades/revisión; U/midistri_bridge/abastecimiento.py para agregado/Excel; U/midistri_bridge/preparacion_views.py para pantalla nativa. No rehacer servicios nativos económicos.

## Entorno de comprobación
- Conservar cambio ajeno P/templates/accounts/forgotPassword.html; no incluirlo.
- Usar los worktrees adecuados existentes; crear ramas codex/midistri-parciales-v584 y codex/midistri-parciales-v6 antes del código.
- Preparar U/tmp/settings584.py SQLite ficticio y U/tmp/settings584_pg.py PostgreSQL local; ambos deben rechazar hosts distintos de localhost/127.0.0.1 y bases no dedicadas a QA. Fixtures/runtime son ignorados y no se empaquetan.
- Para U, añadir tmp y dependencias QA existentes a PYTHONPATH y usar python -B manage.py test ... --settings=settings584 --noinput; las pruebas de locks/transacciones usan settings584_pg.
- Para P, PYTHONPATH=.;tmp/qa_dependencies y python -B manage.py test ... --settings=midistri_portal.test_settings --noinput. La sintaxis de producto e instalador se valida para Python 3.7.
- Registrar RED y GREEN de cada tarea; no ejecutar otra vez suites completas sin cambios/fallos que lo justifiquen.

### T1 — Atención final aditiva y contrato
**Files:** crear U/midistri_bridge/preparacion.py, U/consignaciones/tests_midistri_parciales_v584.py; modificar U/midistri_bridge/models.py, services.py; crear U/midistri_bridge/migrations/0006_preparacion.py.
**Interfaces:** normalizar_cantidades(items:list, cantidades:list)->list canónica; resumir_atencion(sol, propuesta=None)->dict del contrato; services.serializar(sol) añade contrato_pedido=2 y atencion.
- [ ] Escribir test RED: pedido de 10 a 25000/PVP30000 y propuesta6 produce preparada6/cancelada4/total_solicitado250000.00/total_preparado150000.00; Solicitud.items queda idéntica.
- [ ] Añadir casos de producto faltante/duplicado/ajeno, bool, negativo, fracción y cantidad11; rechazarlos sin escritura. Histórico emitido sin preparacion se interpreta completo y no se guarda; pendiente muestra total preparado0.
- [ ] Ejecutar python -B manage.py test consignaciones.tests_midistri_parciales_v584 --settings=settings584 --noinput; confirmar fallo esperado.
- [ ] Implementar normalización pura y resumen; añadir JSONField preparacion con default=dict mediante migración aditiva sin RunPython económico.
- [ ] Reejecutar focal y verificar migración sobre fixture anterior sin cambiar items, huella, saldos o documentos.
- [ ] Commit sólo archivos T1; no afirmar pruebas productivas.

### T2 — Revisión común, emisión parcial y PDF nativo
**Files:** modificar U/midistri_bridge/preparacion.py, services.py, administracion.py, operadores_api.py, views.py, urls.py; crear U/midistri_bridge/preparacion_views.py y templates/midistri_bridge/preparacion.xhtml; modificar gestion.xhtml; crear U/consignaciones/tests_midistri_preparacion_pg_v584.py.
**Interfaces:** preparar_revision(user,ident,cantidades,*,ctx=None,conexion_id=None)->{revision,pedido,preparacion_previa}; confirmar_revision(user,revision_id,*,ctx=None,conexion_id=None)->resultado. services.emitir(user,ident,*,ctx=None,cantidades=None) consume cantidades ya validadas; None conserva emisión completa antigua.
- [ ] RED PostgreSQL: aprobar10, revisar6, confirmar genera asignación6, cargo150000, remito con6; items original10. Segundo POST misma revisión conserva ids/PDF/saldo. Todas0 cancela sin pedido/PDF/cargo.
- [ ] Casos: revisión caducada15min, otra conexión/usuario/distribuidora, permiso financiero ausente, cambio de estado, producto de otra solicitud y nueva cantidad enviada al POST final. Rechazar. Fallo inyectado en PDF revierte la operación completa.
- [ ] Ejecutar focal PG y observar RED; revisar SQL de locks sin joins opcionales.
- [ ] Guardar cantidades canónicas en OperacionAdministrativa, ligadas a actor/conexión/alcance/huella. Al emitir usar sólo unidades positivas, snapshots originales y aplicar_saldo_pedido nativo. Revalidar permisos antes de devolver incluso un resultado ya confirmado.
- [ ] Urban nativo pasa por una pantalla de revisión; su POST antiguo emitir sin revisión no carga saldos y redirige a revisar; operador MiDistri usa los mismos servicios. Añadir inputs y resumen readonly; checkbox para confirmar cargo y preparación.
- [ ] GREEN focal PG; comparar bytes del documento histórico previo y saldos de otro vendedor. Commit T2.

### T3 — Invitaciones independientes por contacto
**Files:** modificar U/midistri_bridge/models.py, services.py; crear U/midistri_bridge/migrations/0007_contactos_acceso.py y U/consignaciones/tests_midistri_contactos_v584.py.
**Interfaces:** invitar_contacto(user,conexion_id,vendedor_id,contacto,*,ctx=None)->(Invitacion,token); contacto contiene contacto_id, destino y version, resueltos por backend. crear_acceso(c,vendedor,*,invitacion=None) conserva el uso legado y guarda AccesoVendedor.invitacion_origen cuando corresponde.
- [ ] RED: dos contactos A/B del mismo vendedor crean invitaciones distintas; activar A y luego B permite identificar ambos accesos. Renovar A invalida pendiente anterior de A, no B.
- [ ] Casos: 48h vencida, un uso, Email cambiado/contacto desactivado, vendedor trasladado/inactivo, revocación global y otra conexión. Baja de campañas impide nuevo envío, pero no revoca por sí sola sesión ya activada.
- [ ] Correr tests_midistri_contactos_v584 y confirmar RED.
- [ ] Añadir a Invitacion destino_normalizado, contacto_adicional opcional y version_contacto; a AccesoVendedor invitacion_origen opcional. Defaults vacíos para históricos, sin convertirlos.
- [ ] Mantener invitar/activar históricos; para invitaciones con destino, bloquear vendedor y reemplazar sólo sesiones del mismo destino. En identificar revalidar identidad/contacto vigente sin confundir baja promocional con revocación de sesión.
- [ ] GREEN focal más activación/revocación antigua de tests_midistri_bridge/tests_midistri_v580; commit T3.

### T4 — Todos los Emails y aviso con cantidades realmente preparadas
**Files:** modificar U/consignaciones/comunicaciones_contactos.py, comunicaciones_campanas.py, comunicaciones_campanas_views.py, comunicaciones_campanas_models.py, templates/consignaciones/comunicaciones_campanas_detalle.xhtml y comunicaciones_campanas_previa.xhtml; U/midistri_bridge/campanas_acceso.py, avisos.py, views.py; crear U/consignaciones/migrations/0123_midistri_acceso_destinos.py y tests_midistri_envios_contactos_v584.py.
**Interfaces:** candidatos_contacto(...,respetar_preferencia=True) y destinos_habilitados(...,respetar_preferencia=True) conservan default; consumidores MiDistri usan False pero respetan contactos activos/recibe_email y bajas. elegir_contactos(...,choice=None) devuelve todos para None, '' o 'todos'; selección explícita de principal/id sigue disponible.
- [ ] RED: principal y adicional producen2 Emails, duplicado normalizado sólo1 por vendedor; dos vendedores con igual Email generan2 accesos privados. Preferencia principal de circuitos ajenos no cambia.
- [ ] Añadir tests: límite5000 tras expandir; sin permiso/opt-out excluye; vieja previa no se amplía sola; reintento no duplica enviado; token de A no se usa para B; estado SMTP incierto exige conciliación.
- [ ] Test aviso emitido parcial6/10 incluye6, canceladas4, total150000 y mismo PDF; no manda pedido original10 como entregado. Todas0 usa cancelación.
- [ ] Ejecutar focal y confirmar RED.
- [ ] Migrar constraint de acceso a unicidad por campaña+vendedor+Lower(destino), conservando la de promoción. No tocar filas históricas ni confirmadas. En nuevas previas informar vendedores y Emails; validar versión de revisión antes de confirmar.
- [ ] Bloquear/releer el EnvioCampana antes de crear su invitación; usar invitar_contacto por envío y sobre cifrado exacto; conservar cola/Aviso y resultados por destino. No enviar SMTP real en tests.
- [ ] GREEN focal, tests_midistri_campanas_v583 y regresiones de comunicaciones de contactos/transportes; commit T4.

### T5 — Abastecimiento agregado para Urban Point
**Files:** crear U/midistri_bridge/abastecimiento.py, abastecimiento_views.py, templates/midistri_bridge/abastecimiento.xhtml y U/consignaciones/tests_midistri_abastecimiento_v584.py; modificar urls.py, gestion.xhtml, operadores_api.py.
**Interfaces:** filas_abastecimiento(user,*,desde,hasta,estado='pendientes',ctx=None,conexion_id=None,distribuidora_ids=None)->list agregada; excel_abastecimiento(filas)->bytes XLSX; API operator-order-supply usa alcance delegado y devuelve binario XLSX.
- [ ] RED: original10/preparado6 genera solicitadas10, preparadas6, canceladas4 y pendientes0 al filtrar todos; pendiente10 muestra pendientes10. Histórico emitido completo no cambia.
- [ ] Casos: códigos iguales de distinto producto no se fusionan, fechas locales inclusivas hoy−29/hoy, otro alcance403, texto=SUM(...) neutralizado en Excel y201 pedidos rechazados sin truncar.
- [ ] Afirmar que libro no contiene nombre vendedor, LIN, VV, Email/teléfono o costo proveedor; exporter depósito anterior mantiene su orden y detalle privado.
- [ ] Ejecutar focal y confirmar RED.
- [ ] Implementar consulta autorizada y agrupación por distribuidora/producto/SKU/nombre histórico; descargar Excel y auditar sin contactos. No cruzar contra stock ni generar compras.
- [ ] GREEN focal; revisar libro con openpyxl; commit T5.

### T6 — Catálogo público con categoría y precio vendedor
**Files:** modificar P/midistri_portal/views.py, templates/midistri_portal/catalogo.html y carrito.html; crear P/midistri_portal/test_catalogo_v6.py.
**Interfaces:** contexto catalogo añade categorias y categoria seleccionada; GET categoria conserva valor al paginar y volver del carrito. Valores reservados: '' Todas y '__sin_categoria__' para vacío; categorías reales se validan contra la tienda actual.
- [ ] RED: visitante ve Precio vendedor25000 y PVP30000; filtro categoría+nombre reduce publicaciones y conserva ambos filtros al paginar; no muestra categoría exclusiva de otra tienda ni producto inactivo.
- [ ] Test sin sesión no crea carrito/pedido ni obtiene identidad/remito. Sesión vendedor fija su distribuidora pese a GET ajeno. Subtotal2×25000=50000, no60000.
- [ ] Ejecutar python -B manage.py test midistri_portal.test_catalogo_v6 --settings=midistri_portal.test_settings --noinput y confirmar RED.
- [ ] Implementar filtros y etiquetas públicas, manteniendo las validaciones existentes, Display0 y cálculos Decimal. Mantener forma de pedir protegida.
- [ ] GREEN focal y test_display_cero; commit T6 en P.

### T7 — Contrato validado y preparación parcial en MiDistri
**Files:** modificar P/midistri_portal/contract.py, administracion_contract.py, operadores_views.py, views.py y templates detalle.html/operador_pedido.html/pedidos.html; crear test_parciales_v6.py. U/midistri_bridge/api.py añade GET order/<uuid> y capabilities, y prueba en tests_midistri_parciales_v584.
**Interfaces:** pedido_valido valida contrato_pedido=2/atencion y retorna sus campos; ausencia permite legado. Endpoint individual sólo propio. capabilities anuncia contrato_pedido=2 y preparacion_parcial/acceso_por_contacto; sólo respuesta antigua404/405 permite modo legado. Panel envía cantidades al revisar; confirmar sólo revision y aceptación.
- [ ] RED: contrato v2 con solicitadas10/preparadas6/canceladas4 y totales correctos pasa; inconsistencia de precio/cantidades o producto extra falla sin sobrescribir copia local.
- [ ] Test detalle actualiza estado y total a150000 al abrir, sin visitar lista; fallos de red conservan último dato claramente fechado y sin ejecutar operaciones.
- [ ] Test P6 ante U583 sin capacidad mantiene preparación completa antigua y oculta edición parcial. Respuesta v2 inválida nunca cae al modo legado.
- [ ] Ejecutar focal P y test endpoint U, observar RED.
- [ ] Implementar validación de aritmética Decimal, formularios con solicitado/preparado/cancelado, revisión y confirmación del resultado parcial. Exponer descarga PDF y estado de Email sin crear otra cola.
- [ ] GREEN focal P más test_contract/test_operadores/test_administracion; commit T7 por repo.

### T8 — Descargar abastecimiento desde el panel Distribuidor
**Files:** crear P/midistri_portal/templates/midistri_portal/operador_abastecimiento.html y test_abastecimiento_v6.py; modificar operadores_views.py, urls.py, operador_pedidos.html.
**Interfaces:** POST a midistri_operador_abastecimiento pasa distribuidora de contexto, fechas y estado a operator-order-supply usando operator_token; valida MIME/estructura XLSX con client.api existente.
- [ ] RED: descarga devuelve sólo agregado de su tienda; parámetro oculto de otra distribuidora se rechaza/ignora fijando contexto autorizado; permisos insuficientes403. Respuesta HTML o binario inválido no se ofrece como Excel.
- [ ] Ejecutar focal y confirmar RED.
- [ ] Añadir filtros y botón Excel para Urban Point, distinto al Excel de depósito. No configurar destinatario ni enviar Email.
- [ ] GREEN focal P; commit T8.

### T9 — Verificación conjunta y revisión independiente
**Files:** fixtures y scripts sólo U/tmp y P/tmp; pruebas PG entregables de T2/T3 se amplían si falla concurrencia. Sin datos de producción.
- [ ] Ejecutar suites focales nuevas y regresiones existentes de U bridge/menu/catálogos/campañas/permisos, y toda midistri_portal de P una vez.
- [ ] Probar PG real local con dos confirmaciones simultáneas; un único cargo/PDF/pedido y un solo aviso. Dos contactos activados en paralelo siguen vigentes.
- [ ] Levantar ambas apps localmente con fixtures ficticias. Verificar categorías públicas, precios, pedido2productos, parcial de uno y0 de otro, remito/cargo correctos, detalle vendedor y Excel sin datos privados.
- [ ] Capturar pantallas de catálogo, revisión, resultado parcial y Excel. Probar límites PDF y respuestas HTTP ya existentes sin alterar sus políticas.
- [ ] Django check, makemigrations --check --dry-run en ambas. Registrar entorno real de cada prueba; no declarar Python3.7/MariaDB probado si sólo se validó sintaxis en Python3.12/SQLite.
- [ ] Pedir revisión independiente final del diff conjunto; corregir hallazgos Important/Critical y revalidar el cambio afectado antes de publicar.

### T10 — Documentación y dos releases instalables
**Files U:** README.md, HANDOFF.md, VERSION_DOCUMENTADA.txt, docs/00_INDICE.md, 04_REGLAS_DE_NEGOCIO.md, 05_FLUJOS_FUNCIONALES.md, 17_CHECKLIST_ENTREGA.md, 19_PRUEBAS_MANUALES_CRITICAS.md, MANUAL_USUARIO.md, Manual_Urban_Soft.pdf; CAMBIOS_v1_18_584_midistri_parciales.txt, COMANDOS_CPANEL_v1_18_584.txt, docs/MIDISTRI_PARCIALES_v584.md, scripts/instalar_v584.py, test_instalar_v584.py, paquete_v584.py, actualizar_manual_v584.py, release_files_v584.json.
**Files P:** mismos documentos base de P, Manual_MiDistri_Pedidos_Online.pdf; CAMBIOS_v6_pedidos_parciales.txt, COMANDOS_CPANEL_MIDISTRI_v6.txt, docs/PEDIDOS_PARCIALES_v6.md; tools/instalar_release_midistri_v6.py, test_instalar_release_midistri_v6.py, paquete_integracion_v6.py, actualizar_manual_v6.py, release_files_v6.json.
- [ ] Actualizar manuales/reglas/compatibilidad, contratos públicos/privados, cantidades canceladas, contactos e informe. Capítulo vigente delante de cada PDF, verificar visualmente la unión. Estado instalación productiva pendiente.
- [ ] RED instaladores: raíz/runtime incorrectos, archivos cambiados, paquete alterado, migración desconocida/ajena, reversión, instalación repetida y restauración insegura rechazados sin reemplazos parciales.
- [ ] U exige base583 y permite sólo bridge0006/0007 y consignaciones0123 en el plan; P exige base5 y plan de migraciones vacío. Respaldo privado de código antes de copiar. No cambiar claves, flags, venv, datos económicos o campañas al instalar.
- [ ] Definir recuperación hacia adelante: U bloquea restore si sus targets están aplicados; P consulta capabilities y bloquea restore a v5 si Urban anuncia parcial o no puede comprobarlo. Probar estas ramas sin red real; impedir código antiguo que malinterprete preparaciones/accesos. Mantener copia de código y esquema.
- [ ] GREEN instaladores y preflight real sobre bases sintéticas anteriores; hashes de filas/saldos/documentos antes/después sin cambios por instalación.
- [ ] Crear commits separados sólo con inventarios explícitos. Construir urban_soft_v1_18_584_midistri_parciales.zip y midistri_pedidos_v6_pedidos_parciales.zip; verificar CRC, hashes, contenido, sintaxis destino y coincidencia byte a byte con cada commit.
- [ ] Guardar sólo ZIP+SHA en Downloads; manuales e instrucciones dentro del repo/ZIP. Publicar dos ramas/PR independientes y adjuntar ambos PR al chat. Informar hashes/commits reales, sin afirmar deploy.
- [ ] Entregar comandos completos P6 primero (belnuweb Python3.7), después U584 (sistema7000 Python3.10), reinicio/check explícitos. No nuevo respaldo completo dentro del intervalo vigente.
- [ ] Después del recibo del usuario, verificar versión/capacidades, catálogos y remitentes sin pedidos reales. Mantener campaña en borrador hasta autorización nueva de envío.

## Autorrevisión del plan
Completada el22/10/2026 sobre el texto: catálogo/precio→T6; cantidades/snapshots→T1; cargos/PDF/locks→T2; accesos por destino→T3; todos los contactos/Email→T4; abastecimiento agregado→T5/T8; contrato/UI→T7; integración y cinco focos→T9; documentación/paquetes/rollback→T10. Interfaces y nombres cotejados. Ninguna tarea fue ejecutada todavía.
Este documento es un plan; no certifica código implementado, migraciones ejecutadas, pruebas pasadas ni despliegue.
