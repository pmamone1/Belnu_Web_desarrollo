# MiDistri-Pedidos v19 — Identidad y catálogo

## Guía de uso

1. Abrí Configurar MiDistri desde Urban Soft. Si la tienda ya está elegida, aguardá el spinner de ingreso: no necesitás pulsar otro botón para entrar. Los permisos y la validación de la cuenta se conservan.
2. En Encabezado y logo cambiá el nombre de la tienda y los textos de los botones Catálogo/Acceso Distribuidor. Su función no cambia. Elegí un logo de comercio (bolsa, carrito, tienda, paquete, ofertas, kiosco) o transporte (camión, furgón, ruta logística), o subí tu imagen propia. El favicon puede usar el mismo logo u otro ícono de la galería.
3. Los cambios se guardan como borrador y se ven en la vista previa. Revisar y publicar muestra progreso con spinner; Publicar esta versión conserva confirmación. Mientras está procesando no se permiten clics repetidos ni cerrar el diálogo. Ante un error podés reintentar sin crear otra publicación.
4. Buscá por nombre, código o categoría: termos encuentra termo; se toleran acentos y errores leves. La cantidad de resultados aparece en letra pequeña. Ordená por nombre, precio vendedor o PVP, de menor a mayor o al revés. Se conservan selección, categoría, búsqueda y orden al cambiar de página.
5. El trofeo y Más vendidos en tu distribuidora usan el ranking por unidades confirmadas y debitadas de todo Urban Soft: consignación y pedidos, no sólo MiDistri. No se muestran cifras comerciales ni datos de otros vendedores. No se cuentan abiertas o anuladas ni se duplican ventas al registrar su cobro.
6. Con stock libre en depósito verás Entrega en24/48hs; sin disponibilidad, Entrega en96hs. Entre1y9 unidades disponibles aparece ¡Últimas unidades! en rojo con letras blancas. Son estimaciones sujetas a aceptación; la página no reserva stock.
7. En el Email de pedido preparado se informa la entrega estimada por producto aceptado. Ese dato queda guardado al confirmar; el correo no lo recalcula según movimientos posteriores.
8. La sincronización de cada5min trae catálogo e indicadores. Si la copia de Urban falta o tiene más de10min, no promete disponibilidad rápida ni inventa ranking. Las tiendas antiguas conservan su presentación pero utilizan el mismo catálogo actualizado.

## Detalle técnico

Encabezado y etiquetas usan mensajes estructurados con límites150/80, escape de texto y rutas fijas. PresetsSVG estáticos del repositorio, sin carga deSVG arbitrarios. presentacion.marca y favicon_marca admiten sólo9 valores de la lista; logo propio sigue el circuito autenticado de subida, revisión y publicación. Preview de logo privado usa ruta autenticada y nunca publica durante el guardado. Borradores/publicaciones previos usan defaults compatibles sin migrar su JSON. Se retira logo duplicado de bienvenida; el cabezal lo muestra una sola vez.

EditorProgreso controla promesa, aria-busy, rolesstatus, botones del diálogo, cancelación y finally; no inventa porcentajes. SSO automático sólo con tienda elegida, preservando POST/CSRF y desafío validado. Ante falta deJavaScript se conserva botón dentro de noscript.

Búsqueda: normalizaciónUnicode sin acentos, raíces plurales sencillas y similitud léxica>=.82 para palabrasde4+letras y diferencia de longitud<=2; todos los tokens deben coincidir dentro del catálogo elegible de la tienda. Orden por allowlist SQL de precio/PVP/nombre, desempate estable. Conteo usa Paginator.count sobre resultados completos.

Publicacion.indicadores JSON (migración0010) conserva copia pública validada: sólo ranking1..10 oNone, entrega24/48 o96, últimas_unidadesbool coherente; rechaza campos privados. No transmite cantidades reales, costos ni datos de vendedores. Rank proviene de Urban602 y no de pedidos locales de MiDistri. Sección destacados y tarjetas comparten precios vigentes vendedor/PVP y sólo productos elegibles. Se conserva el snapshot original de cada pedido y sus precios históricos.

## Compatibilidad, migración y rollback

Paquete acumulativo16/17/18→19, Python3.7/Django3.2, requiere Urban602 primero. Aplica sólo portal0010 sobre0009. No toca cuentas de Email, WhatsApp, sesiones, credenciales, cron registrado ni venv. No envía campañas ni publica borradores durante instalación. El cron existente deUrban añade etapa de cálculo antes de sincronizar; para verlo inmediatamente ejecutar el coordinador ya instalado. Las tablas nuevas son derivadas, no reemplazan registros económicos.

Rollback: conservar esquema aditivo, snapshots, pedidos y documentos. Instalador bloquea restauración ciega tras aplicar0010; preparar corrección hacia adelante o restauración de código revisada manteniendo la columna. No deshacer datos ni reemplazar instalaciones ajenas. Ante error conservar salida y respaldo de archivos. No se confirma instalación por ZIP o marcador.

## Validación

Ver VALIDACION_v19.md y REVISION_FINAL_v19.md. Instalación/aceptaciónHTTPS pendientes. Sin campaña. MiDistri-Puntos sólo análisis.
