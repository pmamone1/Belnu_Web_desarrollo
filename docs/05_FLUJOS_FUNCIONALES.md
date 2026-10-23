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
