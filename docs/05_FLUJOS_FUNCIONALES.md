## MiDistri-Pedidos v13

Acceso único de Distribuidor, menú MiDistri y guía por tienda con remitentes propios; excepción20/65. Pedidos separados y código30min ligado a tienda. Instalación productiva pendiente; campaña sin enviar.

Guía vigente: [GUIA_v13.md](GUIA_v13.md). Esta sección tiene prioridad para los flujos afectados. Mantener permisos y no usar remitentes ajenos.

## MiDistri-Pedidos v12

Banners de ancho completo, fotos más grandes y fundido accesible. Conserva cuatro diseños/temas, la página anterior y la sesión por pestaña. Sin cambios de catálogo, precios ni permisos; producción pendiente.

Guía vigente: [BANNERS_v12.md](BANNERS_v12.md). Validación: [evidencia](VALIDACION_v12.md).

## MiDistri v11 — Tienda con borrador y referencias

Cuatro diseños, mensajes y banners de productos con previa PC/celular y publicación completa. Referencia breve de Urban, conservando UUID y originales. Migración0009 preserva página vigente. Requiere Urban591; instalación productiva pendiente; sin campaña ni cambios SMTP.

Guía: [TIENDA_REFERENCIAS_v11.md](TIENDA_REFERENCIAS_v11.md). Evidencia: [VALIDACION_v11.md](VALIDACION_v11.md).

## MiDistri-Pedidos v10 - Catálogo coordinado

Operación cada cinco minutos con Urban v588: altas autorizadas, cambios y bajas, conservando exclusiones, ocultos y pedidos anteriores. Mantiene sincronizador/API y galería v9; acumulativo v8/v9, sin migraciones nuevas. Instalación v10 y cron productivos pendientes. El video Alma Chocolate141 ya fue publicado/sincronizado para20/65 según confirmación del usuario y lectura del portal23/10/2026. SMTP y campaña sin cambios.

Guía vigente: [CATALOGO_AUTOMATICO_v10.md](CATALOGO_AUTOMATICO_v10.md). Prioridad sobre instrucciones antiguas para este flujo.

## MiDistri-Pedidos v9 - Galería sin controles redundantes

Con un recurso se ocultan flechas y miniaturas; con varios se conserva la navegación de fotos y videos. Sin migraciones nuevas, cambios de permisos, precios o pedidos. Instalación productiva pendiente. El diagnóstico confirmó que el video2 de Alma Chocolate no está publicado para19/68 (20/65); requiere publicación expresa y sincronización, no se resuelve sólo instalando esta versión.

Guía vigente: [GALERIA_v9.md](GALERIA_v9.md). Para el resto del portal se mantiene v8.

## MiDistri-Pedidos v8 - Fotos, textos y cuatro temas

Vigente sobre v7 r2 confirmada por el usuario; instalación v8 pendiente. Apariencia: Claro, Nocturno, Azul y Verde. Catálogo para el Kiosco, texto de disponibilidad simplificado, fotos en carrito y detalle, y botón «Armar un nuevo pedido». Fotos actuales de la misma distribuidora; cantidades y precios históricos intactos. Sin modelos, migraciones nuevas, cargos ni campañas. No requiere actualización Urban Soft.

Guía vigente: [FOTOS_PRESENTACION_v8.md](FOTOS_PRESENTACION_v8.md). Este capítulo prevalece sobre los temas y textos de versiones anteriores.

## MiDistri-Pedidos v7 r2 · Recuperación de instalación

Corrige el error de configuración que detuvo el v7 en Django check. Usar el ZIP r2 completo para retomar el intento; no editar hashes ni settings a mano. Conserva el circuito aprobado. Instalación r2 productiva pendiente; el intento comunicado no llegó a migrar. Ver [recuperación y compatibilidad](RECUPERACION_MIDISTRI_v7_r2.md).

## MiDistri-Pedidos v7 - Acceso con código, galerías y tienda

Vigente revisión final: promociones con revisión privada y confirmación separada; recuperación durable de respuestas perdidas; retiro por fuente vigente; campañas20/65 conservan sus datos propios. Salir reintenta el cierre sin restaurar identidad. Ver guía de esta versión.


Implementación local integrada; instalación productiva pendiente. Código de30min, sesión por pestaña, recuperación del acceso Distribuidor, campañas configurables, avisos con historial, galerías y siete temas/promociones. Conserva precios, preparación parcial, contactos y permisos. Instalar MiDistri7 primero y Urban585 después con funciones nuevas apagadas; activar coordinadamente. La campaña no se envía.

URLgeneral > Email > código > elegir identidad > catálogo/carrito > revisión > pedido > preparación parcial/cargo/PDF. Administrar desde Urban > Mi tienda/Productos > revisar/publicar > sincronizar. Campañas: borrador/vista previa > confirmación explícita; no se confirma al instalar.

Documentación vigente: [ACCESO_TIENDA_v7.md](ACCESO_TIENDA_v7.md). Instrucciones anteriores que siguen son antecedentes y no prevalecen sobre este capítulo.

## Flujo v6

Pedido web recibido > marcar OK > revisar productos/cantidades > confirmar preparación > cargo y PDF sólo de preparados > cola de Email a todos los contactos habilitados. Ver remito para imprimir usa el mismo PDF. Abrir detalle en MiDistri consulta el estado actual; si falla informa última copia. Mercadería necesaria permite exportar agregado a Urban Point; el Excel por vendedor para depósito permanece separado. No hay pago online ni stock reservado por este circuito.

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

# Flujo MiDistri
Urban publica > portal sincroniza > distribuidora invita > vendedor entra por enlace > elige/revisa/envía > depósito recibe Excel > Urban confirma preparado/cargo/remito o cancela por stock.
Ante fallo se conserva el intento para reintentar. Un cambio de precio requiere revisión nuevamente.
