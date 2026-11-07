# Validación local MiDistri-Pedidos v43

Fecha de validación 07/11/2026. Instalación productiva pendiente.

Las 46 pruebas Django de abastecimiento, reseña, galería, catálogo lateral, indicadores, presentación, SKU y portal base pasaron sobre SQLite sintético. El caso de una unidad local frente a un pedido de dos se reprodujo primero en rojo, tanto al agregar como al enviar el carrito. Con la corrección se conserva el carrito y se rechaza el pedido nuevo antes de registrarlo. Las pruebas incluyen omisión del campo, rechazo atómico, separación de estados, vista previa y conservación de referencias.

Pasaron 5 pruebas con python -m unittest tools.test_paquete_v43 -v. El ZIP provisional se comprobó contra archivos de las cuatro bases reales de Git: 39, 40, 41 y 42. La simulación ejecutó la comprobación previa y la copia sobre carpetas temporales. Verificó CRC y SHA-256, rechazo de archivos faltantes o cambiados, conservación de 0015 ya aplicada y rechazo de planes ajenos, regresivos o incoherentes. La restauración de código sobre base 42 conservó 0015 y quitó sólo la migración 0016 pendiente. No se llamó a cPanel.

En bases SQLite temporales se ejecutaron las rutas reales 0014 a 0016 y 0015 a 0016. La primera aplicó 0015 y 0016. La segunda aplicó sólo 0016. Se conservaron una descripción anterior y un pedido sintético. La nueva disponibilidad comenzó con un objeto vacío. Django informó que el modelo no requiere generar migraciones adicionales.

El PDF principal tiene 45 páginas. Se compararon el contenido y el texto de las 44 anteriores y se renderizaron e inspeccionaron la guía v43 y su unión con la primera página histórica.

La publicación y el ZIP definitivo se acreditan al entregar. La instalación y sincronización productivas siguen pendientes. Las pruebas utilizaron datos sintéticos y no enviaron pedidos ni comunicaciones reales.
