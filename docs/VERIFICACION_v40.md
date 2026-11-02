# Verificación MiDistri-Pedidos v40

## Base y alcance

Rama codex/midistri-marca-v40 sobre 824f5da3b7f8fdb11a9b567e5ffa0c21f031ffe9 (v39). Textos visibles del portal y adaptación exacta de ocho errores conocidos; rutas, contratos y destinos conservados. Error persistido se adapta al presentar, sin escribir histórico. El cambio ajeno templates/accounts/forgotPassword.html se preserva y excluye del inventario/ZIP. No se accedió a datos ni SMTP productivos.

## Pruebas automatizadas

- Ciclo rojo/verde: cinco casos iniciales detectaron la marca anterior en login, error, panel y ApiError/transporte; después pasaron. Un sexto caso detectó error histórico visible, luego pasó con filtro sin reescribir la fila.
- Suite completa: 340 pruebas ejecutadas, OK con 2 omitidas (338 pasan), 14,296 segundos. Comando: tmp/qa_midistri14/Scripts/python.exe manage.py test midistri_portal --settings=midistri_portal.test_settings --verbosity 1. Evidencia tmp/marca40_abreviada_suite.log. Las dos omitidas son previas: bloqueo real PostgreSQL y concurrencia específica MariaDB/MySQL, fuera del motor SQLite de esta corrida; no acredita motor productivo ni SMTP real.
- Instalador/paquete: 29 pruebas OK; corte final 8,984 segundos (tmp/marca40_abreviada_instaladores.log). Comando: tmp/qa_midistri14/Scripts/python.exe -m unittest tools.test_instalar_release_midistri_v40 tools.test_paquete_v40. Evidencia tmp/marca40_instaladores.log. Base39 real comprobada con preflight y aplicación en destino sintético, normalización CRLF, rechazo de core ausente/modificado, restauración y repetición segura.
- manage.py check: sin incidencias. makemigrations --check --dry-run: No changes detected. Ambos con midistri_portal.test_settings. Sin migraciones nuevas.
- Escaneo de todas las plantillas/static activos del portal y templates/static comunes: sin la palabra Urban (incluidas formas abreviadas), verificación sin distinguir mayúsculas. Se añadieron regresiones de plantillas/recursos y literales de mensajes/errores; ambas fallaron antes de corregir las referencias abreviadas y pasan luego. En fuentes quedan comentarios internos y claves exactas del mapa de mensajes heredados, sin exposición de marca estática en UI. Nombres de configuración, URLs reales y documentación histórica se conservan.

## QA visual local

Fixtures locales en tmp/qa_marca40.py y Playwright tmp/qa_marca40.cjs. Login, callback inválido (403) y panel con tienda autorizada/permiso insuficiente a 1440, 390 y 320 px: nueve capturas, texto neutro, sin desborde horizontal ni errores JavaScript. Solicitudes externas bloqueadas. Inspección visual de login390, error320 y admin1440 completada. No acredita el envío de código ni la autenticación productiva.

## Manual principal

Manual_MiDistri_Pedidos_Online.pdf: 42 páginas = una nueva vigente + 41 de v39. tools/actualizar_manual_v40.py compara streams/texto de cada página histórica con Git y los conserva. Páginas 1 y 2 renderizadas con Poppler e inspeccionadas visualmente: guía legible y unión preservada. Poppler reportó fuentes Symbol/ArialUnicode ausentes del historial sin afectar el texto de la guía nueva. El aviso vigente establece prioridad sobre instrucciones/capturas antiguas de marca; no se reescriben páginas históricas.

## Entrega

Inventario explícito tools/release_files_v40.json; paquete incremental sólo para base39. ZIP candidato en output/midistri_pedidos_v40_marca.zip; su manifiesto identifica el HEAD usado al construir y producción pendiente. El coordinador debe reconstruir desde commit publicado para la entrega final. Inventario ampliado: 49 payloads y 51 entradas de ZIP. No incluye forgotPassword.html, credenciales, bases, media privada, tmp ni entornos. Producción, publicación GitHub y copia final a Downloads pendientes y separadas. Sin nuevas campañas ni respaldo SQL completo generado. No se incrementan instalaciones confirmadas por crear este paquete.

## Revisión de referencias abreviadas

Se corrigieron también «Guardado en Urban» en aviso de publicación y pantalla Productos, y «Los archivos que Urban ya haya autorizado» en publicación pendiente del editor. Dos textos administrativos de comandos usan conexión/cola de la distribuidora. Se conserva el texto de productos/tiendas y las identidades de URL. Escaneo r"\burban\b" sobre vistas/recursos; Playwright repite las nueve comprobaciones con ese patrón ampliado.
