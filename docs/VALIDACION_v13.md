# Validación v13
Implementación local; instalación productiva pendiente. Campaña no enviada.
- Suite completa midistri_portal:150 pruebas,1omitida, todas las ejecutadasOK; tmp/v13_review_green.log.
- Tests nuevos de acceso, callback con tienda firmada, dos pestañas, cuenta sin permisos, tienda ajena y código ligado a tienda observadosRED y luegoGREEN.
-22 tests de instalador/paquete real: OK, contra bases8/9/10/11/12. Rechazo de archivo crítico ausente o modificado; preflight sin escrituras y aplicación/restauración en carpetas temporales.
- Ast de paquete valida sintaxisPython3.7. Runtime de pruebas localPython3.12 conDjango3.2.15; no se afirma ejecución del runtimePython3.7 productivo.
- Vista de panel enChrome local390/1440: Configurar MiDistri y Pedidos separados; sin desborde. Manual15páginas, anterior conservado y unión revisada.
- Nueva guíaSMTP reside enUrban; portal no guarda contraseñas ni envía códigos mediante correo global.
- Producción, SMTP/WhatsApp y cPanel pendientes de aceptación. No se modifican banderas, conexión, catálogo ni credenciales al instalar. Se conserva la modificación ajena templates/accounts/forgotPassword.html y se excluye del ZIP.
Revisión independiente completada, hallazgos corregidos en una pasada; suite final150OK/1omitida. Ver REVISION_FINAL_v594_v13.md para decisiones y límites. No se realizó segunda revisión independiente.
