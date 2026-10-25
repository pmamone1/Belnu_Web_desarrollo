# Validación MiDistri26 — 25/10/2026

- Suite completa197pruebas correcta con1omisión preexistente (196correctas). Las2regresiones nuevas comprobaron etiqueta Más vendidos y CTAizquierda/derecha Ver, conservando las etiquetas centrales y enlaces. Se observaron fallar antes del cambio.
- Django check sin incidencias y makemigrations --check --dry-run sin cambios.
- Instalador/ZIP:25pruebas correctas contra bytes reales de las bases23,24y25, con preflight/aplicación/restauración y rechazo de CSScentral ausente/alterado y de planes ajenos. Sin objetivos ni ejecución de nuevas migraciones.
- QA local en navegador con datos ficticios y templates/CSS reales: cuatro diseños (compacto,fotos,promociones,lista), marcos1440/390px,6tarjetas con distintos títulos/display/fotos/etiquetas. Las8combinaciones tuvieron diferencia0px entre selectores de cantidad de una misma fila, sin desbordamiento horizontal y con controles de44px dentro de la tarjeta. Se revisó visualmente el pie de compra alineado y el CTA Ver; captura y mediciones locales guardadas en comprobantes de trabajo.
- Manual principal28páginas:27anteriores conservadas. Capítulo vigente y unión revisados visualmente.
- Revisión independiente estática y cotejo final ZIP/commit antes de entregar. Instalación y aceptación HTTPS pendientes.

No se probó producción ni se enviaron campañas. No cambia criterio de ranking, cantidades/display, datos económicos, contratos, permisos, documentos, remitentes, WhatsApp o cron. Urban606 se conserva.
