# Validación de la entrega coordinada 20261021-midistri-v1

21/10/2026. Revisados repositorios independientes: Urban pmamone1/sistema7000 base9f321d3; MiDistri pmamone1/Belnu_Web_desarrollo base10b49c4. Código preparado; cPanel no modificado desde este entorno.

- Urban Django5.2.18/Python3.12: 67 tests de integración nueva, remitos históricos, alcance y políticas de rutas, correctos. Incluye recepción sin saldo, precio/tenant, token un uso/vence, cantidad inválida, API autenticada, consola, Excel sin matrícula, emisión y correo idempotentes, y cola que no bloquea por fallos. Una advertencia del entorno de prueba indica directorio estático vacío; no es fallo de aplicación.
- MiDistri Django3.2.14/Python3.12: 9 tests del portal correctos (segregación/cabecera, invitación GET sin consumo, snapshot incompleto, bajas, fallo de red conservado, rutas legacy, pedido ajeno404, baja removible y precio cambiado que requiere revisión).
- Cinco pruebas existentes de preparación de entorno y manifiesto/referencias estáticas: correctas.
- Cinco pruebas del instalador: check sin cambios, proyecto equivocado, base diferente, paquete alterado, aplicar/respaldo/restaurar.
- Django check y makemigrations --check --dry-run sin incidencias en ambos proyectos.
- Análisis de sintaxis de los archivos nuevos del portal y del instalador con gramática Python3.7: correcto. Ejecución sobre Python3.7 real de cPanel pendiente.
- Prueba HTTPS real entre dos procesos Django con bases SQLite sintéticas independientes: sync2 distribuidoras, invitación GET/POST, catálogo solo distribuidora del vendedor, carrito/revisión/envío, doble envío sin duplicación, historial, enlace reutilizado rechazado. Certificado local autofirmado y validación relajada únicamente en el script QA fuera de repositorios; el transporte de producción mantiene verificación TLS y no admite HTTP/redirecciones.
- Continuación con base sintética: recibir/exportar no cargó saldo; confirmar dos veces creó un único Pedido y saldo200, PDF congelado y correo con adjunto en backend de memoria. No se envió correo externo ni se usó producción para pruebas.
- PDF de remito sintético revisado visualmente. Manual principal Urban regenerado desde Markdown completo,28 páginas, primeras3 revisadas visualmente incluida unión con contenido previo.
- Revisión independiente: tres hallazgos importantes (baja en carrito, cambio silencioso de precio, starvation de correo). Reproducidos con pruebas fallidas y corregidos. Nombres locales del producto también se conservan para mostrar intentos pendientes.

## Pendiente antes de habilitar producción
Prueba conectividad/correo real desde cPanel, motores PostgreSQL/MySQL reales y concurrencia, validación visual en navegador/celular, unidades de presentación/precios y publicaciones por distribuidora. No afirmar suite completa del repositorio Urban: se ejecutaron los67 tests mencionados, no todas sus suites históricas.

El navegador de QA no pudo instalarse (descarga de Chromium incompleta en el entorno); no se declara revisión visual móvil como realizada. Plantillas renderizadas en tests Django. El código responsive usa controles grandes y una columna en pantallas pequeñas, pero necesita ese control visual antes del piloto.

## Decisiones documentadas
- Catálogo por distribuidora mediante publicaciones explícitas, sin deducir stock ni pertenencia por nombre.
- Sin RI adicional: precio vendedor común confirmado por el titular.
- División de Pedido nativo por proveedor cuando una solicitud incluye varios. Un PDF conjunto contiene los remitos emitidos.
- La API pública de catálogo existente conserva sus campos; los nuevos precios vendedor/contactos se sirven solo bajo conexión privada autorizada.
- Históricos/productos/fotos legacy se conservan como respaldo y se ocultan del portal; no se borran físicamente.
- No se instalaron cron, secretos ni envíos en cPanel. La instalación se detiene si la base difiere de la revisada.
