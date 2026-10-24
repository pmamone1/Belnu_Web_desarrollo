# Validación MiDistri-Pedidos v14

Implementado y revisado localmente; instalación y aceptación productiva pendientes. No se envió la campaña, no se cambiaron remitentes ni WhatsApp.

- RED inicial: falta de ingreso sin tienda en Urban (12 pruebas fallidas) y formulario/selección del portal (5 fallos y1error funcional tras resolver dependencias locales). GREEN posterior: nuevo contrato y formulario integrados.
- Urban:20 pruebas en PostgreSQL local, incluidas3concurrentes (consumo único de OTP/ticket y no duplicación de entregas). Regresión de ingreso nuevo/legado/API59OK. Después de las correcciones finales,107 pruebas de ingreso, operadores y ámbitoOK. Logs sintéticos locales v598_concurrencia.log, v598_regresion_email.log y v598_revision_green.log.
- MiDistri: suite completa midistri_portal157 pruebas,156 ejecutadasOK/1omitida, Django3.2.15 en Python3.12 local. Siete casos nuevos observadosRED yGREEN. No se afirma ejecución del runtimePython3.7 del servidor.
- Instaladores y ZIP sobre bases reales: Urban23OK; MiDistri22OK. Se verifican preflight sin escritura, base alterada/ausente rechazada, aplicación y recuperación en temporales, rechazo de migraciones ajenas y bloqueo de reversión tras0015. Logs v598_instaladores2.log y v14_instaladores2.log.
- Django check y makemigrations --check: sin errores ni cambios de modelos faltantes. Ast del inventario para Python3.10/3.7 y node --check del acceso sin errores.
- QA de vista real renderizada con datos sintéticos en navegador local: sólo campo Email y botón, sin selector visible de tienda; sin desborde a1280px. No se ejecutó navegación HTTPS completa entre dominios ni envío SMTP real.
- PDF principales:233 páginas Urban y16 MiDistri, capítulo nuevo delante y páginas anteriores conservadas. Portadas y uniones renderizadas e inspeccionadas. Poppler avisó por fuentes del contenido histórico; las páginas vigentes/unión inspeccionadas son legibles sin recortes.
- Revisión independiente y su pasada de correcciones:ver REVISION_FINAL_v598_v14.md. No se afirma revisión independiente posterior a la pasada.

## Suite histórica general Urban
Se inició la suite consignaciones completa en SQLite local; su resultado y tiempo se agregarán al cerrar la entrega. No se presenta como aprobada mientras esté en curso. Las pruebas nuevas y de concurrencia se ejecutaron también en PostgreSQL, sin usar producción.

## Entrega y aceptación
Urban598 exige base597 y esquema consignaciones0125/bridge0014; agrega sólo bridge0015. MiDistri14 exige base13/esquema0009 y Urban598. Instalar en ese orden. Las banderas, conexiones, productos, precios, saldos, documentos y credenciales se conservan.
Los paquetes contienen inventarios explícitos; se verifican CRC/SHA y correspondencia con el commit publicado al construir los artefactos definitivos. Producción queda pendiente hasta confirmación del usuario. No se cambia el cron ni se envía la campaña.
