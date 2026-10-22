# MiDistri: catálogo público, preparación parcial y abastecimiento
Fecha: 22/10/2026. Diseño funcional aprobado en este chat; implementación pendiente.

## Objetivo y decisiones del usuario
Facilitar la compra del vendedor y la preparación real de la distribuidora, sin cobrar mercadería no preparada. Compartir con Urban Point la mercadería solicitada, sin datos personales de los vendedores.
- Catálogo público con filtro por categoría, precio vendedor y PVP.
- Pedido calculado al precio vendedor, nunca al PVP.
- Preparación por producto: cantidad entera entre 0 y la solicitada.
- Si se piden 10 y se preparan 6, las otras 4 se cancelan por falta de stock. No quedan pendientes para otra entrega.
- Confirmar genera automáticamente el pedido nativo, cargo y remito sólo por lo preparado.
- Todos los Emails asociados activos y habilitados del vendedor; respetar bajas.
- Excel de abastecimiento para Urban Point. Sin envío automático del informe.
- La campaña d3c5dbbc-6d01-4f89-a017-1bb91d4f74c5 NO se confirma ni se envía durante este trabajo.
- Ejecución solicitada: el agente principal implementa en este chat, con revisión independiente final.

## Bases y límites de la entrega
U = Urban Soft: commit 3d6aedd7e452bcf9370eb4d31748490a2695c2b6, v1.18.583 instalada; próxima entrega v1.18.584.
P = MiDistri: commit dd4478782c4f1e341c6345743a86af289948e35f, v5 instalada; próxima entrega v6.
Raíces productivas y runtimes separados: U /home/mcollini/sistema7000 con Python 3.10; P /home/mcollini/belnuweb con Python 3.7.
U mantiene Django 5.2/PostgreSQL; P mantiene Django 3.2/MariaDB. Sin dependencias nuevas previstas.
Probar con datos ficticios locales. No usar producción como prueba, no tocar venv ni SIB2.
Conservar mejoras v579–v583/v5, incluidas validación Display 0, permisos y aislamiento por distribuidora.
Las 20/65 se agrupan sólo cuando ambas están autorizadas; no ampliar permisos por el número de distribuidora.

## Catálogo y cálculo
Filtrar por nombre y categoría simultáneamente; categorías obtenidas sólo de publicaciones activas de la tienda actual. Opción Todas y Sin categoría. Conservar filtros al paginar y regresar desde el carrito.
Mostrar Precio vendedor y PVP sugerido a cualquier visitante: decisión pública explícita del usuario. Sin identidad de vendedores, LIN, VV o contactos en vistas públicas.
Pedir, ver pedidos y remitos sigue requiriendo acceso personal vigente.
Subtotal = cantidad × precio vendedor; total = suma de subtotales con Decimal y dos decimales. Etiquetar Total al precio vendedor.
En la recepción Urban valida precio contra maestro vigente. Después de recibir, la preparación usa los precios congelados originales: no actualiza por cambios posteriores en Producto.

## Solicitud original y atención final
Solicitud.items y huella conservan íntegramente lo pedido. Añadir Solicitud.preparacion JSON vacío por defecto; sólo se completa en la confirmación final.
Esquema persistido: version=1, cantidades=[{producto_id, cantidad_preparada}], motivo=falta_stock cuando hay recorte, confirmado_por, confirmado_en.
Lista completa, sin SKU duplicado ni producto ajeno; no aceptar bool, fracciones, negativos, más que lo pedido ni precios enviados por navegador.
Sin preparacion guardada:
- recibido/ok = pendiente de preparar;
- emitido histórico = todas las cantidades originales preparadas;
- cancelado histórico = todas canceladas.
La lectura de históricos no escribe ni reconstruye documentos.
Si todas las cantidades son cero, confirmar como cancelación total: cero pedidos nativos, cero cargo, cero remito y un único aviso de cancelación.
Si alguna es positiva, estado técnico emitido conservado; mostrar Preparado parcial o Preparado completo según el detalle. Cantidad cancelada = solicitada − preparada.

## Revisión y emisión
Ambas entradas —Urban nativo y panel Distribuidor de MiDistri— usan un servicio común:
1. revisar cantidades y mostrar solicitado, preparado, cancelado, unitario congelado, subtotales y total;
2. confirmar expresamente la preparación y el cargo sobre una revisión vinculada al actor, conexión, alcance y pedido, válida 15 minutos.
OperacionAdministrativa guarda las cantidades canónicas y la huella; el POST final consume esa revisión, no nuevas cantidades arbitrarias.
Guardar atención, crear Pedido/PedidoProducto/PedidoAsignacion, aplicar saldo nativo y materializar PDF en la misma transacción. Mantener la agrupación por proveedor existente.
Los registros nativos y el PDF contienen únicamente cantidades preparadas. El vendedor puede consultar también lo cancelado por separado.
Bloqueo de Solicitud y vendedor; nunca bloquear joins opcionales. Revalidar permisos financieros, remitos y alcance en backend.
Misma revisión repetida devuelve el resultado ya confirmado; otra revisión obsoleta se rechaza sin duplicar cargos, PDF ni avisos. Si falla el PDF o el saldo, todo revierte.
No inferir disponibilidad física automática: el operador confirma cantidades efectivamente preparadas. No añadir movimientos de stock por intuición.

## Contrato entre aplicaciones
Mantener items originales y los estados técnicos recibido/ok/cancelado/emitido para compatibilidad.
Añadir contrato_pedido=2 y atencion:
{version:1, estado:pendiente|total|parcial|cancelada,
 items:[{producto_id,cantidad_preparada,cantidad_cancelada}],
 total_solicitado:decimal_string,total_preparado:decimal_string}.
Pendiente: preparada=0, cancelada=0, total_preparado=0; las cantidades continúan solicitadas.
Atención final: preparada+cancelada=solicitada por cada producto.
P6 valida estructura y aritmética; un contrato v2 inválido se rechaza, no se interpreta silenciosamente como histórico.
P6 admite respuestas antiguas sin contrato_pedido para instalación escalonada; no ofrece cantidades parciales si Urban no anuncia esa capacidad.
Nueva consulta individual GET order/<uuid> valida conexión, vendedor y distribuidora. P refresca el detalle al abrirlo; no depender de visitar Mis pedidos para corregir un total antiguo.
La API autenticada GET capabilities devuelve {version:1, contrato_pedido:2, preparacion_parcial:true, acceso_por_contacto:true}; U583 no tiene esta ruta y P6 conserva el modo legado ante 405/404. Otros errores de autenticación o contrato no se interpretan como compatibilidad antigua.
operator-order acepta cantidades sólo al revisar; al emitir exige revisión. Respuesta de revisión incluye preparacion_previa, sin cambiar el pedido.
Instalar P6 primero y U584 después. Durante el intervalo P6 funciona con U583 y mantiene preparación completa antigua; activar la parcial sólo cuando U584 anuncie capacidades.

## Remito y Email del pedido
Reutilizar el remito nativo congelado, materialización y cola Aviso existente. Descargar para imprimir y mostrar estado de Email desde la confirmación.
Aviso emitido incluye cantidades preparadas, total real y resumen de cancelados; adjunta el mismo PDF disponible para imprimir. Nunca un segundo documento calculado con maestros actuales.
Se conserva un Aviso por solicitud/tipo; no añadir un segundo envío automático al introducir botones nuevos. Reenvíos explícitos respetan aceptados y conciliación de resultado incierto.
El acceso al remito requiere los permisos y alcance actuales; precio/costo de proveedor no se vuelve público.

## Todos los contactos y enlaces personales
En MiDistri, todos significa principal y adicionales activos con Email habilitado y autorización vigente para la finalidad. Respetar bajas y cambios de contacto.
La preferencia principal de otros circuitos no se cambia. Añadir una opción interna al selector de destinos para que MiDistri solicite todos; los demás consumidores conservan el valor por defecto.
Normalizar y deduplicar por vendedor+Email, no globalmente: dos vendedores con un Email compartido reciben accesos separados.
Campañas nuevas muestran destinatarios y cantidad de Emails tras expandir contactos. Límite 5000 mensajes después de expandir, no 5000 vendedores.
Cambiar la unicidad de acceso de campaña a campaña+vendedor+destino normalizado. Mantener unicidad y comportamiento de promociones.
Cada destino tiene invitación de un uso y 48 h, ligada a vendedor, distribuidora, conexión, contacto/destino y versión del contacto.
Nueva invitación para un destino reemplaza las pendientes de ese destino; no las de otros contactos del mismo vendedor.
Activar una invitación ligada a contacto no revoca accesos de los otros contactos; reemplaza sólo los del mismo destino. Registrar el origen en AccesoVendedor.
Verificar finalidad y vigencia del destino antes de enviar y activar. Al usar el acceso, verificar que el contacto siga activo y con el mismo Email; desactivar el contacto o cambiar ese Email revoca efectivamente ese acceso. Una baja de campañas por sí sola detiene futuros Emails, sin borrar pedidos ni revocar una sesión ya activada. Revocación manual global de vendedor conserva su efecto sobre todos.
Invitaciones/accesos históricos sin destino conservan su semántica anterior. No convertir ni reenviar históricos.
Conservar vínculo del token cifrado al envío exacto y resultado SMTP incierto sin reintento automático.
Migrar no genera invitaciones, accesos, envíos ni confirmaciones de campañas; las vistas previas antiguas deben revisarse de nuevo, nunca ampliarse solas.

## Excel de abastecimiento para Urban Point
Desde pedidos web, consulta por distribuidora, rango de fechas de pedido y estado. Por defecto: 30 fechas locales inclusive: hoy menos 29 días hasta hoy, en Argentina y pendientes recibido/ok.
Columnas agregadas: Distribuidora, SKU histórico, Producto histórico, Solicitadas, Pendientes de preparar, Preparadas, Canceladas por falta de stock.
Agrupar por distribuidora+producto_id+SKU/nombre histórico, evitando fusionar códigos iguales de productos distintos.
Para estados finales, Pendientes de preparar=0. Las unidades canceladas no vuelven a ser un pedido pendiente.
Sin nombres, LIN, VV, Emails ni teléfonos de vendedores; sin costo ni cuenta de proveedor. Se puede compartir el archivo con Urban Point.
No descontar stock supuesto ni generar compras: el informe describe pedidos. Hasta 200 pedidos por consulta/exportación; si excede, pedir acotar filtros, sin truncar silenciosamente.
Respetar alcance y permisos pedidos.gestionar existentes. Auditar exportación sin datos personales.
Conservar Excel para depósito, con detalle vendedor/LIN/VV y orden habitual de línea/orden, limitado a la distribuidora autorizada. Son archivos diferentes.
Sólo descarga Excel en esta entrega; no hay destinatario fijo ni Email automático a Urban Point.

## Migración, recuperación y entrega
U: migraciones aditivas bridge0006_preparacion, bridge0007_contactos_acceso y consignaciones0123_midistri_acceso_destinos. No editar migraciones aplicadas.
P: no se prevén nuevas migraciones; JSON de respuesta ya existente aloja el contrato. Cualquier diferencia detectada se documenta antes de aplicar.
No rellenar preparaciones históricas ni modificar saldos, documentos o filas de campañas existentes en las migraciones.
Tras registrar parciales o accesos por contacto, no volver a código antiguo que los interprete como completos o revoque otros destinos. Recuperación segura: deshabilitar nuevas confirmaciones/accesos y corregir hacia adelante; nunca deshacer economía ni esquema a ciegas. El instalador U bloquea restauración cuando se aplicaron sus targets. El de P bloquea restaurar a v5 si Urban anuncia preparación parcial o si no puede comprobar con seguridad esa capacidad.
Dos commits/PR y ZIP independientes, inventarios explícitos, hashes, instaladores de raíz/runtime exactos y respaldo automático de archivos. No generar un respaldo completo de base por cada release: referencia confirmada 21/10/2026, cuatro instalaciones Urban desde entonces.
Manuales Markdown y PDF principales, reglas, flujos, checklist, pruebas manuales, VERSION y CAMBIOS actualizados en ambas entregas.
No afirmar instalación en producción hasta recibo del usuario y verificación. Ningún Email real durante QA o instalación.
