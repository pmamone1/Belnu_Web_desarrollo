# Validación MiDistri Pedidos Online v3
RED: 2 fallos en19 casos antes de corregir la cabecera.
GREEN: 19/19 de toda la suite del portal.
Los POST HTTPS con token y origen interno pasan; sin token, con origen externo o null se rechazan.
Reproducción de navegador Urban local: antes403 Origin:null; después guardado302 y mensaje de éxito.
Datos sintéticos; sin operación económica ni Email de prueba en producción.
Instalador9/9; Django check y makemigrations --check --dry-run: correctos, sin cambios.
PDF principal actualizado y unión visual revisada; páginas anteriores conservadas idénticas.
Inventario explícito, sintaxis mínima y hashes del ZIP se verifican en el generador de entrega.
Se conserva la limitación global de v580 (233 fallos,438 errores y56 omitidas en la
batería ampliada anterior; comparación global v579 interrumpida). No se afirma suite global verde
ni homologación productiva. No se repite esa batería ajena al cambio de dos cabeceras.
