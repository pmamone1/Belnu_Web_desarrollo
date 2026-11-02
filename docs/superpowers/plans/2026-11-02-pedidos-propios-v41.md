# Pedidos propios v41 - Plan de implementación

> Ejecución autorizada del contrato de integración acordado por el coordinador. Mantener el worktree y las modificaciones ajenas.

**Objetivo:** Leer la extensión opcional estricta de pedidos consignados propios y presentar fecha de débito/devolución por producto, conservando DTO/históricos legados y marca v40.

**Arquitectura:** Extender modalidades.py con dos formas exactas del DTO. contract.py pasa los productos alcanzados. La presentación genera exclusivamente campos informativos por producto para historial/detalle. La descarga PDF continúa intacta.

**Tecnología:** Django existente/Python3.7, pruebas SQLite sintéticas, Playwright, ReportLab/pypdf y paquete revisado sobre39/40.

- [x] Escribir pruebas que fallen para extensión propia, privacidad/errores, compatibilidad y pantallas.
- [x] Validar extensión opcional completa, días14, fechaISO, lista única flagsbool y ANY; mantener forma antigua exacta.
- [x] Presentar fecha de débito y devolución porproducto sin inferir salidas/obligaciones. No crear importes ni mutar históricos.
- [x] Regresión completa, marca y QA visual tres anchos; revisar manual nuevo+unión histórica.
- [x] Preparar docs/manual/VERSION/CAMBIOS/checklist y paquete acumulativo49archivos40+archivos41; bases39/40, sin migraciones.
- [ ] Revisión independiente antes de commit/push; sólo luego publicar y copiar ZIP final aDownloads con comandos cPanel.
