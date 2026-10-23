# Validación MiDistri-Pedidos v9

- Suite Django completa con midistri_portal.test_settings: 114 pruebas OK, 1,233 s.
- Instalador independiente: 17 pruebas OK, 0,686 s. Ensayos en carpetas temporales, no producción.
- Django check sin incidencias; makemigrations --check --dry-run: sin cambios.
- Revisión independiente del diff galeria.js: sin hallazgos. Sólo controles y teclado cuando hay más de un recurso; Cerrar, Escape y foco conservados.
- QA real de navegador sobre plantillas renderizadas con datos sintéticos y API externa desconectada: foto única sin Anterior/Siguiente ni miniaturas; dos fotos y enlace YouTube con tres miniaturas, navegación y enlace correcto al seleccionar el tercero. Captura visual sin recortes.
- Manual: 11 páginas, capítulo vigente delante; diez páginas previas conservadas por contenido y unión inspeccionada.
- Python local3.12/Django3.2; constructor valida sintaxis Python3.7. Runtime productivo y prueba del usuario después de instalar: pendientes.

## Caso del video informado
Se consultó el catálogo público de Belgrano: Alma de Campeon (Chocolate) muestra dos fotos y cero videos recibidos; última sincronización informada por la pantalla: 23/10/2026 02:11. El enlace figura en Productos según el usuario. El diagnóstico del usuario confirmó video2 activo, publicaciones19/68 activas y ningún MaterialPublicable activo. Falta publicación expresa y luego sincronización; no es un video recibido que falle al reproducir. Dos ensayos adicionales del procedimiento cPanel en PostgreSQL local: publicación para ambas, repetición sin duplicar y rollback global ante material inesperado (2 pruebas OK; última ejecución de la línea sin sangrías: 0,804s). Su ejecución en producción sigue pendiente de resultado del usuario. No se afirma que ese caso quede corregido al instalar v9; no se publicó material privado ni se reescribió la base para inferirlo.
Los enlaces YouTube/Vimeo siguen abriendo su sitio de origen; v9 no agrega reproducción incrustada ni requiere permisos nuevos.

## Entrega
Base exacta v8 por hashes normalizados de archivos; instalador verifica antes de copiar y respalda código. Inventario cerrado, manifiesto fuente y SHA final se verifican en la entrega; sin media, bases, credenciales o venv. Se conserva el cambio ajeno de forgotPassword.html fuera del commit/ZIP.
Sin migraciones nuevas ni cambios de Urban Soft, SMTP o campaña. La configuración Gmail sigue pendiente: el diagnóstico confirmó sólo los remitentes Belnu existentes, que se conservaron.

El primer comando multilínea del usuario fue rechazado por IndentationError antes de ejecutar sus instrucciones: no se publicó material en ese intento. Se simplificó a una sola línea sin bloques indentados y se verificó el quoting POSIX y los dos ensayos antes de reenviarlo.
