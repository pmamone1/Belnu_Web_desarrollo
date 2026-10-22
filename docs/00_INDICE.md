## MiDistri-Pedidos v4 - Panel de Distribuidor
Instalación pendiente; requiere Urban Soft v583. Entrada desde Urban Soft con
permisos y alcance actuales, sin cuenta staff adicional. Productos y pedidos,
publicación completa con previa y presentación propia por tienda. Precio vendedor
y PVP desde Urban. Migración aditiva0003. Habilitación administrativa explícita;
no publica catálogo ni envía Email al instalar.
Ver [guía vigente](PANEL_DISTRIBUIDOR_v4.md) y [validación](VALIDACION_v4.md).

## MiDistri Pedidos Online v3 - corrección de formularios MiDistri
Corrige el403 CSRF provocado por Referrer-Policy:no-referrer en formularios.
Se usa same-origin: conserva la referencia interna, sin enviarla a otros sitios.
CSRF, autenticación, alcance y permisos se conservan. No hay migraciones,
cambios de importes, datos históricos, claves, venv, cron ni habilitación de envíos.
Instalación productiva pendiente. Requiere MiDistri v2 instalada.
Ver [detalle](CSRF_PORTAL_v3.md) y [validación](VALIDACION_v3.md).

# Índice MiDistri
- [Operación](MANUAL_USUARIO.md)
- [Instalación](INSTALACION_MIDISTRI_PEDIDOS.md)
- [Contrato técnico](INTEGRACION_URBAN580.md)
- [Validación](VALIDACION_INTEGRACION.md)
- [Checklist](17_CHECKLIST_ENTREGA.md)
- [Pruebas manuales](19_PRUEBAS_MANUALES_CRITICAS.md)
