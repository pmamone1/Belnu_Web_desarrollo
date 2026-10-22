# Pruebas manuales MiDistri
Comprobar móvil: enlace GET no consume, POST entra y muestra sólo catálogo de su distribuidora/LIN/VV.
Anónimo sólo ve PVP. Cambiar precio antes de envío exige revisar; conexión fallida conserva UUID.
Reintentar mismo pedido no duplica cargo; otro vendedor no ve pedido/remito. HTML de error no se descarga como PDF.
Comprobar cancelación stock y preparación con remito nativo. Flags/Email apagados no envían.


### Contrato v2 y recuperación
SKU80 debe sincronizar y regresar en el pedido recibido sin quedar pendiente. SKU81 se rechaza.
Verificar recuperación de copia parcial y rechazo de respaldo alterado.
Homologación real Python3.7 y motor del servidor pendiente; no se habilitan flags ni envíos al instalar.
