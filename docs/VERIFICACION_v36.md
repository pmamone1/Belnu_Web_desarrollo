# Verificación MiDistri-Pedidos v36

31/10/2026. Local, SQLite en memoria y datos sintéticos. Sin producción ni SMTP.
- Cinco pruebas nuevas observadas fallando antes de implementar; después OK: grupos y totales,50+1, filtros/ficha, conciliación/cero, escape, permisos, propietario/caducidad y caché privado.
- Suite completa317 tests OK,2 skips preexistentes por motor.
- Instalador/paquete28 tests OK: bases34 y35 reales probadas en carpetas temporales; preflight/apply, idempotencia/rollback y rechazo de diferencias. No son instalaciones productivas.
- Navegador: abrir/cerrar, páginas50+1 ida/vuelta dejando el grupo abierto, teclado,1440/390/320, cuatro temas y sin JavaScript. Herramientas qa_estados_v36.py/test_estados_v36.cjs. La entrega acumula las pruebas y mejoras visuales35 previamente verificadas.
- Manual38 páginas, capítulo36 y unión con35 revisados visualmente. Generador conserva contenido de páginas anteriores.
- Revisión independiente final: sin hallazgos accionables en grupos/conciliación/ficha/alcance/caducidad/enlaces/inventarios. Cambio ajeno forgotPassword excluido.
Sin migraciones nuevas, API remoto nuevo, captura adicional, datos económicos/históricos, remitentes, WhatsApp, cron o campañas. Producción pendiente. Los ZIP se verifican contra el commit publicado antes de entregar.
