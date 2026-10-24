# MiDistri guided configuration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Acceso administrativo claro y guía por distribuidora con remitentes aislados.
**Architecture:** Reutilizar delegación Urban, canales cifrados y permisos; añadir panel de guía, resolución estricta y alcance de código.
**Tech Stack:** Django5.2/Python3.10 Urban; Django3.2/Python3.7 MiDistri; PostgreSQL local para Urban, SQLite local para portal.
**Spec:** docs/superpowers/specs/2026-10-24-midistri-guia-design.md

## Global Constraints
Excepción explícita únicamente20/65. Código30min. No enviar campaña. No producción como prueba. Dos repos/paquetes. Conservar históricos y permisos.

## Review Focus
- Una cuenta con pedidos pero sin configuración no recibe permisos implícitos; explicación y destino correctos (Task2).
- Una conexión con varias tiendas y pestañas paralelas conserva tienda y desafío propios (Task2).
- Compartir un Email entre contactos de distintas tiendas no cambia remitente ni amplía acceso (Task3).
- Responsables locales no pueden editar ni descifrar remitentes ajenos o centrales (Task1).
- Instalación acumulativa y reintento no sustituyen archivos desconocidos ni revierten datos (Task4).

### Task 1: Guía y canales aislados
Files: consignaciones/comunicaciones_remitentes.py, comunicaciones_identidad.py, midistri_bridge/guia.py, guia_views.py, templates/guia.xhtml, urls.py, navbar.py, base.xhtml, seguridad_rutas.py; tests_midistri_guia_v594.py.
Interfaces: exigir_identidad(remitente, distribuidora_id) valida alcance; resumen_guia(ctx,did) devuelve estados sin secretos; vista GET guía y formulario propio GET/POST.
- [ ] Tests: guía sólo alcance privado; cuenta sin conexión ve explicación; responsables locales no POST central/servidor/ajeno; excepción20/65; centralización tercera bloqueada; identidad repetida bloqueada.
- [ ] Ejecutar RED focal nuevo.
- [ ] Implementar resolución, guía y menú conservando pedidos.
- [ ] GREEN focal y tests actuales de configuración/envíos; commit.

### Task 2: Acceso único y editor
Files: Urban operadores_views.py, templates/operador_acceso.xhtml, operadores.py; MiDistri operadores_views.py, templates/base.html, operador_base.html; tests_midistri_acceso_v594.py, test_guia_v13.py.
Interfaces: destino permitido tienda/panel/banners y distribuidora firmados en desafío. POST Urban selecciona sólo conexión y alcance vigentes. Callback fija tienda autorizada y abre editor si tiene permiso.
- [ ] Tests RED para tienda conservada, sin conexión botón ausente, selección ajena403, permisos no ampliados, botón público y configuración distinta de pedidos, dos pestañas, recuperación.
- [ ] Implementar navegación y mensajes; GREEN nuevo + regresión operadores/handoff; commit.

### Task 3: Código ligado a tienda
Files: Urban acceso_codigo*.py, migration0014_desafio_alcance.py, api.py; MiDistri acceso_views.py, template/acceso_codigo.html, client contract; tests_midistri_codigo_tienda_v594.py, test_codigo_tienda_v13.py.
Interfaces: solicitar_codigo(..., distribuidora_id=None) conserva API antigua segura; DesafioIngreso.alcance JSON lista; capability login_codigo_tienda=1; cada fase revalida alcance actual.
- [ ] Tests RED tienda fuera conexión, Email multi-dist, shared20/65, contacto cambiado, legado ambiguo, entrega única remitente seleccionado.
- [ ] Implementar migración aditiva y selector público. No tocar sesiones existentes.
- [ ] GREEN focal + regresión código/contactos; commit.

### Task 4: Entrega y revisión
Files: documentación obligatoria Urban y MiDistri, manualesPDF, scripts/instalar_v594.py y paquete_v594.py; tools/instalar_release_midistri_v13.py y paquete_integracion_v13.py; inventarios y tests.
- [ ] Revisar documentos requeridos y actualizar comportamiento real, compatibilidad, migración, rollback y pruebas manuales.
- [ ] Probar instaladores y paquetes en temporales, sintaxisPython3.10/3.7, Django check y makemigrations --check, pruebas funcionales locales y vistas móvil/escritorio; PDF/unión visual.
- [ ] Revisión independiente completa; una pasada de correcciones con RED/GREEN y suite relevante.
- [ ] Commits/push/PR separados, construir ZIP contra commits finales, verificar bytes e inventario, guardar enDownloads y entregar comandos completos. No afirmar instalación productiva.
