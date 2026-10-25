# Plan de corrección y verificación — 25/10/2026

Cambios autorizados: corregir cobertura del ranking histórico sin tocar documentos, selector de cantidad compacto, columna de salidas abiertas/en devolución y orden por ventas totales Urban. Se mantienen alcance por distribuidora, precios y remitentes. La confirmación de estados abiertos/en devolución vino del usuario.

1. Reproducir omisiones históricas, duplicaciones y contradicciones en PostgreSQL local antes de corregirlas.
2. Leer y conciliar remitos completos contra sus ítems, con prioridad de snapshots y controles; no publicar ranking cuando la cobertura sea incompleta.
3. Añadir columna con consulta en lote y permiso salidas.ver. Añadir posición completa compatible y orden ventas, con cantidad visual compacta.
4. Regresión local, navegador real con datos sintéticos, revisión independiente y controles de instalador.
5. Manual/PDF, inventario, commits y ZIP separados; producción y campañas pendientes.
