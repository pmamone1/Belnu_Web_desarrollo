# Instalación MiDistri-Pedidos v19

Requiere Urban602 primero. Paquete midistri_pedidos_v19_catalogo_identidad.zip, acumulativo sobre16/17/18. Subir a /home/mcollini, comprobarSHA256 y unzip -t, extraer en staging y usar /home/mcollini/virtualenv/belnuweb/3.7/bin/python instalar.py --root /home/mcollini/belnuweb, primero sin --apply y luego con --apply. Valida archivos/plan, respalda código, pausa, check/modelos, portal0010, collectstatic/reinicio. No toca Urban ni venv, no envía ni publica borradores. Portal0010 conserva indicadores públicos enJSON; resto de mensajes/marca enJSON existente, sin migración de contenido de tiendas.

Después ejecutar el coordinador ya instalado en Urban para actualizar indicadores y sincronizar. El cron existente mantiene5min. Nuevos permisos/variables no requeridos. Configuración de Email/WhatsApp conserva valores y separación por distribuidora.

Si un control falla, no saltearlo; conservar salida/respaldo. No revertir DB ni snapshots/documentos. Restauración automática bloqueada después de0010; usar corrección hacia adelante o restauración revisada de código conservando esquema aditivo. El instalador no confirma recepción de Emails ni aceptación productiva.

Instalación productiva pendiente. Sin campaña.
