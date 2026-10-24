# MiDistri-Pedidos v12 - Banners panorámicos
Estado: implementado y probado localmente; instalación productiva pendiente.

## Guía de uso
Desde Urban Soft, abra Pedidos > Administrar MiDistri-Pedidos y entre a Mi tienda. Elija la distribuidora que desea configurar.
Agregue o edite un bloque Banner, seleccione las fotos de productos, el título, texto y botón. El banner ocupa todo el ancho de la ventana y muestra la imagen más grande.
La opción de mostrar la foto completa o recortarla se conserva. En el celular la foto y el texto se acomodan uno debajo del otro para facilitar la lectura.
Entre varias fotos se aplica un fundido suave. Puede usar Anterior / Siguiente y Pausar / Reanudar. El intervalo sigue siendo el que configuró en la tienda.
Con una sola foto no aparecen controles de navegación. Los videos requieren que la persona pulse reproducir; no comienzan automáticamente.
Revise la vista previa de PC y celular antes de publicar un cambio de contenido. La actualización de apariencia no publica sus borradores ni cambia productos o precios.

## Instalación y operación técnica
CSS panorámico con unidades del contenedor de página para excluir barras de desplazamiento; preview móvil acotada. Cuatro diseños y cuatro temas conservados.
Fundido cruzado600ms cancelable, controles con foco/teclado/táctil, pausa por foco/hover/visibilidad y movimiento reducido sin animación ni rotación inicial. Las diapositivas salientes quedan inert y aria-hidden mientras finaliza la transición.
Inicialización idempotente al evento midistri:render y limpieza de listeners, temporizadores y animaciones; compatible con la sesión por pestaña del vendedor.
Las promociones anteriores a la primera publicación utilizan el controlador común, conservando datos, enlaces, videos e interacción manual; no se publica automáticamente un borrador.
Acumulativo sobre bases8/9/10/11 revisadas. Sin migración propia: conserva/verifica0009 y aplica esa migración anterior sólo si falta. Python3.7/Django3.2, sin nuevas dependencias ni variables.
La recuperación del instalador es conservadora si hay migraciones de la entrega acumulada aplicadas: corrección hacia adelante, sin borrar páginas publicadas ni pedidos. Archivos de código respaldados.
No se instaló ni se probó producción durante esta preparación. Sin campañas, cambios de catálogo, SMTP, conexiones o venv.
