# MiDistri-Pedidos v8 - Fotos y presentación

Cambios solicitados sobre v7 r2, cuya instalación y sincronización fueron informadas por el usuario. v8 implementada localmente; instalación productiva pendiente. Sólo belnuweb: no requiere actualizar Urban Soft.

## Guía de uso
1. En Apariencia quedan Claro, Nocturno, Azul y Verde, tanto para visitantes como en Mi tienda del Distribuidor. Preferencias retiradas se muestran como Claro; no se borra la configuración guardada.
2. El catálogo encabeza «Elegí los productos para tu Kiosco!». Debajo dice «Portal para realizar pedidos. La distribuidora confirma disponibilidad.»
3. Al abrir Ver mi pedido se muestra la foto de cada producto junto a su nombre, cantidades, precio vendedor y PVP. Tocando la foto se abre ampliada. Si no hay foto disponible, aparece «Foto pendiente».
4. Antes de enviar se informa: «Este pedido queda sujeto a disponibilidad y aceptación por parte de la distribuidora.» El pedido se sigue calculando al precio vendedor.
5. El detalle del pedido recibido también muestra las fotos. El botón se llama «Armar un nuevo pedido» y abre la revisión del nuevo carrito antes de enviarlo. Revisar siempre cantidades y precios allí.

## Implementación y compatibilidad
TEMAS, preferencias del navegador y CSS exponen únicamente cuatro temas. Una preferencia local retirada vuelve a Claro; un tema de tienda retirado usa las variables claras por defecto. No se reescriben Tienda ni sus auditorías; el Distribuidor puede elegir y guardar cualquiera de los cuatro temas.
Las fotos proceden de la Publicacion sincronizada de la misma distribuidora. Se elige la primera foto multimedia cuando la función está habilitada, con respaldo en la lista de imágenes anteriores. No se usan videos como foto ni publicaciones de otra distribuidora.
El carrito ya consulta sus productos en bloque. El detalle agrega una sola consulta de publicaciones por distribuidora/productos y enriquece copias de las filas para presentar la imagen. Puede mostrar la foto todavía disponible de una publicación retirada para facilitar la consulta histórica.
Las fotos del detalle son las actuales del catálogo, no evidencia documental congelada. Nombres, precios, cantidades, preparación y totales del pedido conservan sus snapshots originales; los datos no se modifican para agregar la foto. No se cambia contrato/API, autenticación, permisos, envíos, cargos ni remitos.
Si la foto no existe, aparece un reemplazo textual. Si una URL publicada deja de estar disponible, la reparación corresponde al catálogo y su sincronización; este cambio no descarga ni reescribe archivos originales.

## Instalación y rollback
Base revisada: commit e6453191fff892e8d8d7dfa39c0881c5374ecb2b de MiDistri v7 r2. Sólo /home/mcollini/belnuweb, Python 3.7. Requiere migración existente midistri_portal/0008_recuperacion_promociones. Sin modelos ni migraciones nuevas, nuevas dependencias, variables, cron o sincronización obligatoria.
El instalador verifica hashes antes de copiar, respalda código automáticamente, ejecuta check, makemigrations --check --dry-run, plan vacío, collectstatic y reinicio de belnuweb. No ejecutar sobre sistema7000 ni instalar paquetes Urban para esta entrega.
Rollback sólo de código mediante instalar.py --root /home/mcollini/belnuweb --restore RUTA_RESPALDO. Valida respaldo y archivos antes de detener; mantiene base, medios, pedidos y auditoría. No restaurar base ni revertir migraciones.
Se reutiliza el respaldo de base dentro del intervalo vigente del usuario; no se pide otro completo para estos cambios visuales. No se afirma una instalación por existir ZIP o VERSION.
La campaña permanece sin enviarse. Ver VALIDACION_v8.md y COMANDOS_CPANEL_MIDISTRI_v8.txt.
