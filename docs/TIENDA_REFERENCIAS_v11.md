# MiDistri-Pedidos v11 — Mi tienda y referencia de pedidos
Estado: implementación local; instalación productiva pendiente. Requiere Urban Soft591 antes de instalar.

## Guía de uso
1. Entrá como Distribuidor desde Urban Soft y elegí tu tienda. Sólo podés gestionar las distribuidoras autorizadas.
2. Mi tienda > Banners de productos reúne diseño, colores, mensajes y promociones. Los enlaces antiguos dirigen al mismo editor.
3. Elegí Catálogo compacto, Fotos grandes, Promociones o Lista rápida. Los temas claro, nocturno, azul y verde son independientes.
4. Cambiá título, subtítulo, bienvenida, instrucciones, aviso de carrito, mensaje recibido y contacto. Los campos son texto; no ejecutan HTML.
5. Insertar en mi tienda agrega texto, banner, carrusel o video al borrador. Elegí fotos de productos publicados o subí archivos propios privados.
6. Hasta 10 bloques activos y20 elementos por carrusel. Ordená con Subir/Bajar, ocultá, recuperá una copia y editá textos por diapositiva.
7. Para banners rotativos elegí 3–15 segundos (inicial 5), formato horizontal/cuadrado y encajar/cubrir. Hay pausa, navegación y respeto por movimiento reducido. Una foto no muestra flechas.
8. Guardar no publica. Revisar en PC o celular muestra la página privada; Publicar esta versión completa cambia toda la presentación.
9. Si una publicación queda pendiente, reintentala o descartala con motivo para corregir el borrador. Un rechazo definitivo lo libera. Versiones publicadas permite recuperar un borrador, conservando historial.
10. Pedidos e historial muestran la referencia de Urban: fecha y MP-000123. Los precios siguen viniendo de Urban y el total se calcula a precio vendedor.
11. La campaña sigue sin enviarse. No se modifican SMTP, Gmail, catálogo automático ni pedidos históricos al instalar.

## Instalación y operación técnica
Python3.7/Django3.2.15 vigente. Migration0009 añade PaginaTienda/VersionPagina/EdicionPagina y captura presentación/promociones actuales como versión inicial equivalente, con la misma plantilla pública anterior hasta publicar un nuevo diseño. Los borradores no exponen archivos privados; vista previa usa la ruta autenticada existente.
Versiones públicas son snapshots de configuración, nunca de precios actuales. Publicación valida recursos remotos y revisión; registro durable pendiente permite reintentar una respuesta incierta sin duplicar versión. No hay transacción distribuida: Urban puede haber aceptado la autorización de archivos mientras MiDistri conserva página anterior hasta recibir confirmación. Archivos propios previamente aprobados no se borran al ocultar un bloque; permanecen vinculados a su historial. Productos y material retirados se omiten al renderizar tras sincronizar y se rechazan al publicar. Restaurar elimina diapositivas de catálogo ya retiradas antes de guardar el borrador.
Se admiten respuestas API previas sin folio durante instalación coordinada; una referencia recibida no se reemplaza por otra contradictoria ni se borra por respuesta antigua. UUID/rutas/propiedad del pedido siguen vigentes.
No se amplían límites de subida: foto5MiB/20MP, MP4 H.264/AAC16MiB; logo propio usa el mismo circuito privado de imágenes.

## Compatibilidad y rollback
Paquete acumulativo sobre MiDistri8/9/10 revisados. Instalar primero Urban591, después MiDistri11; no mezclar directorios ni paquetes. Sin nuevas variables de entorno; mantener banderas administrativas y multimedia vigentes.
Preflight verifica destinos, hashes y plan exacto antes de copiar. Backup privado de código. Tras0009 aplicada, --restore se bloquea antes de escribir: corrección hacia adelante, sin revertir páginas o pedidos. Antes de migrar, sólo se restaura código verificado y la migración nueva propia no aplicada.
El cambio ajeno templates/accounts/forgotPassword.html está excluido del paquete y commit.
Ver docs/VALIDACION_v11.md y las instrucciones completas de cPanel incluidas en el ZIP.

## Revisión final
Las cuatro observaciones independientes se reprodujeron y corrigieron: rechazo remoto libera borrador, descarte con motivo permite recuperación por otro operador autorizado, banners reinicializan en midistri:render con limpieza de timers/listeners, bandera multimedia conserva ocultamiento, y restore elimina sólo0009 propia nueva verificada y no aplicada. La página inicial conserva el Email visible anterior y normaliza colores antiguos no admitidos a Claro.
