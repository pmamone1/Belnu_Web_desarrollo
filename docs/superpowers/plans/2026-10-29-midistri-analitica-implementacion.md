# MiDistri Analytics Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans; implementación nativa en este chat, con una revisión independiente final. Pasos con checkbox.

**Goal:** Resumen, ficha e historial verificable de vendedores, productos y pedidos, con grupos sin ingresos/sin pedidos y Excel.
**Architecture:** Urban suministra padrón/pedidos mediante instantánea privada paginada; MiDistri registra acciones locales y compone informes. Identidad y alcance se revalidan en ambos servidores. Caché técnica efímera en OperacionAdministrativa evita mezclar páginas cambiantes; no modifica datos comerciales.
**Tech Stack:** Urban Python3.10/Django/PostgreSQL; portal Python3.7/Django3.2, JavaScript existente, openpyxl.
**Spec:** docs/superpowers/specs/2026-10-29-midistri-analitica-vendedores-design.md, aprobado por usuario29/10/2026.

## Global Constraints
- Sin campañas, correos, cargos, cambios de remitentes, WhatsApp, precios o históricos. No usar producción como prueba.
- Sólo vendedor autenticado para captura. Operador necesita pedidos.gestionar y midistri.tienda_configurar.20/65 como bloque autorizado; ninguna otra tienda se amplía.
- UTC en almacenamiento, Argentina en pantalla, rangos inclusivos por días locales. Pedidos desde creado original de Solicitud, no copia local.
- Captura inicialmente apagada; activar/desactivar por comando en el portal, con intervalos de cobertura, conservando datos.
- Estado actual de pedidos separado de lo solicitado; cancelaciones no suman confirmado. Sin truncado oculto, falsos ceros o porcentajes mayores100.
- Conservar archivo ajeno modificado templates/accounts/forgotPassword.html del portal; no incluirlo en commit/ZIP.

## Review Focus
1. Sesión iniciada antes del período, varias pestañas y misma identidad con varios Emails: actividad y vendedor únicos correctos.
2. Fuente incompleta/caída/cursor duplicado o credenciales revocadas: no fabricar grupos negativos ni filtrar datos cacheados ajenos.
3. Fotos fallidas, carrusel automático, MP4 pausado y enlace externo: registrar acciones con etiquetas veraces.
4. Pedido de más100 filas, cancelación parcial/nativa y precios de maestro cambiados: fuente histórica íntegra y consultas acotadas.
5. Fallo de telemetría, reintentos y rollback: nunca bloquear el circuito comercial ni borrar esquema/eventos.

### Task1 · Fuente privada Urban
Files: midistri_bridge/analitica.py, operadores_api.py, api.py; consignaciones/tests_midistri_analitica_v621.py.
Interface fuente(acceso,ctx,data)->JSON version1. Entrada distribuidora,desde,hasta; continuación snapshot(UUID),fase(vendedores/pedidos),cursor entero. Primera lectura crea caché técnica15min en OperacionAdministrativa tipo analitica, propietario/conexión/alcance. Cada página500 filas con total, siguiente, corte. Máximo20000 vendedores/20000 pedidos por consulta: rechazo explícito antes de crear informe incompleto.
Padrón activo/no depósito más identidades históricas: id,distribuidora,nombre,lin,vv,activo,actual,contacto bool,pedidos_historicos. Pedidos: id,vendedor,distribuidora,referencia,creado,estado,items públicos,atencion actual; sin costo/contactos/tokens.
- [ ] RED: API ausente, padrón/estados/cancelaciones/precios, página>100, snapshots inmutables, permisos y20/65.
- [ ] Implementar proyección agrupada con prefetched pedidos/folio y resumir_atencion; no N+1 por vendedor ni s.serializar por cada fila.
- [ ] GREEN: manage.py test consignaciones.tests_midistri_analitica_v621; sin nuevos movimientos/modelos Urban. CommitTask1.

### Task2 · Modelos y captura portal
Files: analitica_models.py, models.py, migrations/0012_analitica.py, analitica_captura.py, management/commands/midistri_analitica.py; test_analitica_captura_v28.py.
Interface registrar(request,perfil,tipo,producto=None,recurso=None,cantidad=None,pedido=None,event_id=None) tolera fallo de analítica; recibir_lote(request,perfil,events) valida antes de persistir. Control global defaultFalse; intervalos por tienda. SesionAnalitica identifica pestaña+actor con hash interno, UUID de visita rota tras30min sin tocar acceso. EventoAnalitico idUUID único con datos mínimos. ConsultaAnalitica guarda caché técnica de informe15min, nunca credenciales.
- [ ] RED: flag apagada, control/cobertura, identidad, dedup/cambio de payload, visitas/pestañas, fallo de DB y recurso ajeno.
- [ ] Implementar transacciones cortas y savepoints; límites20 eventos/lote,100 eventos/min por pestaña,20000 filas/fuente. No purga de eventos. Errores capturables se loguean sin datos sensibles; cobertura conocida y aviso de medición orientativa.
- [ ] GREEN: pruebas nuevas y sesión/acceso existentes. CommitTask2.

### Task3 · Captura integrada
Files portal: views.py, sesion_pestana.py, acceso_views.py si necesita perfil; urls.py, analitica_views.py, base.html, galeria.html/js, nuevo analitica.js. Tests: test_analitica_integracion_v28.py y pruebaJS.
- [ ] RED: ingreso exitoso una vez por token, catálogo autenticado, carrito válido, pedido aceptado (UUID único), galería/MP4/enlace y exclusión de administración/anónimos.
- [ ] Registrar desde éxitos del servidor; POST protegido de eventos obtiene identidad del contexto validado, no IDs del cliente. Contexto de página después de identificar limita recursos; evento no agrega petición Urban por foto. JS cola100, lote20, reintento acotado y separación por actor; hora oficial de recepción.
- [ ] GREEN: flujo de sesión/pedido existente y las pruebas de integración. CommitTask3.

### Task4 · Informes y pantalla
Files portal: analitica_fuentes.py, analitica_informes.py, analitica_views.py, templates/analitica*.html, static/analitica_panel.js/css; operadores.py/base.html, urls.py. Urban: enlace a la misma vista mediante destino estadisticas en ingreso existente. Tests: test_analitica_informes_v28.py, test_analitica_panel_v28.py y Urban destinos.
Interface iniciar_consulta(request,perfil,datos)->Consulta; avanzar_consulta(request,consulta,revision) descarga una página y es idempotente por revisión bajo bloqueo. Respuesta carga/progreso/error con reintento. resultado(consulta,filtros) exige completa/no expirada/permisos actuales. Fuente creada vía operador, corte compartido; eventos locales hasta corte.
- [ ] RED: cruce completo, grupos negativos, inactivos/traslados, periodos, conversión0 y pedidos sin visita; error API no se vuelve cero. Excel coincide y evita fórmulas.
- [ ] Implementar resumen, vendedores, ficha, productos e historial50filas; filtros por grupo/nombre/LIN/VV/producto/tipo, Excel acotado de hasta20000 filas por hoja sin truncar. Indicar fuente/inicio/intervalos de captura y estado; inactivos/históricos separados del padrón actual.
- [ ] GREEN: pruebas de informes/pantalla + navegador local escritorio/móvil. CommitTask4.

### Task5 · Entrega coordinada
Urban621 sobre620; MiDistri28 sobre27, bases exactas verificadas, preservando cambios ajenos. Sólo portal0012 aditiva; Urban sin migraciones nuevas. Instalar Urban, portal, comprobar contrato, ejecutar midistri_analitica --activar; detener con --desactivar sin borrar. El cron de catálogo se conserva.
- [ ] Actualizar los8 documentos obligatorios de cada proyecto, manual PDF/prioridad y unión, VERSION_DOCUMENTADA, CAMBIOS y guías de instalación/rollback.
- [ ] Pruebas de instalador y bytes exactos de bases; no secretos/base/media/venv en ZIP. Captura no se activa durante instalación.
- [ ] Revisión final fresca del conjunto en modelo más capaz; una pasada de correcciones RED→GREEN si procede, regresión verde.
- [ ] Publicar commits/PR y ZIP separados verificados en Downloads. Comandos completos cPanel, hashes y estado productivo pendiente. No pedir otra aprobación de plan: el usuario autorizó prepararlo e implementarlo en este mismo chat.
