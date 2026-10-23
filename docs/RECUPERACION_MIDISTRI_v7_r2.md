# MiDistri v7 r2: recuperación de configuración e instalación

El intento comunicado llegó a copiar los79archivos y detener la aplicación, pero falló en manage.py check al evaluar MIDISTRI_MULTIMEDIA_ENABLED con os no importado. Ese intento no alcanzó la fase de migraciones. No afirmar instalación completa por el marcador VERSION_DOCUMENTADA copiado.

La causa era del paquete v7. La suite usaba test_settings y el control AST sólo comprobaba sintaxis, por eso no ejecutó esa expresión de la configuración productiva. La regresión nueva ejecuta belnuweb/settings.py completo con valores sintéticos, sin leer .env ni conectar a una base. Reprodujo NameError antes de la corrección y pasa con la bandera apagada/encendida.

Corrección mínima: leer MIDISTRI_MULTIMEDIA_ENABLED con env.bool, igual que las otras banderas. No añade dependencias ni cambia venv, credenciales, precios, datos históricos o Urban Soft. No agrega migraciones respecto del v7: conserva0004–0008.

## Instalador y compatibilidad

El paquete r2 completo admite la base v6 y los archivos exactos del v7 publicado en e2e4510554254f00765dc66eb71de3647481f0e4, además de archivos r2 idénticos. Una modificación ajena sigue bloqueando. Las huellas están en el manifiesto; no se pide forzar ni editar hashes.

Si reconoce la huella exacta de settings del v7 interrumpido, la comprobación previa carga sólo en su proceso una copia corregida de ese módulo. Usa el .env y las conexiones configuradas del destino de la misma forma que Django; no imprime secretos ni escribe archivos durante la comprobación. La sustitución en memoria se limita a la única línea conocida y exige de nuevo su hash antes de ejecutar. No oculta otros errores ni evita controles de permisos/esquema.

Al aplicar, primero conserva un respaldo de los archivos que cambiará; después detiene la aplicación, reemplaza los archivos y desactiva esa corrección en memoria. manage.py check y los demás controles posteriores cargan la configuración instalada real. Sólo continúa con el plan de migraciones permitido, estáticos y arranque si los controles pasan. Los destinos siguen siendo las hojas finales; no se revierten migraciones.

Conservar /home/mcollini/respaldo_midistri_pedidos_ze9f_6gs del intento anterior. El r2 genera su propio respaldo de archivos; no pide un nuevo respaldo completo de base. No editar settings a mano ni volver a instalar el ZIP v7 original. No restaurar o borrar migraciones por intuición. Si alguna migración0004–0008 ya estuviera aplicada, el rollback de código permanece bloqueado; corrección hacia adelante con funciones nuevas apagadas.

## Pasos del operador

1. Subir midistri_pedidos_v7_acceso_tienda_r2.zip y su .sha256 a /home/mcollini.
2. Mantener las funciones nuevas apagadas. Ejecutar primero la comprobación y después --apply usando Python de belnuweb3.7. Ver COMANDOS_CPANEL_MIDISTRI_v7_r2.txt.
3. La comprobación puede mostrar «Configuración v7 interrumpida reconocida; comprobación con corrección sólo en memoria». No es una modificación del servidor.
4. Sólo «CÓDIGO INSTALADO: midistri-pedidos v7 r2» confirma que terminó el instalador. El marcador de versión por sí solo no lo confirma.
5. Después continuar con Urban585 ya entregado. Su ZIP y commit no cambian. Activar las banderas coordinadamente, reiniciar y sincronizar según las instrucciones originales. La campaña sigue sin enviarse.

## Validación

Reproducción RED del NameError en la configuración real y del rechazo al reintento parcial. GREEN: prueba de configuración real con valores ficticios; pruebas del instalador, incluida ejecución del arranque corregido en un subproceso sin escribir el archivo desplegado; suite completa del portal. Ver VALIDACION_v7.md para los resultados finales. AST de destino Python3.7, ZIP/CRC/SHA e inventario contra commit comprobados antes de entrega.

No se ejecutó en este equipo el Python3.7 o MariaDB productivo ni se modificó el servidor. La comprobación en cPanel y la instalación r2 siguen pendientes hasta recibir su salida.
