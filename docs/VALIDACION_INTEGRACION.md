# Validación MiDistri Pedidos Online v2 — 22/10/2026
Base cPanel revisada10b49c4267fb234cd02791dfcdbac9f578da8a6c; propuesta2eea423 adaptada.
QA local Django3.2.15/Python3.12/SQLite:17/17 pruebas del portal,9/9 del instalador.
Django check y makemigrations --check --dry-run: correctos.
Sintaxis mínima Python3.7 revisada al construir cada archivo del ZIP.
API HTTPS local real con certificado verificado, dos procesos y dos bases: catálogo, invitación,
carrito, pedido, OK, Excel sin cargo, emisión duplicada idempotente y descarga PDF LIN/VV correctos.
SMTP apagado; ningún mensaje real enviado.
Catálogo anónimo verificado en navegador: sólo PVP.
Python3.7 real y motor de base del cPanel no ejecutados aquí; instalación productiva pendiente.
La aplicación nueva agrega0001–0002, sin tocar store ni migraciones aplicadas.
ZIP contiene sólo inventario explícito; media, secretos, bases, entornos y datos QA excluidos.
La batería global de Urban tiene fallos existentes y se documenta en su propio repositorio;
no se declara aprobada por las pruebas de este portal.
