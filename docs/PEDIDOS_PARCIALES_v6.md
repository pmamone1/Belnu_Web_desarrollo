# MiDistri-Pedidos v6 · Catálogo y pedidos parciales

Estado: código candidato de actualización. Instalación productiva pendiente.
Base Urban Soft v583 (3d6aedd7e452bcf9370eb4d31748490a2695c2b6). Contraparte MiDistri v6, base v5.
Instalar **MiDistri v6 primero**, después Urban Soft v584. Repositorios, paquetes y entornos separados.

## Uso
Catálogo: categoría y búsqueda combinables; Precio vendedor y PVP públicos. Los pedidos requieren acceso personal y se calculan con precio vendedor.
Preparación: revisar cada producto, incluir o no y cantidades enteras de cero a lo solicitado. Los precios originales no se editan. Confirmar genera sólo unidades preparadas, cargo y remito congelado; el resto queda cancelado por falta de stock, sin pendiente.
Contactos: una invitación independiente por destino Email habilitado de cada vendedor, respetando bajas. Dos contactos pueden mantener sesiones simultáneas. Los avisos operativos usan todos los contactos habilitados y el mismo PDF; SMTP aceptado no equivale a entrega final.
Abastecimiento: Excel agregado por distribuidora, producto y SKU/nombre históricos, con solicitadas, pendientes, preparadas y canceladas. Sin identidad de vendedor, contactos ni costo. Hasta 200 pedidos por rango; no trunca, no cruza stock ni crea compras.
Seguridad: backend conserva permisos actuales y alcance privado; 20 incluye 65 sólo si ambas están autorizadas. No cambia claves, habilitaciones, cron, venv ni sistemas ajenos.

1. Salidas / Anuncios > Pedidos > Pedidos web de MiDistri. Revisar pedido y marcar OK.
2. Confirmar preparación abre la pantalla de cantidades; no cobra al abrirla. Desmarcar productos o poner cero si no hay stock.
3. Revisar cantidades e importe. Si pide 10 y se preparan 6 a $25.000, se cobra $150.000 y se cancelan 4.
4. Confirmar la revisión dentro de 15 minutos. Un cambio del pedido exige revisar nuevamente. Cero preparado cancela todo sin cargo ni remito.
5. Abrir remito para imprimir. La cola MiDistri envía el mismo PDF cuando las habilitaciones y remitentes están configurados. Consultar el estado antes de reenviar; un resultado incierto requiere conciliación.
6. Mercadería necesaria > fechas y estado > Excel para Urban Point. El Excel de depósito por vendedor permanece disponible por separado.

## Modelo, documentos y compatibilidad
Nuevas migraciones: midistri_bridge0006_preparacion y0007_contactos_acceso; consignaciones0123_midistri_acceso_destinos.
Son aditivas salvo sustitución de restricción de acceso de campaña: antes campaña+vendedor; ahora campaña+vendedor+Lower(destino).
La petición original Solicitud.items permanece intacta. Solicitud.preparacion conserva versión, cantidades, actor, instante y motivo.
Se conservan precios históricos; Pedido, asignaciones, cargo y PDF contienen sólo cantidades preparadas. Todo se confirma en una transacción con locks y revisión consumible una sola vez.
Históricos emitidos sin preparación se interpretan como entrega completa; cancelados como cero preparado. No se regeneran documentos históricos.
Invitacion liga destino normalizado, contacto/version; AccesoVendedor enlaza su invitación. Las sesiones antiguas sin origen siguen con su comportamiento anterior.
Renovar un destino no revoca otro. Cambiar/desactivar un contacto invalida su acceso; la baja de campañas impide nuevas invitaciones, no revoca por sí sola una sesión ya activa.
Las previas antiguas de campañas de acceso requieren nueva revisión; no se amplían destinatarios ni se envía la campaña existente al instalar.

## Contrato API
Respuestas originales conservadas, añadiendo contrato_pedido=2 y atencion(version1, estado, items por producto con cantidad_preparada/cantidad_cancelada, total_solicitado y total_preparado).
Precio × cantidad se valida con Decimal; los totales se calculan con precio vendedor congelado. email_estado no expone destinos.
GET capabilities autenticado anuncia contrato2, preparacion_parcial y acceso_por_contacto. GET order/UUID requiere sesión del vendedor propio y conexión.
POST operator-order con revisar_preparacion recibe lista completa producto_id/cantidad_preparada; emitir sólo revisión y confirmación, sin cantidades editadas.
POST operator-order-supply devuelve XLSX del alcance delegado. Fechas inclusivas de Argentina; defecto hoy-29/hoy. Estado pendientes incluye recibido+ok. Cancelado por falta de stock no vuelve a pendientes.
P6 sólo acepta modo anterior si capabilities devuelve404/405; errores de autenticación, red o respuesta v2 malformada no permiten degradación silenciosa.

## Instalación y recuperación
El instalador MiDistri verifica raíz belnuweb, Python3.7 y prefix exactos, hashes de base v5/paquete y plan de migración vacío. No instala dependencias ni migra Urban. Las tres migraciones anteriores pertenecen exclusivamente al paquete Urban Soft.
Hace copia privada de código antes de reemplazar, detiene sólo belnuweb, ejecuta check, makemigrations --check, comprueba plan vacío, collectstatic y reinicia.
Una reinstalación idéntica es válida; archivos diferentes se rechazan antes de copiar.
La restauración del código anterior se bloquea si cualquiera de estas migraciones está aplicada. Deshabilitar administración si hay incidencia y corregir hacia adelante; no revertir datos o documentos.
MiDistri v6 no debe volver a v5 cuando Urban expone contrato nuevo o no puede comprobarse. El instalador de MiDistri también protege ese caso.
Se conserva respaldo completo existente del21/10/2026; no se solicita otro por esta actualización. Confirmaciones de instalaciones se registran al recibir salida, nunca desde un marcador documental.

## Validación y límites
Ver VALIDACION_v6.md y checklist. Se usan exclusivamente bases y datos sintéticos locales.
No se certifica instalación en producción, entrega SMTP real ni ejecución en los runtimes de cPanel hasta recibir el resultado del usuario.
La campaña existente permanece en borrador y no se confirma con esta entrega.
