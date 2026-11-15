# MiDistri v58 · Navegación y movimientos de cuenta

## Guía de uso

### Consultar sin perder la pantalla
El indicador de carga acompaña las consultas, filtros, páginas, remitos en PDF y cambios del carrito. Si falla una consulta, MiDistri conserva la vista y muestra un aviso para que puedas volver a intentar.

### Leer el estado de cuenta
La tabla presenta el saldo anterior, la fecha y la referencia de cada movimiento, las variaciones y los saldos consignado, vencido y total después de cada operación. En el celular podés deslizar la tabla para ver todas las columnas. Abrí Comprobantes desde el movimiento correspondiente.

## Detalle técnico

- Mantener el transporte autenticado por pestaña y la validación de CSRF. Mostrar progreso hasta terminar de leer o aplicar cada respuesta, sin incluir la telemetría.
- Cargar la navegación del vendedor, filtros, paginación y visor de PDF en el documento actual. Conservar el recorrido Atrás y Adelante.
- Mostrar el saldo anterior y los movimientos en el orden que devuelve la API de Urban Soft. Calcular el saldo total de cada renglón con los dos saldos acumulados.
- Validar errores de consulta, clics sucesivos, apertura de un PDF y renderizado del detalle de un pedido después de navegar por AJAX.

Instalación sobre MiDistri v57. Sin migraciones. El instalador respalda el código y admite restaurar el respaldo con --restore. Los permisos y los importes de Urban Soft se consultan mediante las rutas vigentes.
