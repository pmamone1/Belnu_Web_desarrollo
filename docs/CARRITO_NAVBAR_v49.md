# Carrito en el menú · MiDistri v49

## Guía de uso

### Agregar y cambiar productos
En el catálogo elegí la cantidad y tocá Agregar / actualizar. El ícono a la derecha del menú muestra cuántas unidades llevás. En el carrito usá Actualizar o Quitar: el contador y el total cambian al instante, en la misma pantalla. Si un cambio no se confirma, vas a ver un aviso. El botón Enviar pedido sigue siendo el que confirma el envío.

### Qué datos se muestran
En el carrito figura tu nombre y línea. MiDistri no agrega el nombre ni el número de la distribuidora al encabezado, al detalle del pedido ni a la selección de perfiles de vendedor. La administración conserva el nombre de cada distribuidora para que el operador pueda elegir dónde trabajar.

### Configurar el mensaje
En Configurar MiDistri, elegí Presentación del carrito para editar u ocultar el bloque y usá Revisar y publicar. El aviso predeterminado dice que la mercadería es consignada y que los pedidos tienen derecho a devolución, salvo casos especiales.

## Detalle técnico

El POST existente de cantidad responde con JSON cuando el cliente solicita ese formato. Conserva CSRF, alcance por perfil y pestaña, disponibilidad, múltiplos de presentación y el límite de renglones. Desde el carrito devuelve el mismo fragmento del GET, con revisión y totales recalculados. El navegador serializa cambios, conserva la observación y mantiene el formulario normal cuando no usa JavaScript en los accesos compatibles con ese modo. La página usa mensajes genéricos al mostrar los textos anteriores predeterminados y quita las referencias conocidas al negocio en el encabezado público sin cambiar el JSON publicado. El texto libre, imágenes, motivos históricos y remitos originales no se editan.

Instalación sobre v47 o v48, con 0016 ya aplicada. El ZIP incluye la v48 si aún no se instaló. Sin migraciones, cambios en Urban Soft, pedidos automáticos ni campañas. El instalador verifica el código de base, realiza un respaldo de archivos y recompila los estáticos. Para revertir, usar el respaldo de código generado por esta instalación; los borradores, documentos y pedidos mantienen su contenido y no se migra la base.
