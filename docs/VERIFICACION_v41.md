# Verificación MiDistri-Pedidos v41

## Base y alcance

Rama codex/midistri-pedidos-propios-v41 desde MiDistri40 f362520c247b23796d5b0846f1170b13ab1b5587. Extensión opcional estricta de metadata propia; presentación informativa de fecha de débito y devolución por producto. Incluye marca40 y preserva datos propios/DTO legado. No se cambia la descarga ni contenido remoto de remitos. Cambio ajeno templates/accounts/forgotPassword.html conservado y excluido.

## Pruebas y evidencia local

Ciclo rojo comprobado: nuevo DTO inicialmente rechazado y pantallas sin fecha/flags; tras integrar, 22 pruebas dirigidas OK de propios, legado y marca. Nuevos casos cubren plazos 7/14/21/30, fechas configuradas sin recalcular, devolución false/true, copia sin referencias mutables, campos privados/incompletos/incoherentes, producto ajeno/duplicado y persistencia de última respuesta válida/precios ante DTO inválido. No se crea ningún débito/pago/salida durante estas pruebas.

Suite completa: 346 pruebas OK con 2 omitidas (344 pasan), 7,083 segundos. Comando tmp/qa_midistri14/Scripts/python.exe manage.py test midistri_portal --settings=midistri_portal.test_settings --verbosity 1. Evidencia tmp/propios41_suite.log. Las omitidas previas corresponden a bloqueo real PostgreSQL y concurrencia MariaDB/MySQL fuera del motor SQLite usado; no afirmar pruebas productivas de esos motores ni SMTP real.

Paquete/instalador: 29 pruebas OK, 32,357 segundos. Comando tmp/qa_midistri14/Scripts/python.exe -m unittest tools.test_instalar_release_midistri_v41 tools.test_paquete_v41. Evidencia tmp/propios41_instaladores.log. Prueban ZIP real con ambas bases Git39/40, preflight/aplicación en destinos sintéticos, normalización CRLF y rechazo core ausente/alterado; recuperación/reintento sin revertir datos. No acredita instalación cPanel.

manage.py check sin incidencias y makemigrations --check --dry-run: No changes detected, ambos con test_settings. No migraciones nuevas. Conserva validación del esquema 0014 y plan vacío.

## QA visual y marca

Fixtures tmp/qa_propios41.py y Playwright tmp/qa_propios41.cjs: historial y detalle con devolución mixta, sin devolución e histórico legado, a 320/390/1440 px, 18 capturas. Comprueban fecha débito 16/11/2026 en propios, flags por producto, fechas legadas 01/12/2026, ausencia de aviso erróneo de devolución faltante/Urban, sin desborde horizontal ni errores JavaScript. Solicitudes externas bloqueadas. Inspección visual de detalle mixto a 390 px, historial mixto a 1440 px y detalle sin devolución a 320 px. Estos fixtures no prueban el cálculo/debito del servidor ni salida de SMTP.

Escaneo de todas plantillas/static comunes y portal con palabra Urban sin distinguir mayúsculas y regresión de literales de mensajes UI: incluidos en suite de marca40, aprobados. Nombres/direcciones/datos de usuarios se conservan por diseño.

## Manual y entrega

Manual_MiDistri_Pedidos_Online.pdf: 43 páginas = 1 nueva vigente v41 + 42 históricas de v40. tools/actualizar_manual_v41.py compara streams de contenido y texto de cada página histórica con Git40 y los conserva. Guía v41 y unión con v40 renderizadas e inspeccionadas; sin cortes en el capítulo nuevo. Render nuevo con nombre único confirma título completo; la página de unión se comparó píxel por píxel con el PDF v40 original publicado: idéntica a 1132 × 1600, sin diferencias. Poppler informa fuentes Symbol/ArialUnicode ausentes del histórico, sin impedir lectura de la guía.

Paquete acumulativo 39+40+41 con inventario explícito de 66 archivos y 68 entradas de ZIP en tools/release_files_v41.json, bases 39 SHA 824f5da3b7f8fdb11a9b567e5ffa0c21f031ffe9 y 40 SHA f362520c247b23796d5b0846f1170b13ab1b5587. Excluye cambio ajeno, credenciales, media, bases y entornos. Instalador crea respaldo privado de archivos, no exige respaldo SQL nuevo por cada paquete ni incrementa instalaciones confirmadas.

Revisión independiente, publicación GitHub, reconstrucción del ZIP final/copia a Downloads y producción se acreditan por separado. En este corte: validación local completada; revisión independiente completada sin hallazgos; publicación final y copia a Downloads comprobadas; instalación productiva pendiente. Sin campañas ni envíos SMTP.

## Revisión independiente

Revisión fresca de v41 completada: 22 pruebas independientes OK y sin hallazgos. Contrato legado, extensión estricta, UI y conservación del PDF revisados antes de publicar.

## Cierre de entrega acreditado

Implementación publicada: https://github.com/pmamone1/Belnu_Web_desarrollo/commit/354f9d7366fba1cffe2eaf436ebc34911eabc04e. Draft PR: https://github.com/pmamone1/Belnu_Web_desarrollo/pull/42. ZIP construido desde código publicado, comparado con Git y guardado en C:/Users/pmamo/Downloads. Instalación productiva pendiente de ejecución y confirmación. No requiere instalar v40 antes: el ZIP v41 incluye marca40 y admite directamente las bases revisadas39/40. Sin campañas ni SMTP real.

Se comparan los 66 payloads y el instalador raíz byte por byte con git show del commit publicado; integridad/huellas del ZIP y copia Downloads comprobadas. Reconstrucción final posterior al cierre documental registra su propio source_commit en release_manifest.json; huella final en el chat para evitar referencia circular dentro del ZIP.
