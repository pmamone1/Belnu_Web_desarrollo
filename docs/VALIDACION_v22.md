# Validación v22 — 25/10/2026

- Suite completa del portal: 191 pruebas, resultado correcto con una omisión preexistente (190 ejecutadas correctamente).
- Django check sin incidencias y makemigrations --check --dry-run sin cambios.
- Instalador/ZIP: 25 pruebas correctas; base real 99e3663, comprobación sin escritura, aplicación/restauración y rechazo de archivos centrales faltantes/modificados. Se verifica que no haya objetivos de migración ni ejecución de migrate.
- Render local del catálogo con datos de prueba: una prueba correcta; sólo las dos publicaciones con posición aparecen en Más vendidos, la publicación sin ventas sigue accesible por Nombre.
- Manual principal: 24 páginas, capítulo vigente y unión revisados visualmente; 23 páginas históricas conservadas.
- Inventario explícito; cotejo final con commit publicado registrado en el comprobante de entrega. Revisión de la lógica comercial compartida con Urban605.

Instalación productiva, aceptación HTTPS y sincronización pendientes. No se envían campañas, no se cambian remitentes, credenciales, WhatsApp, cron ni conexiones.
