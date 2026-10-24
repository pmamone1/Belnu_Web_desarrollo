# Validación v15

Suite completa midistri_portal:157casos,156OK y1omitido. Nueve pruebas JS del código:OK; RED inicial con seis fallos funcionales antes de implementar. Se verifican pegado, autofill, solicitud única, fallo sin bucle, reenvío y perfiles múltiples.

Pruebas locales con datos sintéticos; sin SMTP real, sin permisos nuevos ni campaña.

- Instaladores y paquetes: Urban23OK y MiDistri23OK, contra archivos de las bases598/14. Preflight sin escritura, rechazo de base alterada/ausente, respaldo/aplicación/recuperación en temporales y rechazo de migración ajena pendiente.
- Django check y makemigrations --check: sin errores ni cambios pendientes. AST de inventarios para Python3.10/3.7; JS probado en Node y navegador local. No se afirma ejecutar Python3.7 del servidor.
- Reproducción en navegador local: no-referrer envió Origin:null/Referer ausente; origin envió origen válido y referencia sin ruta/query. La regresión HTTPS del cliente Django acepta token/mismo origen y rechaza null/ajeno/token ausente/replay.
- UI renderizada real con API sintética: código grande visible; completar seis números hizo una sola verificación y navegó sin pulsar Entrar. No se pidió acceso real al portapapeles del usuario ni se usó una cuenta productiva.
- PDF principales:234páginas Urban y17MiDistri. Capítulo nuevo y unión con primera página histórica renderizados e inspeccionados, sin recortes; contenido previo verificado sin cambios de streams. Avisos de fuentes históricas Poppler heredados no afectan esas páginas inspeccionadas.
- Revisión independiente:un P2 de validación incompleta del plan del instalador MiDistri fue reproducido con RED, corregido y pasóGREEN. Revisor confirmó la corrección, sin hallazgos abiertos. Detalle en REVISION_FINAL_v599_v15.md.

Instalación productiva, entrega SMTP real, navegación HTTPS entre dominios y comportamiento clipboard/autofill del móvil quedan pendientes de aceptación después de instalar. No se declara prueba global de producción ni se habilita DEBUG. No hay nuevas migraciones, cambios de SMTP/WhatsApp, envíos ni operaciones económicas.
