# Validación local y límites

Producción pendiente. No se usó producción para probar ni se enviaron campañas o Emails a destinatarios reales.

- Código: límites 1799/1800 segundos, cinco intentos, un uso, reenvío, respuesta genérica, contactos múltiples y revalidación. Concurrencia real PostgreSQL17.11 local.
- Integración real de servicios Urban: Email ficticio en locmem -> dos identidades -> pedido10+2 -> preparación6+0 -> cargo150000 -> un único pedido/PDF nativo -> dos destinatarios habilitados. Sesión válida a31min. No hay campaña creada por el ensayo.
- Final después de corregir la revisión: portal109/109 en su suite completa; Urban195/195 focales en PostgreSQL17.11. Ensayo JavaScript de cierre offline y recuperación online verde. Incluye galerías, contratos, sesiones, callback, precios, promociones y flujo económico nativo sintético.
- Instaladores:16 pruebas por proyecto verdes, incluido plan real de MigrationExecutor en estados parciales y final sin reversiones; hashes/raíz/runtime/reintento/restauración y preflight sin copia.
- Navegador local: ingreso por Email, pedido10 a25000, total250000/PVP37500, identidad visible sólo en pestaña autenticada, nueva pestaña anónima, Salir, fotos ampliadas/miniaturas/Escape/foco, tema nocturno y violeta, móvil390px. Ingreso administrativo desde Urban, revisión privada de promoción y reproductor con controles utilizables verificados al finalizar. SMTP sustituido por buzón local. Multimedia de las capturas es sintética; validación de URL y archivos se prueba aparte.
- Entorno de ejecución de QA: Python3.12/Django5.2.15 Urban y Django3.2.15 portal. PostgreSQL17.11 y SQLite locales. No hay MariaDB local ni ejecución Python3.7/3.10 disponible: sintaxis destino comprobada por AST, migración productiva y SMTP real pendientes. No afirmar certificación completa de esos runtimes.
- Suite histórica amplia Urban conserva incidencias anteriores descritas en docs/INCIDENCIAS_SUITE_v584.md; no se presenta como suite general verde. La validación de esta versión es focal y se publican sus límites.

Revisión independiente ejecutada y siete hallazgos Important corregidos en una pasada; ver REVISION_FINAL. Paquetes definitivos se reconstruyen sobre el commit final, con CRC/inventario/hashes y comprobación de fuente. Producción pendiente.
