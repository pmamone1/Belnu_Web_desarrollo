# Instalación MiDistri32
Instalar Urban624 primero. Preflight de ambos paquetes antes de aplicar. Este paquete admite archivos revisados de30/31; conserva portal0014 y no tiene migraciones nuevas. La instalación no activa ni prepara campañas.
Nuevo cron para obtener primero la previa con la configuración pausada; autorizar envíos sólo después de revisarla: */15 * * * * /home/mcollini/virtualenv/belnuweb/3.7/bin/python /home/mcollini/belnuweb/manage.py midistri_incentivos_preparar
Conservar todos los cron existentes, incluido procesar_campanas de Urban. El nuevo productor no realiza SMTP. Sin configuración activa sólo completa las previas de lectura solicitadas; no encola campañas. Las coberturas incompletas quedan bloqueadas.
