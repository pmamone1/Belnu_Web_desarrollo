# MiDistri-Pedidos v38 - Ajustes del catálogo

Actualización acumulativa sobre bases34/35/36/37 revisadas. Conserva compatibilidad con Urban626/627/628 y el Urban compatible instalado. Instalación productiva pendiente. Sin campañas.

## Guía de uso
En PC, el lateral de filtros y promociones permite llegar al último botón completo, por encima de Ver mi pedido. El espacio disponible se ajusta al alto real de esa barra y al redimensionar la ventana.
En celular y tableta, Filtros y promociones empieza cerrado al entrar y al cargar otro catálogo dentro de la sesión. Tocá su título para abrirlo o cerrarlo; tu elección se conserva en esa pantalla. En PC el panel empieza abierto. Al pasar entre celular y PC se aplica el estado de ese tamaño. Sin JavaScript los filtros siguen abiertos y utilizables.
Se conservan las fotos completas, Relevancia estable, filtros y páginas de24/48/96/192, cantidades y carrito, diseños y temas de v37. Esta guía prevalece sobre los dos límites visuales anotados como diferidos en v37; el resto del manual anterior sigue vigente.
El cambio sólo corrige presentación. No cambia precios, pedidos, sesiones, permisos, históricos ni campañas. Publicar el código o descargar el ZIP no acredita instalación en producción.

## Detalle técnico
catalogo_lateral.css descuenta --catalogo-carrito-alto de100dvh, además de32px de margen del lateral sticky. catalogo_lateral.js mide la oclusión vertical de body>.sticky; ResizeObserver observa border-box y actualiza cambios de altura, borde o relleno del carrito y resize cubre cambios de ventana. Sin barra, la reserva medida es cero; sinJS la reserva CSS por defecto es84px y el panel nativo permanece abierto.
El inicializador corre al cargar y tras midistri:render. Un Set mantiene sólo los paneles actuales; los nuevos reciben el estado por breakpoint/preview y los ya inicializados conservan su elección manual. Hay un único listener global de breakpoint y uno de resize; al reemplazar la barra se desconecta su observer. No se modifican sesion.js, la sesión por pestaña ni la navegación. El preview móvil sigue cerrado inicialmente. base.html referencia CSS/JS38 para renovar caché.
Regresiones ejecutables en tools/test_catalogo_v38.cjs y servidor tools/qa_catalogo_v38.py. La prueba navega mediante MidistriTab.load real, reemplaza body y emite el evento auténtico. Instrumenta sólo el recuento de listeners, sin sustituir el código productivo de sesión/panel. fixtures sintéticos: SQLite memoria, API stub y correo locmem; solicitudes externas de imagen interceptadas.

## Compatibilidad y recuperación
Sin modelos, rutas, permisos ni migraciones nuevas; se requiere midistri_portal0014_dispositivo_recordado aplicada. El paquete contiene todos los archivos acumulativos de37 más38 y acepta bytes revisados de34/35/36/37; no necesita instalar versiones intermedias. No modifica credenciales, SMTP, WhatsApp, cron, venv ni templates/accounts/forgotPassword.html.
El instalador v38 verifica hashes, destino, Python3.7 de belnuweb, intervalos/dispositivos y plan de migraciones vacío antes de reemplazar. Rechaza diferencias desconocidas y respalda los archivos reemplazados. No genera ni exige un respaldo completo nuevo por cada versión; se mantiene la frecuencia autorizada y el registro sólo de instalaciones confirmadas.
Recuperación de código: ejecutar instalar.py de v38 con --root /home/mcollini/belnuweb --restore /home/mcollini/respaldo_midistri_pedidos_XXXX, reemplazando la ruta por el respaldo real informado. Usar /home/mcollini/virtualenv/belnuweb/3.7/bin/python. Verifica versión, integridad y ausencia de cambios posteriores; no revierte esquema, datos ni históricos. No usar un respaldo de otra versión con este instalador.

## Validación
Ver VERIFICACION_v38.md para resultados ejecutados. Se distingue QA local de instalación en cPanel, aún pendiente; sin SMTP ni pruebas productivas. El manual PDF antepone este capítulo y conserva íntegramente las páginas anteriores de v37.

## Instalación cPanel
Subir midistri_pedidos_v38_ajustes_catalogo.zip a /home/mcollini. Comprobación y aplicación requieren la misma carpeta extraída y el Python propio de belnuweb. Revisar toda la salida, conservar la ruta de respaldo y confirmar la instalación por su resultado real.
```sh
cd /home/mcollini
unzip -q midistri_pedidos_v38_ajustes_catalogo.zip -d midistri_actualizacion_v38
/home/mcollini/virtualenv/belnuweb/3.7/bin/python /home/mcollini/midistri_actualizacion_v38/instalar.py --root /home/mcollini/belnuweb
/home/mcollini/virtualenv/belnuweb/3.7/bin/python /home/mcollini/midistri_actualizacion_v38/instalar.py --root /home/mcollini/belnuweb --apply
```
