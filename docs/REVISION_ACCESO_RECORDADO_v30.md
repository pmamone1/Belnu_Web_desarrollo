# Revisión independiente del acceso recordado y correcciones

El revisor independiente examinó ambos rangos completos y encontró tres problemas importantes; ninguno crítico. Se corrigieron en una sola pasada, con reproducciones fallidas y luego aprobadas:

1. Restauraciones simultáneas con la misma instantánea de cookies: devolvían200 pero la primera pestaña terminaba403. Ahora la vinculación usa el dispositivo validado, y restaurar no rota la sesión compartida. Test `test_restauraciones_con_instantanea_de_cookies_no_invalidan_otras_pestanas` con y sin sesión inicial, y prueba HTTPS de dos pestañas concurrentes.
2. Navegación privada pendiente después de un cierre en otra pestaña: podía repintar el historial. La generación de navegación se invalida al limpiar/cerrar y se comprueba después de cada espera, antes de pintar o descargar. Test `test_navegacion_cierre_v30.js` observado RED→GREEN; también prueba salir durante una navegación ocupada.
3. Pestaña obsoleta o perfil retirado podía borrar la nueva cookie válida. Ahora se distingue la credencial inválida de la pestaña/selección, se conserva la confianza de otros perfiles y se actualizan las opciones. Dos reproducciones observadas RED→GREEN; cobertura adicional del retiro durante la llamada a Urban y del OTP que sustituye el dispositivo en la misma pestaña.

Sin menores diferidos. No se hizo una segunda revisión independiente: el proceso acordado verifica las correcciones con tests y regresión completa. Los límites y resultados de motor se detallan en VALIDACION_ACCESO_RECORDADO.

Decisiones revisadas: secreto estable hasta revocación (un secreto robado debe revocarse); conservación física de cookies sujeta al navegador; cPanel/SMTP reales no probados por el revisor; edición ajena forgotPassword excluida y conservada. La nueva solicitud del31/10 sobre campañas se incorporó después: errores y preparaciones interrumpidas no se reintentan; pruebas nativas69/69, sin envíos reales. No se afirma que esa ampliación haya pasado por el revisor del acceso.
