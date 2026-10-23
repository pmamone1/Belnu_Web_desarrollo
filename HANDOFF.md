## MiDistri-Pedidos v7 r2 · Recuperación de instalación

Corrige el error de configuración que detuvo el v7 en Django check. Usar el ZIP r2 completo para retomar el intento; no editar hashes ni settings a mano. Conserva el circuito aprobado. Instalación r2 productiva pendiente; el intento comunicado no llegó a migrar. Ver [recuperación y compatibilidad](docs/RECUPERACION_MIDISTRI_v7_r2.md).

## MiDistri-Pedidos v7 - Acceso con código, galerías y tienda

Vigente revisión final: promociones con revisión privada y confirmación separada; recuperación durable de respuestas perdidas; retiro por fuente vigente; campañas20/65 conservan sus datos propios. Salir reintenta el cierre sin restaurar identidad. Ver guía de esta versión.


Implementación local integrada; instalación productiva pendiente. Código de30min, sesión por pestaña, recuperación del acceso Distribuidor, campañas configurables, avisos con historial, galerías y siete temas/promociones. Conserva precios, preparación parcial, contactos y permisos. Instalar MiDistri7 primero y Urban585 después con funciones nuevas apagadas; activar coordinadamente. La campaña no se envía.

Documentación vigente: [ACCESO_TIENDA_v7.md](docs/ACCESO_TIENDA_v7.md). Instrucciones anteriores que siguen son antecedentes y no prevalecen sobre este capítulo.

## Entrega MiDistri v6 · 22/10/2026

Instalación productiva pendiente. Base v5; instalar P6 antes de U584. Sin migraciones MiDistri nuevas. Runtimes separados: belnuweb Python3.7; Urban Python3.10. No enviar campaña. Conservar templates/accounts/forgotPassword.html ajeno a esta entrega; no incluirlo. Restauración a v5 bloqueada si Urban anuncia contrato nuevo o no puede comprobarse. [Guía](docs/PEDIDOS_PARCIALES_v6.md) y [validación](docs/VALIDACION_v6.md).

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

# Handoff MiDistri v2
Destino exclusivo belnuweb/Python3.7. Base confirmada10b49c4. Propuesta previaPR2 conservada y endurecida con validación de respuesta/propietario/PDF y LIN/VV.
Datos/base/store anteriores intactos; migra sólo midistri_portal0001–0002. No hay instalación ni envíos productivos.
