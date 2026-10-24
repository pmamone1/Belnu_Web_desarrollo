# MiDistri-Pedidos v16 — Editor visual y pedidos revisados

## Guía de uso

1. Entrá como Distribuidor desde Urban Soft > MiDistri > Configurar MiDistri. Cada tienda tiene sus propios bloques y mensajes.
2. En el Editor visual elegí PC o Celular. Arrastrá bloques/fotos del catálogo o usá los botones Subir/Bajar; seleccioná un banner para ajustar altura, colores, fuente, posición y capas. Alturas iniciales240px/160px; el contenido puede expandirse para no recortar texto.
3. El resultado se ve en el lienzo y se guarda como borrador por AJAX. Guardar no publica. Deshacer/Rehacer afecta sólo el borrador. Si hay un problema de red, usá Guardar/reintentar; si otra pestaña cambió la revisión, descargá tu copia antes de recargar.
4. Podés subir logo/fotos/videos propios; permanecen privados hasta publicar. Durante subida o revisión se bloquea la edición para conservar tus cambios. Ante respuesta de subida perdida, reintentá con el mismo botón.
5. En Diseño y mensajes, configurá Nombre/encabezado de la tienda, título, mensajes y contacto. El saludo conserva nombre, LIN y VV; ya no repite la línea descriptiva. Apariencia queda a la derecha del navbar con cuatro temas.
6. Revisar y publicar comprueba materiales y pide confirmación. Las promociones de margen acompañan el scroll sin tapar la compra; en celular pasan al contenido o se ocultan según elección.
7. En Pedidos web de MiDistri, bajá cantidades o usá×. Escribí motivo y confirmá Guardar cambios y avisar. Las unidades retiradas quedan canceladas; el original se conserva. Este paso no debita ni emite remito; la preparación financiera posterior usa sólo cantidades aceptadas.
8. El aviso al vendedor se encola después del guardado y se intenta por el remitente propio a todos sus Emails habilitados. Revisá estado en Avisos; resultados inciertos requieren conciliación. La instalación no envía mensajes reales.
9. En Mercadería necesaria elegí Faltantes por stock. Descargá el Excel o elegí responsables Urban Point y confirmá el mensaje interno con adjunto. Contiene productos/SKU/cantidades agregadas; no incluye vendedores, LIN, VV o precios, ni cambia stock. Es una solicitud de abastecimiento.
10. El catálogo sólo ofrece activos con foto pública utilizable, precio vendedor y PVP>0. En Urban > MiDistri > Catálogo > Productos excluidos consultá qué falta corregir. Las altas/bajas/cambios conservan la sincronización cada5min; pedidos y documentos históricos no se reescriben.

## Instalación y operación técnica

Editor propio JS/CSS, sin dependencias productivas nuevas. Estilos estructurados validados: colores hex, familias permitidas, tamaños acotados, zonas y capas por porcentajes; sin HTML/CSS/JS arbitrario. Se conserva JSONversion1 con estilo opcional y nuevo mensaje encabezado. Server devuelve JSON privado y aplica el permiso de configuración y tienda puntual también para SuperUsuario; CSRF sigue activo. Preview usa la misma plantilla del sitio en iframe sin scripts. Cambios locales se muestran de inmediato y se renderizan tras pausa; autosave700ms, una solicitud en curso, UUID/payload conservados ante respuesta incierta, conflicto409 sin sobrescritura. Subida conserva huella en EdicionPagina.datos._subida, metadato privado que no entra en la página pública, para reconocer replay antes de repetir el agregado. Revisión/firma de publicación ligada al mismo documento; controles congelados durante validar/subir. Precios/nombres de productos quedan fuera del copy editable.

Urban agrega RevisionPedido en bridge0016, con operaciónUUIDúnica, número por solicitud, actor, motivo, clasificación de stock y cantidades aceptadas. No modifica Solicitud.items, snapshots, precios, saldos o remitos al revisar. Se bloquea la solicitud y se verifica revisión optimista; reducción hasta cero cancela sin cargo. La emisión financiera mantiene su revisión firmada y no puede exceder la cantidad comercial aceptada. Optional revision_comercial en API se valida contra identidad y cantidades originales antes de mostrar al vendedor. Aviso revision_N conserva snapshot del cambio; worker acotado4 se lanza sólo tras commit y con banderas de envío existentes; outbox/conciliación vigentes evitan reenvíos inciertos y permiten fallback por midistri_enviar_avisos. No se envía bajo transacción.

Faltantes suma deltas de revisiones clasificadas como stock y el remanente final no atendido, sin acumular una misma baja dos veces; otras causas no borran faltantes anteriores de stock. Envío interno: vista firmada30min ligada al actor y alcance, selección explícita de responsables Urban Point activos con permiso y alcance, Excel privado y conversación idempotentes. No genera Email SMTP externo al responsable: queda en Mensajes internos y sus avisos existentes. No actualiza inventario. No usar el producto como autoridad de precios históricos.

El filtro de catálogo se aplica en snapshot, recepción de pedidos, portal, carrito, búsqueda/categorías y promociones. Foto utilizable significa derivada pública segura vigente; no se hacen consultasHTTP por cada imagen. Archivos privados o archivados no se exponen. La regla no exige PVP≥precio vendedor. Reporte de exclusiones limitado a2000publicaciones por consulta y búsqueda, con aviso si supera el límite.

## Compatibilidad, migración y recuperación

Urban600 requiere archivos exactos599 y bridge0015; aplica sólo bridge0016, aditiva, sin modificar filas existentes ni migraciones aplicadas. Portal16 requiere archivos15 y portal0009; sin esquema nuevo. Destinos exclusivos sistema7000/Python3.10 y belnuweb/Python3.7; sintaxis de ambos destinos verificada por el constructor de paquetes. No actualizar venv, SMTP, WhatsApp, conexiones ni cron. El instalador valida huellas/plan, respalda archivos y reinicia sólo su aplicación. Instalar Urban600 primero, luego portal16.

No restaurar base ni borrar migraciones. Urban bloquea --restore cuando0016ya está aplicada: usar corrección hacia adelante para no perder límites de revisión. Portal bloquea restauración al runtime15 si hay borradores/versiones con estilos o encabezado16; esos datos deben conservarse. Si no se usó formato nuevo y los archivos no se cambiaron después, el respaldo de código admite --restore. Las versiones previas de página se pueden recuperar al borrador desde el editor anterior y volver a publicar bajo el runtime actual. No se solicita un nuevo respaldo completo fuera del intervalo acordado.

## Validación y estado

Ver VALIDACION_v16.md. La instalación productiva, aceptación HTTPS y correo real quedan pendientes; sólo se probaron datos sintéticos locales. No se ejecuta campaña y no hay modelos/cálculos del club MiDistri-Puntos. Su análisis sigue en documento separado.
