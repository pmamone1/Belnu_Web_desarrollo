# Validación MiDistri-Pedidos v18

Fecha24/10/2026. Base acumulativa16/17. Runtime localPython3.12/Django3.2.15/SQLite; sintaxis destinoPython3.7 verificada al construir.

Suite completa171 casos:170 aprobados y1 omitido. JavaScript:16 casos de sesión/código y estadoeditor aprobados; sintaxis de editor, carrusel y cantidades correcta. Casos nuevos RED observados y luego GREEN: aleatorio400 antes de la acción, cabezal equivocado, carrito acepta no-múltiplo y checkout inválido transmite, metadata de anulación se perdía. Cantidades inválidas ahora no mutan carrito ni crean/transmitenPedidoLocal; reintentos previos mantienen snapshot. Precio sigue por unidad; total150000 en caso de6×25000.

QA real en navegador local con datos sintéticos: seleccionar Catálogo mueve scroll de0 a249px y lo resalta; cabezal/Página completa muestra conjunto; banners laterales se crean con zona propia; Random toma6 y3 productos distintos en borrador; guardado por AJAX confirmado sin publicar. Carrusel público de prueba tiene sólo‹/›, navega3/6 y no muestra pausa/reanudar. Leyenda x unidad visible; botón de display6 avanza0→6→12. No se hizo pedido ni envío en producción. Captura local de demostración guardada fuera del paquete.

Contrato de anulación valida bool/estado, motivo5..2000 sin truncarlo y fecha con zona; atención total/parcial se valida contra cantidades/importes originales. Historial distingue anulación de falta de stock y muestra total vigente. Alcance/CSRF/permisos se revalidan; aleatorio no guarda ni publica y sólo usa catálogo elegible de tienda autorizada.

Django check y makemigrations correctos, sin esquema nuevo. Instalador/ZIP:23 casos aprobados y aplicación/recuperación ensayadas contra bytes exactos de16 y17. Manual principal20páginas,19previas preservadas; página1/unión2 renderizadas y revisadas. Revisión independiente de fuentes sin defectos importantes abiertos. Inventario/CRC/hashes se verifican contra commit al entregar.

Requiere Urban601 primero, luego portal18. Instalación y aceptaciónHTTPS pendientes; teléfono físico pendiente. No se envían campañas ni se modifican remitentes, WhatsApp, cron o venv. MiDistri-Puntos sólo análisis.
