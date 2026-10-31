# MiDistri-Pedidos v30 - cPanel
Base exacta: MiDistri29/0013. Instalar Urban622 primero. Conservar captura de analítica y canales. Sin campaña.
Subir midistri_pedidos_v30_acceso_recordado.zip a /home/mcollini y verificar el SHA256 publicado en la entrega.

```bash
cd /home/mcollini
STAGING_MIDISTRI30=$(mktemp -d /home/mcollini/staging_midistri30_XXXXXX)
unzip -oq midistri_pedidos_v30_acceso_recordado.zip -d "$STAGING_MIDISTRI30"
/home/mcollini/virtualenv/belnuweb/3.7/bin/python "$STAGING_MIDISTRI30/instalar.py" --root /home/mcollini/belnuweb
/home/mcollini/virtualenv/belnuweb/3.7/bin/python "$STAGING_MIDISTRI30/instalar.py" --root /home/mcollini/belnuweb --apply
/home/mcollini/virtualenv/belnuweb/3.7/bin/python /home/mcollini/belnuweb/manage.py midistri_acceso_recordado_estado
```

Después de ambas instalaciones, agregar MIDISTRI_ACCESO_RECORDADO_ENABLED=True en las variables de AMBAS Python Apps de cPanel y reiniciarlas. No borrar otras variables. Repetir el diagnóstico del portal: habilitado y urban_habilitado deben ser true. La llamada comprueba el contrato remoto, no envía correos ni modifica datos.
El portal requiere HTTPS. Tras un primer código válido, cerrar y reabrir el navegador en el mismo dispositivo: entra sin otro código o permite elegir los perfiles ya acreditados. Borrar cookies exige código. Probar «Salir y olvidar este dispositivo» incluso sin conexión. No probar con datos ajenos ni enviar campaña.
Si falla el preflight o una migración, compartir salida y respaldo de código, sin repetir a ciegas. MariaDB puede dejar DDL parcial; la guarda lo detecta antes de copiar. No revertir0014 ni borrar registros. Desactivar funcionalmente con la bandera False en ambas y reiniciar.
