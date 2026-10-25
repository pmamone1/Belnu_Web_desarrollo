# Instalación MiDistri-Pedidos v20

Instalar Urban603 primero. Base exacta portal19; paquete midistri_pedidos_v20_cantidades_ventas.zip. Subir a /home/mcollini, comprobar SHA256 y unzip -t, extraer en staging privado. Ejecutar con /home/mcollini/virtualenv/belnuweb/3.7/bin/python instalar.py --root /home/mcollini/belnuweb, primero sin --apply y después con --apply. Verifica esquema base portal0010, hashes y plan vacío, respalda código, collectstatic y reinicio. No instala ni modifica Urban ni venv.

Sin migraciones, variables ni cambios de remitentes. No registrar otro cron: el existente recalcula y sincroniza cada5min. Restauración de código desde respaldo, sin reversión de base ni históricos. Si un control falla, detener y conservar salida; no saltearlo. Instalación productiva y prueba HTTPS pendientes; sin campaña.
