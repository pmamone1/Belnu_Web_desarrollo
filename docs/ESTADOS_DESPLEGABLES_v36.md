# MiDistri-Pedidos v36 · Pedidos por estado desplegables

## Guía de uso

1. En Estadísticas de vendedores, dentro de Pedidos por estado y atención, tocar Ver pedidos debajo de la fila que se desea consultar. El detalle se abre allí mismo, sin otra pantalla ni espera de descarga.
2. Se muestran fecha y referencia, vendedor, distribuidora, unidades solicitadas/confirmadas e importes solicitados/confirmados. La referencia permite abrir el pedido completo con los permisos existentes. Confirmado no equivale a cobrado.
3. Cada grupo conserva el período, corte y ficha de vendedor de la consulta. Cancelado, preparado completo/parcial y OK para preparar no se mezclan. Si faltan datos históricos, se indica Por conciliar.
4. Para grupos largos se muestran 50 pedidos por página. Anterior/Siguiente conserva la consulta y deja abierto el grupo elegido. El desplegable funciona con teclado y sin JavaScript. Se puede cerrar tocando nuevamente su título.
5. Esta entrega incluye v35: fotos pequeñas ampliadas proporcionalmente y estados de Mis pedidos con colores definidos. No hace falta instalar v35 por separado si continúa instalada v34.

## Detalle técnico

analitica_informes conserva las claves de estado/atención junto a sus etiquetas en cada agregado. analitica_estados.preparar agrupa únicamente data.pedidos ya autorizado y filtrado por ficha; no usa todo el catálogo ni llamadas a Urban. Correlaciona por códigos, no por etiquetas traducidas, y pagina cada grupo a 50, con orden por fecha/id. No modifica el resumen o el Excel. Los valores provienen del snapshot ya consultado y conciliación impide presentar importes inciertos.
analitica_views invoca la proyección sólo para HTML completo, después de los controles existentes de operador, alcance, propietario y caducidad. No hay nueva ruta ni permisos. Las plantillas añaden details/summary nativos dentro de una fila a todo el ancho y una tabla con desplazamiento horizontal en celular. Los enlaces GET de página validan que el grupo exista en la consulta/ficha; cada navegación vuelve a validar acceso y caducidad.

## Compatibilidad, validación y rollback

Portal v36 acumulativo sobre 34 o 35, con Urban626/627 sin cambios de contrato. Sin migraciones nuevas, cambios económicos, históricos, credenciales, cron, captura adicional o campañas. Código publicado no acredita instalación productiva.
Pruebas de datos: conteos por grupo, paginación51=50+1, ficha sin otros vendedores, conciliación/cero, autoescape, caché privado, permisos, propietario y vencimiento. Navegador local: abrir/cerrar, teclado, páginas ida/vuelta, cuatro temas,1440/390/320 y sin JavaScript. No se usa producción ni SMTP para probar.
Rollback: restaurar el respaldo de archivos de esta versión, sin revertir datos o migraciones. Volver a35 pierde el desplegable nuevo; volver a34 pierde además los cambios visuales de35. Borradores, pedidos y snapshots se conservan. Reutilizar respaldo de base conforme a la política 30 instalaciones confirmadas/15 días; no contar publicaciones o ZIP como instalaciones.
