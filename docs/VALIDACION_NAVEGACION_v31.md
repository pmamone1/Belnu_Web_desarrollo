# Validación local y entrega
Fecha31/10/2026. Sólo datos sintéticos; SMTP en memoria y red exterior bloqueada en pruebas visuales. No se usó producción ni se enviaron correos/campañas.
- Urban:214 pruebas de regresión PostgreSQL17 aprobadas; entrega compartida, concurrencia, permisos, documentos, configuración, campañas sin reintentos y dispositivos. Pruebas adicionales del nombre público/vista previa aprobadas según registro local.
- Portal:266 pruebas MariaDB10.11 aprobadas (2 omisiones de motor), sin cambiar SQLMode. Paginación desktop1440 y móvil390/320, páginas1/2/12 y filtros; sin salida del encabezado, Cambiar perfil conservado. Spinner real de recordado.js: visible en espera, oculto al error, estado accesible, movimiento reducido.
- Manuales principales con nuevo capítulo vigente y páginas anteriores conservadas; primera página y unión revisadas visualmente.
- Instaladores:29 pruebas Urban y28 portal; preflight/apply/repetición/rollback sintéticos, rechazo de diferencias y plan vacío de migraciones.
- Revisión independiente y huellas finales: completar antes de publicar. Instalación productiva pendiente de ejecutar comandos.
