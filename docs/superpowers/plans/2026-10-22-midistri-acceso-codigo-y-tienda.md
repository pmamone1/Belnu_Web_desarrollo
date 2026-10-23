# MiDistri: acceso con código y tienda — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Método elegido por el usuario: el agente principal implementa en este chat; revisión independiente final.

**Goal:** Entregar ingreso por Email/código de 30 minutos, sesión por pestaña, campañas configurables, historial ordenado y portal con galerías y presentación por distribuidora.

**Architecture:** Urban conserva identidad, permisos, precios, comunicaciones y documentos. MiDistri implementa experiencia de acceso, sesión por pestaña y presentación, con contratos privados versionados entre servidores. Los tres subplanes mantienen límites propios y se entregan en dos paquetes separados.

**Tech Stack:** Urban Python3.10/Django5.2/PostgreSQL; MiDistri Python3.7/Django3.2/MariaDB; JavaScript progresivo, sessionStorage, SMTP existente, validadores de imágenes/video compatibles.

**Spec:** `docs/superpowers/specs/2026-10-22-midistri-acceso-codigo-y-tienda-design.md`.

## Global Constraints

- Código válido exactamente 1800 segundos desde su emisión; un uso, cinco errores, reenvío mínimo 60 segundos.
- No cerrar la sesión al vencer el código ni por la regla heredada de una hora. Salir revoca; no prometer detección infalible de cierre/restauración de pestañas.
- No enviar todavía la campaña existente ni invitaciones nuevas. Ninguna prueba usa destinatarios reales.
- Repositorios, claves, runtimes y paquetes independientes; no cambiar venv, SIB2, stock, cargos o históricos por este trabajo.
- Mantener permisos y alcance privado. La agrupación 20/65 sólo opera dentro de las autorizaciones de la conexión y del usuario.
- Base mínima U584/P6 validada por archivos y esquema. Candidatos U585/P7 pendientes de implementación; no afirmar instalación por un marcador.

## Review Focus

1. Cierre/restauración de pestaña frente a una cookie todavía válida: sin filtración de identidad ni falsa garantía de revocación (Acceso, tareas 3–4).
2. Un Email compartido entre vendedores y un contacto cambiado tras verificar código: elección limitada y revalidación al consumir ticket (Acceso, tareas 1–2).
3. Acceso administrativo que funciona para el agente pero falla al usuario: evidencia por rama, dos pestañas y recuperación sin aceptar origen ajeno (Acceso, tarea 0).
4. Material privado o retirado, Range y una URL maliciosa: ningún bypass del permiso de publicación (Galerías, tareas 1–2).
5. Campaña aprobada con datos viejos y SMTP incierto: vista previa congelada, sin ampliar audiencia ni reenviar (Comunicaciones, tareas 1–3).

---

## Repositorios y archivos compartidos

`U` significa raíz Urban; `P`, raíz MiDistri. Cada spec/plan se guarda idéntico en los dos repositorios. Las rutas de código de los subplanes siempre indican U/P; no copiar modelos ni migraciones del otro proyecto.

- U: `C:/Users/pmamo/.codex/worktrees/urban-ayuda-curso-v556/repo-v496`, base `0c8fb003a03fc9383da0f7b2df160111b0b7fae1`.
- P: `C:/Users/pmamo/.codex/worktrees/midistri-pedidos-integracion`, base `6734ce86aced5cc199fd8320231eaffb80774c72`.
- Preservar el cambio ajeno P `templates/accounts/forgotPassword.html`, archivos de pruebas locales y entregas anteriores. No usar `git add .`, limpieza recursiva ni amend de releases anteriores.
- Ramas propuestas: U `codex/midistri-acceso-codigo-v585`; P `codex/midistri-acceso-codigo-v7`.

## Orden de ejecución

1. [Acceso y corrección administrativa](2026-10-22-midistri-acceso-codigo.md): tarea 0 primero; después OTP y sesión por pestaña. Produce identidad y configuración compatibles, sin activar producción.
2. [Comunicaciones](2026-10-22-midistri-comunicaciones-configurables.md): configuración central, campaña de URL general e historial. No envía campaña.
3. [Galerías y presentación](2026-10-22-midistri-galeria-tienda.md): contrato multimedia, visor y promociones/temas, reutilizando configuración pública de comunicaciones.
4. Validación integral, revisión independiente y entrega descritas debajo.

## Task D1: Integración local de las dos aplicaciones

**Files:** crear U `consignaciones/tests_midistri_flujo_v585.py`, P `midistri_portal/test_flujo_v7.py`; modificar fixtures locales dentro de `tmp/`, fuera de paquetes.

**Interfaces:** consume contratos y servicios de los tres subplanes; produce evidencia con tiempos, resultados y límites reales, sin secretos.

- [ ] Escribir casos integrados: código emitido a contacto sintético, selección entre dos vendedores, pedido 10+2, preparar 6+0, cargo $150.000, PDF único, dos Email habilitados y campaña en borrador sin envíos. Afirmar importes al precio vendedor, PVP sólo informativo.
- [ ] Ejecutar tests nuevos antes de completar el ensamblado; registrar el fallo concreto. No aceptar un test que pase porque usa exclusivamente mocks del contrato que pretende probar.
- [ ] Ensamblar localmente ambas aplicaciones sobre bases sintéticas; transporte SMTP simulado y URLs locales permitidas sólo en configuración de prueba, nunca en código productivo.
- [ ] Ejecutar test nuevo y regresiones focales; usar PostgreSQL real para concurrencia/locks y MariaDB local para migraciones y longitudes. Comprobar sintaxis Python3.7 P y Python3.10 U. Si falta un runtime/servicio, registrar qué no se ejecutó y resolverlo antes de anunciar compatibilidad probada.
- [ ] Revisar celular/PC: código y error claro, recarga, más de 30 minutos simulados, Salir, galería, video, filtros, historial y los siete temas. Guardar capturas con datos sintéticos y comprobar ausencia de secretos en HTML, logs, URL y almacenamiento del navegador.
- [ ] Commit por repositorio: `test: verify MiDistri code login and storefront flow`.

## Task D2: Documentación, instaladores y ZIP separados

**Files U:** `scripts/instalar_v585.py`, `scripts/test_instalar_v585.py`, `scripts/paquete_v585.py`, `scripts/release_files_v585.json`, `scripts/actualizar_manual_v585.py`, `COMANDOS_CPANEL_v1_18_585.txt`, `CAMBIOS_v1_18_585_midistri_acceso_tienda.txt`, `docs/MIDISTRI_ACCESO_TIENDA_v585.md`, `docs/VALIDACION_v585.md`, `docs/REVISION_FINAL_v585.md`, `Manual_Urban_Soft.pdf`.

**Files P:** `tools/instalar_release_midistri_v7.py`, `tools/test_instalar_release_midistri_v7.py`, `tools/paquete_integracion_v7.py`, `tools/release_files_v7.json`, `tools/actualizar_manual_v7.py`, `COMANDOS_CPANEL_MIDISTRI_v7.txt`, `CAMBIOS_v7_acceso_tienda.txt`, `docs/ACCESO_TIENDA_v7.md`, `docs/VALIDACION_v7.md`, `docs/REVISION_FINAL_v7.md`, `Manual_MiDistri_Pedidos_Online.pdf`.

**Files ambos:** README, HANDOFF, VERSION_DOCUMENTADA, docs/00_INDICE,04_REGLAS_DE_NEGOCIO,05_FLUJOS_FUNCIONALES,17_CHECKLIST_ENTREGA,19_PRUEBAS_MANUALES_CRITICAS,MANUAL_USUARIO. El documento de planificación no constituye una release.

**Interfaces:** consume hojas de migración y manifiestos exactos de tareas previas; produce ZIP+SHA e instaladores que distinguen comprobación, instalación y activación funcional.

- [ ] Escribir tests de instalador: raíz/runtime ajenos, hash diferente, migración desconocida, dependencia de video ausente, base parcial, reintento, rollback y funciones nuevas apagadas; afirmar cero modificaciones en preflight.
- [ ] Ejecutar RED; derivar instaladores de U584/P6 conservando comprobaciones/backup privado y planificación por hojas, sin permitir migraciones inversas ni editar aplicadas.
- [ ] Implementar y ejecutar GREEN. P7 primero con flags apagadas; U585 después. No activar Email/login/multimedia automáticamente ni alterar destinatarios/productos en instalación.
- [ ] Actualizar manuales con comportamiento integrado, migración, compatibilidad, límites de pestaña y rollback; anteponer capítulo a PDF principal y verificar visualmente la página de unión. No copiar PDF adicional a Downloads.
- [ ] Construir `urban_soft_v1_18_585_midistri_acceso_tienda.zip` y `midistri_pedidos_v7_acceso_tienda.zip`; verificar CRC, inventario y hashes contra commit. Excluir bases, claves, sesión/OTP, media, venv, tmp, copias de respaldo y cambio ajeno. Guardar ambos ZIP+SHA en Downloads tras aprobación de archivos si el entorno la requiere.
- [ ] Registrar backup existente y sólo instalaciones realmente confirmadas. No solicitar otro backup completo por este paquete si no se cumple la frecuencia 30 instalaciones/15 días.
- [ ] Commit por repositorio: `release: package MiDistri code login and storefront`.

## Task D3: Revisión final y publicación

**Files:** documentos `REVISION_FINAL` y `VALIDACION` de D2, cuerpo de cada PR, manifiestos finales.

**Interfaces:** consume evidencias de D1/D2 y los tres subplanes; produce dos commits publicados, dos PRs independientes y comandos cPanel completos en el chat.

- [ ] Usar `superpowers:verification-before-completion` y después `superpowers:requesting-code-review`. El principal implementa; un revisor independiente revisa el cambio completo y alcance, con prioridad en Review Focus. No desplegar ni enviar campaña para «probar».
- [ ] Resolver hallazgos con reproducción y pruebas. Registrar fallos históricos de suite Urban frente a base; no usar una lista verde de tests focales para afirmar suite total verde.
- [ ] Auditar diff e inventario explícitos, repetir sólo pruebas afectadas por correcciones y reconstruir ZIP si cambió payload; registrar SHA finales.
- [ ] Publicar commits y crear/actualizar PR separado en cada GitHub, adjuntarlos al chat y conservarlos sin merge automático.
- [ ] Entregar enlaces locales a los dos ZIP, SHA, commits reales y comandos cPanel completos P7/U585. Distinguir publicado, instalado y activado. Ofrecer manual actualizado como enlace opcional. **La campaña sigue sin enviarse.**

## Estado y autorización

Este plan está preparado para revisión, no ejecutado. El usuario ya eligió implementación en este chat con revisión final; no volver a preguntarle método ni autorización de envío de campaña. Tras su revisión del plan, ejecutar tarea 0 de Acceso primero y continuar en el orden anterior.
