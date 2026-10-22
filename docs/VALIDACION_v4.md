# Validación MiDistri v4
Instalación productiva pendiente. 22/10/2026.
- 37 pruebas de panel, vendedor, contratos, logos, revisión concurrente e idempotencia OK.
- 12 pruebas de instalador en carpetas temporales OK.
- Navegador local con Urban: acceso acotado, publicación y sincronización, mensajes
  de tienda, pedido recibido/OK/revisión/preparación y remito con datos ficticios.
- API y permisos comerciales comprobados en Urban; ningún cargo ni Email productivo.
- PDF propio de 5 páginas: dos nuevas delante; tres anteriores preservadas y unión
  verificada visualmente. Manual Urban de216 páginas también actualizado.
- No se probó intérprete Python3.7/MariaDB real aquí. Runtime de pruebas Django3.2,
  SQLite local; sintaxis3.7 comprobada al construir el paquete. Urban usa PG17.11 local.
- QA del navegador usa HTTP/overrides sólo de desarrollo, no entregados. No hubo
  reducción de seguridad en la configuración productiva ni avisos del navegador omitidos.
Preflight real sobre esquema sintético0002 verificado sin modificar datos.
Revisión independiente completada: restauración postmigración bloqueada y precio negativo administrativo corregidos.
Pendiente: validación en cPanel después de instalar ambos paquetes y aceptación HTTPS.

Regresiones de revisión: restauración bloqueada si cualquier migración nueva está aplicada, conservación de archivos de migración; catálogo admin permite precio negativo corregible y conserva validación de tipos, finitud y límites.

Empaquetado: inventario explícito de 39 archivos de código/documentación/manual, más instalador de entrada y manifiesto. CRC y hashes de todas las entradas verificados. Sintaxis del payload comprobada para el Python productivo de este proyecto. El ZIP final se reconstruye desde el commit publicado; no incluye bases, media, claves ni entornos.
