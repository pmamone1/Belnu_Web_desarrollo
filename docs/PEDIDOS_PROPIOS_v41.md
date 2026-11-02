# MiDistri-Pedidos v41 - Pedidos propios

## Guía de uso

### Consultar el pedido
En Mis pedidos, desplegá la fila o abrí el pedido completo. Los pedidos consignados propios muestran su plazo informado y Fecha de débito. La fecha viene de la distribuidora y puede estar configurada; el portal no la calcula a partir del día del pedido. Las distribuidoras 20/65 usan 14 días según su configuración vigente; otras configuraciones admiten 7/14/21/30 días.

### Devolución por producto
Cada producto informado identifica Admite devolución o No admite devolución. Un pedido puede combinar ambos tipos. Si existen partes con condiciones distintas para un mismo producto, se informa que la devolución depende de cada parte. No se infieren permisos de devolución a partir del catálogo actual ni de un remito. Los productos sin metadata conservan su presentación histórica.

### Histórico y documentos
Los pedidos anteriores con vencimientos conservan sus fechas informadas, incluso heredadas. Los pedidos propios no requieren una salida de consignación ni se muestran como si faltara esa fecha. Las condiciones se consultan en la web; esta versión no añade estas reglas al remito PDF, que se descarga desde el servicio autorizado. Los pedidos/precios históricos y las mejoras de marca de v40 se conservan.

## Detalle técnico

Extensión opcional estricta de modalidades_pedidos: a las seis claves legadas se agregan juntas gestion='pedido', fecha_debito (YYYY-MM-DD válida), devolucion_productos (lista no vacía, hasta 200 entradas únicas con producto_id positivo y admite_devolucion booleano). El producto debe existir en items del DTO; no se infieren flags faltantes. Sólo modalidad consignado y plazo 7/14/21/30, vencimientos=[]; devoluciones_permitidas debe coincidir con ANY de los flags explícitos. Fecha de confirmaciónISO con zona horaria. No se recalcula la fecha ni se exige igualdad confirmación+plazo. Nuevos campos privados o conjunto incompleto se rechazan.

Se conserva exactamente el DTO legado sin estas claves y sus validaciones. DTO nuevo inválido no reemplaza la última respuesta válida; la web puede mostrarla como última información guardada. El portal no crea débitos, devoluciones, salidas, pagos ni importes. Sólo presenta metadata validada del servicio y mantiene precios/cantidades del snapshot del pedido. fecha_pago/costos de proveedor no se admiten en esta extensión ni se muestran.

La devolución explícita se añade a filas de historial/detalle; sin metadata no se inventa. Si un producto tiene flags distintos en partes informadas se muestra un aviso por parte, sin conceder devolución global. No se cambia la descarga de PDF/remitos ni se modifica su contenido. Las rutas, permisos, alcance por distribuidora y nombres de configuración/destinos reales siguen iguales; incluye toda la limpieza de marca40, incluida la forma abreviada.

## Compatibilidad, instalación y recuperación

Paquete acumulativo39+40+41 compatible con bases revisadas39 (824f5da3b7f8fdb11a9b567e5ffa0c21f031ffe9) y40 (f362520c247b23796d5b0846f1170b13ab1b5587). Requiere portal0014 aplicada; sin migraciones nuevas. Primero actualizar lectores portal41 antes de habilitar la extensión del servicio636 si se necesita evitar lecturas rechazadas por40/39. Sin extensión, el lector conserva el comportamiento anterior. Publicar código no activa ni instala la conexión.

Instalador verifica huellas, entorno, esquema y plan vacío antes de copiar, y detiene ante diferencias no revisadas. Respalda automáticamente archivos reemplazados. Cambio ajeno forgotPassword.html excluido. Recuperación de código con instalador41/respaldo, sin revertir datos/esquema; antes de bajar a39/40 deshabilitar emisión de metadata propia o usar lector compatible, ya que esos lectores la rechazan. No borrar metadata histórica para forzar compatibilidad ni restaurar bases por este cambio. Respaldo SQL sujeto al intervalo acordado, sin generar uno completo por cada publicación ni contar ZIP como instalación.

## Validación y entrega

Ver VERIFICACION_v41.md. Documentación/manual/CAMBIOS/VERSION/checklist actualizados. Revisión, publicación final, ZIP/Downloads e instalación productiva se acreditan por separado. Sin campañas ni SMTP real.

## Publicación acreditada

Implementación publicada: https://github.com/pmamone1/Belnu_Web_desarrollo/commit/354f9d7366fba1cffe2eaf436ebc34911eabc04e. Draft PR: https://github.com/pmamone1/Belnu_Web_desarrollo/pull/42. ZIP construido desde código publicado, comparado con Git y guardado en C:/Users/pmamo/Downloads. Instalación productiva pendiente de ejecución y confirmación. No requiere instalar v40 antes: el ZIP v41 incluye marca40 y admite directamente las bases revisadas39/40. Sin campañas ni SMTP real.
