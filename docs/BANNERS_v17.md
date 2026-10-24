# MiDistri-Pedidos v17 — Fotos del banner

## Guía de uso

1. Las fotos de productos ahora se muestran completas y centradas dentro del banner. No hace falta volver a publicar ni modificar el carrusel existente.
2. La altura que elegiste en Mi tienda > Editor visual se conserva. Las fotos mantienen su proporción: si sobra ancho o alto, queda espacio del fondo en lugar de recortar el producto.
3. Funciona en PC, celular y la vista previa. El título, precio vendedor, PVP y botón conservan su ubicación.
4. Si usás una imagen promocional propia, se conserva el ajuste que elegiste para ese material. Esta corrección protege las fotos asociadas a productos del catálogo.
5. No cambia pedidos, saldos, precios, correos, WhatsApp ni campañas.

## Instalación y operación técnica

Causa observada en el portal público: ajuste-cover y una foto cuadrada1080×1080 dibujada en588×240 con object-fit:cover. El navegador recortaba arriba y abajo. Se reprodujo localmente con plantilla y CSS reales y una foto vertical con bordes marcados.

La plantilla identifica media de producto mediante el objeto s.producto ya validado por bloques_vigentes. Un selector posterior de igual especificidad prevalece sobre cover y aplica object-fit:contain y object-position:center. No altera las dimensiones del banner ni el JSON guardado. Los materiales propios conservan su ajuste anterior. La versión del CSS pasa a17 para evitar caché antigua.

Base admitida: v16, commit a6cf1809e0d4d24f62a2c5053c957796fc279293. Compatible con Urban600 instalado. No se entrega ni instala código Urban. No hay migraciones nuevas, cambios de rutas, permisos, modelos, precios o snapshots; el instalador rechaza migraciones ajenas pendientes. No actualiza venv ni hace envíos.

Rollback: respaldo privado de archivos del instalador y --restore, sólo si no cambiaron después. El formato de página sigue siendo v16, por lo que restaurar esta corrección a16 es compatible y sólo vuelve al comportamiento visual anterior. No restaurar base ni tocar migraciones. Validar primero sin --apply, aplicar y comprobar banner/preview en PC y celular.

## Validación

Ver VALIDACION_v17.md. Instalación productiva pendiente. Sin campaña.
