# Validación v23 — 25/10/2026

- Suite completa portal: 195 pruebas, resultado correcto con una omisión preexistente (194 correctas). Se verifica actualización al emitir remito, entrega total/parcial, cancelación, ausencia de LIN en historial/detalle e identidad del catálogo conservada.
- Django check sin incidencias y makemigrations --check --dry-run sin cambios.
- Instalador/ZIP: 25 pruebas correctas contra la base22 real; comprobación sin escritura, respaldo/restauración, rechazo de archivos centrales faltantes/alterados y pendientes ajenas. Sin objetivos ni ejecución de nuevas migraciones.
- Manual principal: 25 páginas; las 24 anteriores se conservan. Capítulo y unión revisados visualmente.
- Revisión independiente estática cerrada sin P1/P2. El implementador ejecutó las pruebas; el revisor no accedió a producción. ZIP final se coteja contra su commit publicado antes de entrega.

Instalación productiva y aceptación HTTPS pendientes. No se enviaron campañas ni se alteraron precios, saldos, históricos, remitentes, WhatsApp, cron o conexión. Urban606: 112 pruebas dirigidas PostgreSQL y 24 de instalador/ZIP correctas.
