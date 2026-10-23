## MiDistri-Pedidos v7 - Acceso con código, galerías y tienda

Implementación local integrada; instalación productiva pendiente. Código de30min, sesión por pestaña, recuperación del acceso Distribuidor, campañas configurables, avisos con historial, galerías y siete temas/promociones. Conserva precios, preparación parcial, contactos y permisos. Instalar MiDistri7 primero y Urban585 después con funciones nuevas apagadas; activar coordinadamente. La campaña no se envía.

Documentación vigente: [ACCESO_TIENDA_v7.md](docs/ACCESO_TIENDA_v7.md). Instrucciones anteriores que siguen son antecedentes y no prevalecen sobre este capítulo.

## MiDistri-Pedidos v6 · Catálogo y preparación parcial

Candidato, base v5; instalar antes de Urban Soft v584. Categorías y precio vendedor públicos junto al PVP. Carrito personal al precio vendedor; preparación parcial desde el panel con revisión y cancelación automática del resto. Detalle individual actualizado, PDF y Excel para Urban Point. Sin nuevas migraciones ni campaña enviada.
Ver [guía](docs/PEDIDOS_PARCIALES_v6.md) y [validación](docs/VALIDACION_v6.md).

## MiDistri-Pedidos v5 — presentación opcional del catálogo

La sincronización admite Display0 de Urban como presentación no informada.
Se conservan fotos, precios, PVP y permisos. Sin nuevas migraciones ni cambios
en Urban. Después de instalar v5, actualizar la copia del catálogo desde el panel.
Instalación productiva pendiente. Ver [guía v5](docs/DISPLAY_CERO_v5.md).

## MiDistri-Pedidos v4 - Panel de Distribuidor
Instalación pendiente; requiere Urban Soft v583. Entrada desde Urban Soft con
permisos y alcance actuales, sin cuenta staff adicional. Productos y pedidos,
publicación completa con previa y presentación propia por tienda. Precio vendedor
y PVP desde Urban. Migración aditiva0003. Habilitación administrativa explícita;
no publica catálogo ni envía Email al instalar.
Ver [guía vigente](docs/PANEL_DISTRIBUIDOR_v4.md) y [validación](docs/VALIDACION_v4.md).

## MiDistri Pedidos Online v3 - corrección de formularios MiDistri
Corrige el403 CSRF provocado por Referrer-Policy:no-referrer en formularios.
Se usa same-origin: conserva la referencia interna, sin enviarla a otros sitios.
CSRF, autenticación, alcance y permisos se conservan. No hay migraciones,
cambios de importes, datos históricos, claves, venv, cron ni habilitación de envíos.
Instalación productiva pendiente. Requiere MiDistri v2 instalada.
Ver [detalle](docs/CSRF_PORTAL_v3.md) y [validación](docs/VALIDACION_v3.md).

# MiDistri - Pedidos Online v2
Contraparte de Urban Soft v580. Catálogo por distribuidora, precio vendedor y PVP, acceso personal sin registro, pedidos sin pago online.
Base10b49c4 y propuesta2eea423 adaptada. Python3.7/Django3.2, requests existente. Instalación productiva pendiente.
Ver docs/INSTALACION_MIDISTRI_PEDIDOS.md, docs/MANUAL_USUARIO.md y docs/VALIDACION_INTEGRACION.md.
No copiar paquetes, settings ni credenciales Urban a este repositorio.
