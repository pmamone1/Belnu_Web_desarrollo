# MiDistri v5 — catálogo con presentación opcional
Fecha: 22/10/2026. Código preparado; instalación productiva pendiente.
Base exacta: MiDistri v4, commit43ae0875f80d13857efa810385cc10a027763e85.
Urban Soft v583 se conserva sin modificación ni paquete adicional.

## Comportamiento
El campo Display de Urban es opcional y permite el entero0. El consumidor
rechazaba todo el catálogo por ese dato, aunque nombre, foto y precios fueran válidos.
MiDistri convierte exclusivamente el entero0 en None al preparar su copia local.
No modifica el payload original, productos maestros, precios, PVP, fotos, stock,
pedidos, cargos, documentos, perfiles, permisos, conexiones o claves.

None y enteros positivos se conservan. Booleanos, texto, negativos y fracciones
siguen rechazados. Las demás validaciones de catálogo se conservan.
Un error sigue preservando transaccionalmente la última copia válida.

## Uso e instalación
Instalar solamente el paquete MiDistri v5 en belnuweb con su Python3.7.
No requiere nuevas dependencias ni nuevas migraciones; el instalador exige
midistri_portal0003 ya aplicada y un plan vacío. No ejecuta migrate.
Verifica hashes v4, respalda código, check, makemigrations --check y reinicio.
No activa variables ni envía Email, publica productos o genera accesos al instalar.

Después de instalar, desde el panel pulsar Actualizar copia del catálogo,
o ejecutar con Python3.7: manage.py midistri_sincronizar.
La sincronización actualiza sólo la copia comercial de MiDistri. Los productos
se publican/ocultan desde Urban o el panel; los cuatro productos Esferas
indicados por el usuario deben permanecer sin publicar hasta revisar sus precios.
Fotos existentes, precio vendedor y PVP provienen de Urban; no cargarlos de nuevo.

## Compatibilidad y recuperación
Sin cambios de modelos, rutas, esquema, permisos ni documentos históricos.
Se conserva compatibilidad de Python3.7 y Django3.2.
Puede restaurarse únicamente el código respaldado de v4 desde este instalador,
sin revertir base ni copia comercial; v4 volvería a rechazar un snapshot con cero.
Conservar evidencia y corregir hacia adelante cuando sea posible.
No tocar SIB2, venv de Urban, credenciales ni datos de producción por intuición.

## Validación
RED reproducido con un snapshot sintético de20/65 y Display0; dos pruebas fallaron.
GREEN:41 pruebas del portal. Valores0 quedan None; precios25000/PVP30000 se
conservan y el input permanece idéntico; datos inválidos conservan copia anterior.
14 pruebas del instalador de código, incluido no ejecutar migrate y rechazar
planes ajenos/reversiones. Check y makemigrations locales limpios.
No se ensayó con Python3.7/MariaDB reales en este equipo; sintaxis3.7 se comprueba
al construir el ZIP. Producción y sincronización completas pendientes del usuario.

Preflight real sobre SQLite sintético con esquema0003: plan vacío y SHA de la base idéntico antes/después. PDF principal actualizado a6 páginas: nueva página vigente y5 anteriores preservadas; unión revisada visualmente. ZIP por inventario explícito, CRC y hashes verificados al construir.

Revisión final: el preflight de esta versión sin migraciones consulta todas las hojas del grafo y exige plan vacío. La regresión ejecuta el script generado con el algoritmo de Django; detectó el fallo antes de la corrección y pasa después.
