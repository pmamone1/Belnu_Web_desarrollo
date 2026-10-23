# Revisión final y resolución

Una revisión independiente de ambos repositorios se ejecutó sobre Urban0c8fb00..b4f2c9f y MiDistri6734ce8..974f6bc. No encontró defectos Critical confirmados; identificó siete Important. Se realizó una única pasada de corrección por el implementador, como estableció el plan. No se presenta esa pasada como una segunda aprobación independiente.

| Hallazgo | Resolución y evidencia |
|---|---|
| Acceso administrativo borraba el navegador vendedor | Conserva sólo navegador/desafíos al limpiar autenticación heredada; cookie de sesión de navegador y vencimiento administrativo remoto separado. Regresión de entrada/salida y carrito. |
| Respuesta perdida al publicar | CambioPromocional pendiente y contenido durable antes de llamar Urban; reintento explícito con UUID/revisión congelados tras recargar. Regresión timeout, repetición e intento alternativo bloqueado. |
| Retiro del producto dejaba promoción | FK de origen y verificación de publicación/material vigentes al representar; se conserva fuente al editar. Regresión baja/producto/recurso. |
| Elección al final del OTP | Pendiente pasa al plazo120s del ticket después de verificar; OTP sigue1800s. Regresión1799->1801s. |
| Campaña20/65 copiaba remitente al editar | Bases propias congeladas y overrides explícitos; regresión del formulario/servicio con nombres y Reply-To distintos. |
| Salir sin red no reintentaba | Cierre pendiente separado de identidad, online/botón de reintento y endpoint local idempotente. Ensayo Node con red caída/recuperada y prueba de doble logout. |
| Sin vista previa privada de promoción | Revisión firmada30min, confirmación separada y archivo reservado por proxy privado de sesión/permiso/alcance. Tests de firma, repetición, archivo PNG y bloqueo ajeno. |

Minor resueltos: reproductor con ancho y altura utilizables; ayuda distingue código30min/enlace48h; texto promocional1000caracteres; acciones Reenviar/Cambiar Email. La galería de video y la revisión privada se comprobaron también en navegador local con datos sintéticos.

Validación final: Urban195/195 focales en PostgreSQL17.11; portal109/109 suite completa en SQLite/Django3.2; ensayo JavaScript offline/online verde. Instaladores16/16 por aplicación y plan real de migraciones sin ejecutar reversiones. Los conteos incluyen regresiones heredadas; no equivalen a cubrir toda la aplicación Urban. La suite histórica amplia tiene incidencias previas documentadas en INCIDENCIAS_SUITE_v584.

Límites: causa exacta del antiguo error en el navegador del usuario no identificada; no se usó producción ni SMTP real. No hay ejecución nativa Python3.7/3.10 ni MariaDB en este equipo: comprobación AST y ensayos locales no los certifican. Instalación/activación y prueba productiva siguen pendientes. No se envía la campaña.

Cambio ajeno forgotPassword excluido. No se descartaron requisitos funcionales; cerrar/restaurar pestañas no puede prometer revocación infalible por el comportamiento del navegador, ya informado en la guía. La publicación de código y ZIP no confirma instalación.
