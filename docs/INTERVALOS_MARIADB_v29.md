# MiDistri-Pedidos v29 · Intervalos compatibles con MariaDB

## Guía de uso
La instalación de Urban Soft 621 y MiDistri 28 quedó confirmada por la salida aportada por el usuario el 30/10/2026. El contrato de analítica se verificó y la captura quedó activa con 4 intervalos abiertos. No se presume que haya duplicados ni se afirma haber inspeccionado la base productiva.
Esta corrección se instala sólo en MiDistri, sobre v28. Urban 621 se conserva. No es necesario volver a activar la medición: mantiene el estado que ya tenía, sus fechas y eventos. La pantalla de Estadísticas sigue igual.
La advertencia models.W036 indicó que MariaDB no creó la protección condicional de intervalos. Se reemplaza por una clave única ordinaria, compatible con MariaDB, que permite un solo intervalo abierto por tienda y conserva todos los cerrados.
Antes de actualizar, el instalador consulta si existen abiertos duplicados. Si encuentra alguno, se detiene sin fusionarlo ni borrarlo. Compartí la salida para resolver ese caso conservando las evidencias; no fuerces la instalación.
La advertencia mysql.W002 corresponde al modo estricto de la conexión: es independiente y puede seguir apareciendo. Esta entrega no cambia SQLMode ni parámetros del servidor. Los avisos de archivos admin/js duplicados tampoco impidieron la instalación anterior y no se silencian globalmente.
Después de instalar, el comando de diagnóstico de sólo lectura confirma la captura, cuenta los intervalos abiertos y verifica que el índice único ordinario existe realmente. No manda correos ni cambia datos. El cron actual sigue igual.

## Detalle técnico
Modelo IntervaloAnalitico: marcador abierto_unico=1 para abierto y NULL para cerrado. UniqueConstraint ordinaria(distribuidora,abierto_unico), más CheckConstraint para exigir coherencia con hasta. save actualiza el marcador; el cierre masivo libera el marcador en la misma actualización. No cambian las fechas ni las fuentes del tablero.
Nueva 0013_intervalo_unico_portable; 0012_analitica aplicada se conserva byte por byte. Valida duplicados antes del primer DDL, agrega el marcador, rellena 1/NULL según el estado existente y reemplaza la restricción parcial por las dos restricciones ordinarias. No elimina intervalos, eventos, evidencias, consultas, vendedores ni pedidos; no altera ControlAnalitica.activa.
Preflight exige las capacidades de coherencia del motor y ausencia de abiertos duplicados. Repite la comprobación después de detener la aplicación, antes de copiar. El plan permite sólo 0013 hacia adelante y se detiene ante migraciones ajenas o retrocesos.
MariaDB no ofrece rollback transaccional de DDL. Si una migración falla parcialmente, conservar salida y respaldo de código y preparar recuperación hacia adelante; no repetir a ciegas ni restaurar v28 después de0013. El instalador bloquea esa restauración si 0013 figura aplicada o si detecta la columna nueva aunque el registro de migración todavía no exista. El preflight también detiene ese DDL parcial antes de copiar o detener la aplicación.
Las restricciones no dependen de activar StrictMode. Se validan en MariaDB local sin modo estricto, además de la regresión SQLite y el plan real de migraciones. No se usa producción como entorno de prueba.

## Instalación y recuperación
Subir el ZIP v29, verificar SHA256 y CRC, extraer en carpeta privada y ejecutar instalar.py --root /home/mcollini/belnuweb primero sin --apply. Si pasa, repetir con--apply. El instalador conserva el estado de captura y crea respaldo privado de archivos.
Compatible con Python 3.7/Django 3.2 y Urban 621. Sin cambios de venv, conexiones, catálogo, precios, remitentes, WhatsApp, campañas ni cron. Si el preflight se detiene por datos inesperados, no cambiar ni borrar intervalos por intuición.
Código preparado y pruebas locales documentadas en la entrega; instalación productiva de v29 pendiente de confirmación. Se conserva el respaldo de código v28 informado: /home/mcollini/respaldo_midistri_pedidos_vypa2_0k.
Fuentes técnicas: https://docs.djangoproject.com/en/3.2/ref/models/constraints/ y https://mariadb.com/docs/server/reference/data-types/null-values .

## Evidencia de pruebas
MariaDB 10.11.14 portable, fuente oficial y SHA256 verificado, aislado en 127.0.0.1:63403, sin modo estricto: reproducida la falta de restricción de 0012; actualización conserva IDs/fechas/4 abiertos, un cerrado, un evento y captura True; índice y CHECK inspeccionados en motor, duplicado rechazado, reintento sin cambios. Base con 2 abiertos duplicados: detención antes de agregar columna y ambos registros conservados.
Regresión MariaDB: 241 pruebas con 2 omisiones (concurrencia de editor específica de PostgreSQL y fixture antiguo que retrocede DDL); regresión SQLite: 241 pruebas con 2 omisiones (concurrencia PostgreSQL y concurrencia específica de MariaDB). La migración antigua de página sigue ensayándose en SQLite; la nueva se verifica hacia adelante en MariaDB, no con retroceso. Concurrencia de 2 sesiones MariaDB crea un único intervalo.

Instalador y empaquetado: 28 pruebas superadas. Verificación de modelos sin migraciones pendientes. Revisión visual del capítulo vigente y su unión con las 30 páginas anteriores del manual.
