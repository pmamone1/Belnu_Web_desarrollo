# Verificación MiDistri-Pedidos v39

Corte local sobre base 38, commit 7e0fca0111d64a18f36da51f2ef27b0817fc7d18, coordinado con Urban 1.18.631. Publicación, ZIP finales e instalación productiva pendientes. El archivo ajeno templates/accounts/forgotPassword.html no forma parte de esta actualización.

## Ejecución y límites

Ejecución real en Python 3.12/Django 3.2, con base sintética de QA y sin SMTP real. Se verificó sintaxis para los intérpretes objetivo Python 3.7/3.10; no se ejecutó la suite de esta entrega realmente en ellos. Urban ejecuta Python 3.12/Django 5.2. No se acredita concurrencia PostgreSQL real.

332 pruebas OK con 2 omitidas en 6,806 segundos. Evidencia: tmp/v39_final_funcional.log. Los mensajes esperados de handoff/captura rechazados pertenecen a pruebas sintéticas y no son envíos a usuarios.

Las dos omitidas corresponden a motores específicos: el bloqueo de dos operadores del editor exige PostgreSQL (tests_pagina_v11.py) y la creación concurrente del intervalo único exige MariaDB/MySQL (test_intervalos_mariadb_v29.py). Sus condiciones las omiten en SQLite; no presentarlas como pruebas de concurrencia aprobadas en este corte.

## Contrato y comportamiento cubierto

- modalidades_pedidos opcional y estricto: identidad del pedido dentro del DTO, tipos exactos, fechas ISO válidas, modalidad/plazo/devolución coherentes, rechazo de extras/duplicados y última respuesta válida preservada.
- Firme sin devolución consignada; consignado con plazo y varias fechas, incluso heredadas de salidas anteriores. Históricos sin metadatos compatibles, sin inferir deuda desde Entregado o remito.
- Atención/cancelación efectiva por fuentes enlazadas; documento con consignación anulada retirado completo y orientación a pedir comprobante vigente, sin reescribir Pedido ni PDF histórico.
- Regresiones de permisos, alcance, sesiones, catálogo y snapshots en la suite del portal. Sin rutas, modelos o migraciones nuevas.

## QA visual y de navegación

Ejecutados tmp/qa_modalidades39.py y tmp/qa_modalidades39.cjs con fixtures locales y Playwright. Historial y detalle a 1440, 390 y 320 px, alto 900 px. Capturas completas y centradas en modalidades dentro de tmp/qa_modalidades39.

Se comprueba apertura de detalle del historial, etiquetas Firme/Consignado, plazo de 30 días y dos fechas 01/12/2026 y 03/12/2026. Sin desborde horizontal ni errores JavaScript. Solicitudes externas bloqueadas; no se utiliza catálogo productivo ni SMTP. Este QA no prueba el circuito económico completo ni concurrencia de motor productivo.

## Coordinación Urban y regresión conocida

Urban: 123 pruebas dirigidas OK y DDL 0132 sobre 0131 aplicado en SQLite en memoria, históricos/saldos conservados y sin backfill. QA local Urban configuración/seguimiento/pantalla de confirmación/alerta a 1440/390/320 px: firme saldo proveedor 40, consignado 10 - 3 = 7/70, sin desborde ni errores JavaScript.

Su regresión amplia previa no está verde: 37 incidencias, 5 fallos y 32 errores, reproducidas por el equipo en el bloque legado de 53 pruebas contra base 630 con mismos nombres/tipos/motivos de fixtures de perfiles pendientes sin permisos. No sumar conteos de corridas diferentes ni afirmar toda la suite Urban aprobada. Ver docs/VERIFICACION_v631.md en el repositorio Urban.

## Pruebas previas de paquete y recuperación

Corte previo a ZIP/publicación: 29 pruebas de instalador/paquete Portal OK en 10,869 segundos (tmp/v39_instaladores.log) y 30 Urban OK en 33,388 segundos (tmp/v631_instaladores.log del repositorio Urban), en destinos sintéticos. Ambas bases reales se comprobaron y core ausente/modificado se rechazó. ZIP finales, huellas, copia a Downloads y publicación quedan pendientes de cierre por el responsable. Estos resultados no prueban instalación en cPanel.

Portal 39 no agrega migraciones; conservar esquema existente. Restauración del portal se hace por su respaldo de archivos y controles del instalador, no deshace Urban 0132 ni sus tratamientos/salidas. Aplicada 0132 en Urban se corrige hacia delante con guardas/lectores compatibles, sin borrar históricos.

## Manual y entrega

Manual_MiDistri_Pedidos_Online.pdf: 41 páginas, 1 nueva y 40 preservadas de base 38. tools/actualizar_manual_v39.py compara streams de contenido y texto de cada página histórica extraída con git show. Conservación comprobada. Nueva página y unión con primera anterior renderizadas con Poppler e inspeccionadas visualmente, sin cortes ni solapes.

Documentación técnica/usuario, VERSION_DOCUMENTADA, CAMBIOS, checklist y pruebas manuales actualizados. Pendientes: ZIP final/huellas/Downloads, commits publicados, comandos completos de cPanel, instalación y aceptación productiva confirmadas. Sin campañas, SMTP real, modificación de remitentes/WhatsApp/cron/venv o respaldo SQL nuevo por esta documentación.
