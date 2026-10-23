# MiDistri: galerías y presentación — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. El principal implementa en este chat; revisión final conjunta.

**Goal:** Mostrar fotos ampliadas y videos de productos, y permitir al distribuidor configurar temas y promociones de su tienda.

**Architecture:** Urban exporta exclusivamente multimedia expresamente publicable de productos/tiendas autorizados, preservando originales privados. MiDistri sincroniza metadatos tipados y representa visor, temas y promociones; subidas de promoción se validan en Urban reutilizando sus validadores y su runtime Python3.10.

**Tech Stack:** Django, Pillow y validadores MP4 existentes de Urban; JavaScript accesible, HTML5 video/Range, HTTPS, modelos aditivos P/U.

**Spec:** `docs/superpowers/specs/2026-10-22-midistri-acceso-codigo-y-tienda-design.md`, apartados F–H. Plan principal y configuración pública del subplan de comunicaciones.

## Global Constraints

- No publicar material privado automáticamente al instalar. Productos y recursos deben estar activos y publicados para la distribuidora.
- Hasta 20 fotos y 10 videos por producto; principal primero, resto por orden; hasta diez bloques promocionales activos por tienda.
- Fotos JPG/PNG/WebP hasta 5 MiB/20 megapíxeles; MP4 H.264/AAC hasta 16 MiB. Reutilizar validación real, no sólo extensión.
- Siete temas: claro, nocturno, azul, verde, terracota, violeta pastel, ámbar pastel; controles grandes, contraste legible y sin autoplay.
- Los precios siguen viniendo de Urban: precio vendedor y PVP (precio al público); importes del pedido al precio vendedor.
- No incluir originales, copias publicables ni medios promocionales en ZIP/GitHub. No instalar dependencias en venv productivo desde instalador.

## Review Focus

1. Un MP4 existente es privado: su ID/ruta no puede hacerlo público sin publicación revisada (tarea 1).
2. Retirar producto/medio durante reproducción, Range inválido y referencia de otra distribuidora (tareas 1–2).
3. URL externa/redirección, SVG, archivo truncado o sobredimensionado: no SSRF ni contenido activo (tareas 2–4).
4. Galería con un recurso, sin foto, video caído o JavaScript desactivado: mantener catálogo usable (tarea 3).
5. Guardado concurrente y cambio entre tiendas/temas: no sobrescribir contenido ni preferencia ajena (tarea 4).

---

## Task 1: Publicación multimedia explícita en Urban

**Files U:** crear `midistri_bridge/multimedia.py`, `multimedia_views.py`, `multimedia_models.py`, `consignaciones/tests_midistri_multimedia_v585.py`; modificar `models.py`, `services.py`, `administracion.py`, `operadores_api.py`, `urls.py` y revisión de publicación `templates/midistri_bridge/catalogo_masivo.xhtml`. Migración bridge aditiva después de configuración.

**Interfaces:** `preparar_material(usuario, publicacion_id: int, video_ids: list[int], *, ctx=None) -> dict` genera revisión de material/huella; `confirmar_material(usuario, revision_id: str, *, ctx=None) -> dict` vuelve a autorizar y crea/reutiliza copias por hash. `multimedia_publica(conexion, publicacion) -> list[dict]` devuelve `{id,tipo,url,descripcion,orden,principal}`; tipos foto/mp4/youtube/vimeo; máximo 20/10. Modelo `MaterialPublicable`: UUID, publicación/distribuidora, origen video/foto si corresponde, tipo, ruta privada de copia, hash,tamaño,activo/revisión. No exponer ruta privada en serializer.

- [ ] Escribir `test_mp4_privado_no_sale_sin_revision`, `test_confirmar_material_idempotente_y_auditable`, `test_principal_orden_y_limites`, `test_producto_retirado_o_dist_ajena_no_sirve`, `test_hash_copia_cambiado_rechaza`, `test_range_unico_206_y_rango_invalido_416`. Afirmar que instalar/snapshot no crea copias ni activa publicación.
- [ ] Ejecutar RED. Usar `producto_videos_archivo.leer_video` y validadores existentes, sin modificar original ni media alias. Endpoint público `/midistri-media/<uuid>/` sirve sólo copias con publicación/medio/origen activos, GET/HEAD, hash/tamaño correctos y Range simple acotado; no seguir symlinks. Respuestas no indexables, nosniff, sin credenciales ni caché pública persistente que impida retirar material. URL no contiene ruta, Email ni token de sesión.
- [ ] Implementar revisión visible de selección de videos en panel/catalogo; copias sólo al confirmar una selección autorizada. Snapshot incluye multimedia opcional y mantiene `imagenes` para P6. Validar dos distribuidoras con distinta selección y copia no autorizada por coincidencia de hash.
- [ ] Ejecutar GREEN, tests de producto videos/imágenes y permisos; commit U: `feat: publish reviewed MiDistri product media safely`.

## Task 2: Sincronización tipada y almacenamiento P

**Files P:** crear `midistri_portal/multimedia_contract.py`, `test_multimedia_v7.py`; modificar `models.py`, `services.py`, `tests.py`, `test_display_cero.py`. Migración portal aditiva después de SesionVendedorPortal: nuevo JSONField multimedia en Publicacion, default lista vacía.

**Interfaces:** `validar_multimedia(items: list, origen_urban: str) -> list[dict]` valida enum, campos/longitudes, orden y rutas; únicamente HTTPS mismo origen y `/catalogo-imagenes/` para fotos o `/midistri-media/UUID/` para MP4, YouTube/Vimeo según validador existente de origen. `validar_snapshot` mantiene transacción total y metadatos anteriores ante rechazo; ausencia de multimedia conserva comportamiento de fotos v6.

- [ ] Escribir `test_snapshot_legacy_fotos_funciona`, `test_multimedia_tipada_limites_y_deduplicacion`, `test_url_privada_host_ajeno_redirect_y_javascript_rechaza`, `test_snapshot_invalido_no_vacia_catalogo`. Verificar URLs relativas, puertos, credenciales, fragmentos/query no admitidos y tipos bool/int según contrato.
- [ ] Ejecutar RED. Implementar validación sin solicitudes de red a URLs recibidas; guardar solamente metadatos de recursos publicables. Agregar capacidades multimedia versionadas sin cambiar interpretación de precios/identidades. Flag P `MIDISTRI_MULTIMEDIA_ENABLED=False`; con Urban antiguo/flag apagada se conservan fotos y catálogo.
- [ ] Ejecutar GREEN, sincronización v6 y sintaxis Python3.7; commit P: `feat: synchronize typed storefront media`.

## Task 3: Visor ampliado y reproductor

**Files P:** crear `templates/midistri_portal/galeria.html`, `static/midistri_portal/galeria.js`, `static/midistri_portal/galeria.css`, `test_galeria_v7.py`; modificar `templates/midistri_portal/catalogo.html`, `base.html`, `views.py` sólo para contexto requerido.

**Interfaces:** `abrirGaleria(productoId, indice=0)`, `cerrarGaleria()` en módulo JS; datos por `json_script` escapado, nunca interpolación HTML. Fotos/miniaturas usan URL validada; videos MP4 HTML5 controls/preload=metadata y sin autoplay. Enlaces externos seguros con noopener y sin descargas servidor. Sin JS, foto enlaza a recurso público y resto del material se consulta en details, sin afectar ingreso por código.

- [ ] Escribir `test_card_tiene_galeria_y_precios_correctos`, `test_json_script_escapa_titulos`, `test_sin_js_muestra_material_publico` y prueba browser: tocar principal, avanzar, reproducir, Escape, foco devuelto, no audio automático, scroll/filtros/carrito conservados. Incluir producto sin foto/con video único y recurso 404.
- [ ] Ejecutar RED. Implementar dialog accesible con alternativa compatible, controles anterior/siguiente, miniaturas y contador; usar carga diferida al abrir. Mantener imagen principal de card y mostrar indicador de cantidad/fotos/videos. No abrir modal al tocar cantidad/agregar pedido.
- [ ] Ejecutar GREEN y validación visual local celular/PC/teclado; commit P: `feat: add accessible product photo and video gallery`.

## Task 4: Temas y material promocional por tienda

**Files U:** crear `midistri_bridge/promociones.py`, `consignaciones/tests_midistri_promociones_v585.py`; modificar multimedia_models, operadores_api/api para upload autenticado acotado. **Files P:** crear `midistri_portal/promociones.py`, `test_promociones_v7.py`, `static/midistri_portal/temas.css`, `promociones.js`, template `operador_promociones.html`; modificar `models.py`, `presentacion.py`, `operadores_views.py`, `urls.py`, `client.py`, `templates/midistri_portal/operador_tienda.html`, `catalogo.html`, `base.html`. Migraciones aditivas de Tienda.tema y BloquePromocional.

**Interfaces:** P `TemaTienda` enum con siete claves del spec; `guardar_promocion(perfil, tienda_id: int, datos: dict, revision: int, operacion_id: str, token: str) -> BloquePromocional`; fields título,texto,enlace,tipo,material_id/url,orden,activo,revision. U `subir_promocion(operador, distribuidora_id: int, archivo, operacion_id: str) -> dict` usa permiso `midistri.tienda_configurar` y material de tienda distinto del producto. P `subir_material_tienda(archivo, distribuidora_id: int, operator_token: str, operacion_id: str) -> dict` forward multipart acotado sólo al endpoint fijo Urban; ni destino ni ruta los decide el cliente.

- [ ] Escribir `test_siete_temas_y_preferencia_por_tienda`, `test_promocion_dist_ajena_o_permiso_revocado_rechaza`, `test_maximo_diez_y_revision_obsoleta`, `test_upload_falso_svg_truncado_y_limites`, `test_reintento_upload_no_duplica_archivo`, `test_archivar_retira_recurso_y_no_borra_auditoria`, `test_markup_escapado_enlaces_sin_ssrf`.
- [ ] Ejecutar RED. Implementar subida desde P hacia Urban con stream/cota 16 MiB más margen fijo de multipart, comprobando extensión y contenido en Urban; no usar JSON/base64 para archivos ni aumentar el límite global de API de 1 MiB. El dispatch de upload valida aplicación/operador/cupo antes de procesar archivo, limita memoria/temporales y limpia huérfanos en fallo. Urban usa validadores MP4 v579 y Pillow existentes; no requiere nuevas dependencias de video en P3.7. Fotos se recodifican; sólo material validado y activado se sirve por endpoint dedicado.
- [ ] Implementar configuración de tema, vista previa y bloques ordenables/archivables; permiso vigente y auditoría local más confirmación Urban. Nombre comercial/Email de respuesta provienen de configuración Urban del subplan comunicaciones; no mantener dos autoridades. Revisiones/UUID protegen reintentos y concurrencia. Preferencia del visitante por tienda guarda sólo clave de tema, no identidad.
- [ ] Ejecutar GREEN y regresiones presentación/logo/configuración. Revisar contraste, carrusel manual, teclado y pantallas angostas para cada tema. Confirmar que cambiar tienda no mezcla promociones ni preferencias y que un bloque archivado no sigue público.
- [ ] Commit U/P: `feat: configure distributor themes and promotional media`.

## Handoff

No publicar productos, seleccionar videos ni activar promociones reales para probar. Migraciones/paquetes/documentación y revisión final corresponden a D1–D3 del plan principal. Registrar límites efectivos de cPanel/upload y validar instalación mixta con flags apagadas antes de recomendar activación.
