# Acceso, marca pública y navegación

## Guía de uso
El portal recuerda automáticamente al vendedor después del primer código. El encabezado ya no muestra el botón Salir y olvidar este dispositivo. Cambiar perfil sigue disponible. La eliminación del botón no cambia las rutas protegidas de revocación ni habilita administración por Email.
Si un Email tiene varios perfiles con el mismo remitente autorizado, llega un solo correo de acceso. Si los remitentes son distintos, se mantiene un correo por remitente. El código vale30minutos, un solo uso, y sólo acredita perfiles vigentes; la administración sigue exigiendo Urban Soft.
En Urban Soft, abrir Comunicaciones > Remitentes y canales > Editar el remitente de Email. El campo Nombre público para correos y remitos permite cambiar la marca visible sin tocar SMTP, contraseña ni asignaciones. Con el remitente compartido, el mismo nombre aplica al bloque20/65. Vacío usa MiDistri para ese bloque; las otras distribuidoras conservan su identidad propia. La configuración en servidor admite la clave nombre_publico en su entrada privada.
La marca se usa en los encabezados automáticos de códigos, avisos de pedidos, correos de remitos/devoluciones y en la identidad de remitos que se generan de nuevo. No sustituye palabras en productos ni textos libres escritos por el usuario. No reescribe archivos ya emitidos ni fuentes históricas congeladas. Las colas que ya guardaron un cuerpo conservan ese contenido; revisar pendientes antes de enviarlos si contienen la identidad anterior.
Anterior y Siguiente se ven como botones amplios al pie del catálogo; el contador indica la página actual. Conservan búsqueda, categoría y orden. En celulares el contador se ubica encima de los botones, sin recortar los controles.
Al recuperar el acceso recordado aparece un spinner junto al mensaje de espera. Si hay un error desaparece y se muestra Reintentar. Si el equipo solicita movimiento reducido, el indicador permanece estático.

## Detalle técnico
Urban agrupa por ingreso_id y remitente_id, nunca por la dirección SMTP. Reclama el grupo bajo bloqueo del ingreso y valida por distribuidora identidad original/actual y remitente actual. SMTP ocurre fuera de la transacción. Un resultado compartido acredita sólo los integrantes todavía válidos; las filas representan alcances, no cantidad de correos. No se persiste el código en claro, no hay fallback ni reintentos automáticos. Remitentes distintos conservan independencia, incluso si otro grupo falla.
El nombre público es una clave adicional de la configuración cifrada del remitente; no requiere cambios de esquema. La lectura no cambia la identidad interna, el alcance, los snapshots ni los precios. El filtro nombre_publico se aplica sólo a identidad documental conocida. Los textos y variables de WhatsApp se conservan.
El portal cambia base.html, catalogo_productos.html, temas.css y recordado.js. Usa role=status, aria-busy y aria-hidden para el spinner; respeta prefers-reduced-motion. Paginación con rel prev/next, aria-current y foco visible. Las rutas y el contrato privado no cambian.

## Compatibilidad, instalación y rollback
Bases exactas: Urban622 y MiDistri30, confirmadas por los registros del usuario. Instalar primero Urban623 y luego portal31. No hay migraciones nuevas; se exige bridge0020 y portal0014 ya aplicadas y un plan de migraciones vacío. No activar nuevamente banderas, modificar cron, sincronizar catálogo ni rotar credenciales. El instalador realiza respaldo privado sólo del código reemplazado y detiene/reinicia su propia Python App.
Si hay diferencias no revisadas, el instalador se detiene antes de copiar. No forzar sobre archivos personalizados. Se puede restaurar sólo código de este paquete mediante su instalador --restore y la ruta exacta del respaldo impreso; se verifican huellas y pertenencia. No revertir migraciones, saldos ni snapshots. Mantener intactas las variables de entorno y las otras configuraciones de canal. Un nombre público guardado después de instalar permanece en la configuración cifrada al restaurar código; el código anterior lo ignora.

## Validación y estado
Pruebas locales con SMTP en memoria y datos sintéticos. No se envían correos reales ni campañas. La instalación productiva de623/31 y su comprobación en el sitio real quedan pendientes de que se ejecuten los comandos entregados.

## Revisión final de recuperación
El rollback del portal exige el esquema coherente ya instalado en30 y regenera los estáticos publicados desde las fuentes restauradas con collectstatic --clear antes de iniciar. No elimina media, registros ni migraciones. Los ensayos locales compararon también los bytes servidos. Ver el informe de revisión de esta entrega.
