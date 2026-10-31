# Verificación final - editor y pedidos

Código preparado y probado localmente el31/10/2026. No acredita instalación productiva.

- RED observado antes de implementar: fuentes retiradas bloqueaban guardado HTTP400, botón público presente y nuevos módulos inexistentes.
- Suite portal:298 pruebas, OK,2 skips existentes de motor. Proyección legacy y render No informado:4 pruebas OK.
- Navegador Chromium local con base sintética en memoria: borrar/deshacer/rehacer, protección del catálogo, dos fuentes/tamaños independientes, aviso seleccionable, tabla y detalles en1440/390/320. Sin desbordamiento horizontal ni errores JS.
- Contraste de tabla en claro/nocturno/azul/verde, PC y320: >=4.5. Se reprodujo RED nocturno1.124 antes de usar variables del tema.
- Instalación local con rutas temporales y comandos de aplicación simulados: portal28 pruebas y Urban27, preflight sin escritura, aplicación idempotente, hashes, respaldo/restore, rechazo de base diferente/archivo faltante/paquete alterado. La prueba no ejecuta una instalación productiva ni sustituye su verificación posterior.
- Manuales principales: portal35 páginas y Urban260, capítulo vigente delante. Conservación byte a byte de contenidos de páginas antiguas verificada por el generador; páginas1/2 renderizadas e inspeccionadas visualmente.
- Revisión independiente final sin críticos. Corregidos: contraste nocturno, emitidos legacy sin desglose, inclusión CAMBIOS Urban, protección de contacto en servidor y nota de rollback; también campo clásico obsoleto. Cada fallo de comportamiento fue reproducido antes de la corrección. La revisión no se presenta como una segunda auditoría de los fixes.
- El ZIP contiene sólo inventario explícito; excluye credenciales, bases, media, entornos, temporales y el cambio preexistente de recuperación de cuenta ajeno a esta entrega. Compatibilidad Python objetivo comprobada al empaquetar.

No SMTP ni campañas. No cambios de configuración, cron, datos económicos, documentos históricos o producción. Publicación en GitHub y hashes de los ZIP se comunican con los valores finales de la entrega.
