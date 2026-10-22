# MiDistri: campañas e historial — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Ejecución por el principal en este chat; revisión final según plan principal.

**Goal:** Configurar el contenido real de Emails MiDistri y ordenar la consulta de avisos, sin enviar la campaña pendiente.

**Architecture:** Urban guarda configuración por distribuidora y congela la presentación por campaña. MiDistri consume sólo configuración pública de tienda; SMTP usa credenciales autorizadas y Reply-To validado. Avisos conservan sus registros y conciliación por destinatario.

**Tech Stack:** Django Forms/ORM, SMTP existente, templates escapados, PostgreSQL Urban y cliente HTTPS MiDistri.

**Spec:** `docs/superpowers/specs/2026-10-22-midistri-acceso-codigo-y-tienda-design.md`, apartados D–E,G–H. Coordinación: `2026-10-22-midistri-acceso-codigo-y-tienda.md`.

## Global Constraints

- No enviar todavía la campaña existente ni invitaciones nuevas. No confirmar, encolar ni enviar durante implementación, instalación o revisión.
- No prometer entrega en 48 horas salvo texto configurable revisado; portal para pedidos, sin pago online.
- Seleccionar vendedor incluye todos sus destinos Email activos/habilitados en campañas MiDistri, con bajas y deduplicación por destino.
- Nombre visible configurable no cambia la dirección From autorizada; Reply-To coincide con pie visible.
- Permisos/alcance privados se comprueban en backend, también en detalle y exportación de avisos.

## Review Focus

1. Remitente compartido 20/65 y configuración comercial diferente por distribuidora (tarea 1).
2. CR/LF, HTML y texto vacío en cabeceras/cuerpo; sin inyección ni cabeceras inválidas (tareas 1–2).
3. Editar configuración tras una previa/confirmación no altera silenciosamente Emails aprobados (tarea 2).
4. Reintento SMTP incierto y revisión de historia nunca disparan reenvío (tareas 2–3).
5. Contacto adicional desactivado o dado de baja después de previa, y más destinatarios que el límite (tarea 2).

---

## Task 1: Configuración canónica por distribuidora

**Files U:** crear `midistri_bridge/configuracion_tienda.py`, `configuracion_views.py`, `templates/midistri_bridge/configuracion.xhtml`, `consignaciones/tests_midistri_configuracion_v585.py`; modificar `models.py`, `api.py`, `operadores_api.py`, `urls.py`, `consignaciones/seguridad_rutas.py`. Migración bridge aditiva tras las de Acceso.

**Files P:** modificar `midistri_portal/operadores_views.py`, `presentacion.py`, `templates/midistri_portal/operador_tienda.html`, `test_presentacion.py`.

**Interfaces:** U `configuracion_publica(conexion, distribuidora_id: int) -> dict` sólo nombre_comercial/email_respuesta/texto_entrega/revision, sin SMTP. `guardar_configuracion(usuario, distribuidora_id: int, datos: dict, revision: int, operacion_id: str, *, ctx=None) -> dict` idempotente por UUID y huella; permiso `midistri.tienda_configurar`. Modelo `ConfiguracionTiendaMiDistri`: distribuidora OneToOne, campos del spec y revisión. Nueva API privada delegada `operator-store-settings`/`operator-store-settings-save`; guardado usa current operator-profile, no IDs enviados como autoridad. P `guardar_configuracion_urban(perfil, token, datos, revision, operacion_id) -> dict` no modifica copia local si Urban rechaza.

- [ ] Escribir `test_dos_distribuidoras_remitente_compartido_config_distinta`, `test_sin_permiso_o_dist_ajena_rechaza`, `test_email_invalido_crlf_y_limites`, `test_revision_obsoleta_y_uuid_repetido`, `test_defaults_preservan_responsable`. Verificar defaults sin escribir filas al consultar y ninguna credencial en JSON público.
- [ ] Ejecutar RED U/P. Implementar formulario Urban y edición desde Mi tienda por API privada, con Urban como única autoridad de nombre comercial/Email de respuesta. Resto de presentación P conserva su autoridad local. Mostrar estado por sección si un guardado remoto falla; no anunciar éxito global de una operación parcialmente guardada. Registrar auditoría por distribuidora y actor sin secretos.
- [ ] Implementar validación de longitudes exactas del spec, Email y cabeceras; sólo texto plano. Agregar estos campos públicos a snapshot como sección opcional compatible con P6; el consumidor nuevo tolera ausencia y usa nombre/responsable previos. No sobrescribir contactos históricos ni fila de remitente compartido.
- [ ] Ejecutar GREEN y tests de permisos/configuración/operadores; commit U/P: `feat: configure distributor MiDistri messaging identity`.

## Task 2: Campaña de URL general y vista previa exacta

**Files U:** crear `midistri_bridge/campanas_presentacion.py`, `consignaciones/tests_midistri_campana_codigo_v585.py`; modificar `campanas_acceso.py`, `consignaciones/comunicaciones_campanas_models.py`, `comunicaciones_campanas.py`, `comunicaciones_campanas_views.py`, `comunicaciones_campanas_transportes.py`, templates de formulario/detalle/previa, `consignaciones/models.py` si necesita reexportar modelo. Migración consignaciones aditiva después de 0123, sólo nuevos campos de campaña/snapshot.

**Interfaces:** `presentacion_campana(ctx, campana) -> dict` valida distribuidora, modalidad, campos y URL; `congelar_presentacion(campana, datos: dict) -> dict` versionada y con huella; `renderizar_mensaje(envio, *, previa=False) -> dict` produce asunto, cuerpo, nombre_from, reply_to y pie exactos. Modalidad nueva `portal_codigo` dentro de campaña MiDistri; `enlace_personal` conserva flujo existente. URL general se construye desde origen HTTPS configurado y distribuidora sugerida, nunca desde host/cabecera del navegador.

- [ ] Escribir `test_portal_codigo_no_crea_invitaciones`, `test_url_general_no_expira_ni_contiene_token`, `test_previa_cabecera_cuerpo_replyto_igual_a_transporte`, `test_cambio_config_no_reescribe_confirmada`, `test_cambio_previa_exige_revision`, `test_todos_contactos_bajas_y_limite`, `test_campana_existente_no_cambia_por_instalar`. Afirmar que el botón/link de modo código no llama a invitar_contacto, y que el envío del código sólo lo inicia el portal.
- [ ] Ejecutar RED; implementar campos de sobreescritura, presentación congelada y texto exacto fijo «Portal para realizar pedidos. La distribuidora confirma disponibilidad. Sin pago online». Texto opcional de entrega sólo si el operador lo proporciona. Formulario distingue claramente ambos modos y muestra destino/cabecera/pie antes de confirmar.
- [ ] Reutilizar expansión por contactos de v584 y estados de envío existentes. Conservar validación de contactos antes de SMTP, nunca ampliar una previa antigua sin revisión. Nuevas cabeceras From con alias escapado y dirección SMTP actual; Reply-To configurado/fallback validado. Campañas antiguas sin snapshot mantienen lectura histórica y requieren nueva previa antes de cambios; no migrar su texto ni activar borradores.
- [ ] Ejecutar GREEN y `consignaciones.tests_midistri_campanas_v583`, `tests_midistri_envios_contactos_v584`, `tests_midistri_contactos_v584`, regresiones transporte/campañas relevantes. Transportes siempre mock en tests. Commit U: `feat: preview configurable MiDistri portal campaigns`.

## Task 3: Bandeja ordenada de avisos

**Files U:** crear `midistri_bridge/avisos_consulta.py`, `templates/midistri_bridge/avisos_tabla.xhtml`, `aviso_detalle.xhtml`, `consignaciones/tests_midistri_avisos_consulta_v585.py`; modificar `views.py`, `urls.py`, `templates/midistri_bridge/gestion.xhtml`, `consignaciones/seguridad_rutas.py`. No migración para ocultar/filtrar historia.

**Interfaces:** `consultar_avisos(ctx, filtros: dict, pagina: int=1) -> Page` página de 25 registros, alcance aplicado primero; `detalle_aviso(ctx, aviso_id: int) -> dict` sólo pedido/actor/contactos permitidos, nunca código ni enlace privado. Filtros cerrados: vista pendientes/historial, estado, tipo, desde,hasta,q; rango de fecha local Argentina. GET sólo consulta; acciones existentes siguen POST/CSRF/autorizar.

- [ ] Escribir `test_default_pendientes_y_historial_paginado`, `test_filtros_fechas_y_q_acotados`, `test_detalle_ajeno_403_sin_contactos`, `test_get_no_procesa_ni_resuelve`, `test_incierto_solo_conciliacion_expresa`, `test_historial_no_borra_auditoria`. Filtros inválidos dan explicación, no 500; página vacía mantiene navegación.
- [ ] Ejecutar RED. Implementar tabla accesible con columnas del spec y enlace a detalle, conteos por estado sin duplicar por destinatarios, resultados por destino en detalle y formularios existentes de conciliación. Sacar lista suelta del final de gestión; mostrar resumen y acceso a historia. Mantener solicitud original y enlace al remito existente.
- [ ] Ejecutar GREEN y regresiones de avisos/concurrencia; revisar pantalla en PC/celular con 60 avisos sintéticos. Commit U: `feat: organize MiDistri notice history and delivery states`.

## Handoff

La configuración pública de tarea 1 es consumida por el subplan de galerías. No mandar campaña para validar. Completar pruebas integradas, documentación obligatoria e instaladores D1–D3 del plan principal.
