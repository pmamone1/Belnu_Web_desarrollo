# Comparación de la suite histórica Urban598 contra597

La suite general consignaciones ejecutó3294 casos en SQLite/Python3.12/Django5.2.15 local, durante2057,584s:271fallos,461errores y59omisiones. No es una suite global verde.
Se extrajeron697 casos históricos distintos con incidencias y se repitieron sobre el commit597 exacto6f7b71ca3393501f837fea6922af8235f91f3d2d, exportado en tmp/baseline598, con su propio cwd y baseSQLite:697 casos en92,476s, los mismos271fallos/461errores.
Se compararon las cabeceras completas (incluidos parámetros de subtests) y sus repeticiones:las732ocurrencias son idénticas. No hubo incidencia de pruebas598 en la ejecución general. No se interpreta esto como aprobación de las funcionalidades históricas ni se afirma que todas las limitaciones tengan una sola causa.
Hay fixtures antiguos que chocan con unicidad por distribuidora, permisos endurecidos o condiciones del runtime/backend. El inventario exacto está en BASELINE_FALLOS_v598.json; no se ocultan las incidencias como si fueran pasos aprobados.
La pasada final del nuevo ingreso, API, operadores y alcance se ejecutó aparte en PostgreSQL:109casosOK, incluidos uso único concurrente y aislamiento de traslado. La suite completa del portal:157casos,156OK/1omitido. Ver VALIDACION_v598.md.
No se utilizó producción ni se cambiaron datos reales durante esta comparación. Las correcciones finales de reenvío y traslado tienen su propia evidenciaRED/GREEN; no se atribuye al proceso general iniciado antes de ellas una ejecución del árbol final completo.
