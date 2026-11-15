# MiDistri v53 · Piloto de Mi estado de cuenta

## Guía de uso

### Abrir el resumen del kiosco
Entrá con el perfil de tu kiosco y tocá Mi estado de cuenta. Durante el piloto esta opción aparece en los perfiles 98 y Cerrutti de Belgrano. Al cambiar de perfil, la consulta sigue al kiosco que quedó activo.

### Revisar un movimiento
Tocá el movimiento para ver su importe y los saldos acumulados. Si hay un remito disponible, podés abrirlo, imprimirlo o descargarlo en PDF. Usá Más antiguos para recorrer los movimientos anteriores.

### Cobro en la distribuidora
Si figura un traslado, ese importe se cobra en tu cuenta con la distribuidora. Un saldo de $0 en esta pantalla sólo indica que el importe ya no está pendiente en esta cuenta.

## Detalle técnico

Instalar Urban Soft v689 antes de MiDistri v53. El backend revalida distribuidora, conexión y vendedor con el token del kiosco. La ruta de MiDistri muestra el menú sólo cuando el perfil autorizado informa cuenta_disponible. La respuesta se verifica contra la identidad activa y se sirve con Cache-Control private, no-store.
Los enlaces a PDF se verifican en Mis remitos, que confirma sesión, kiosco y propiedad de cada documento. Los ajustes y pagos con referencia sin PDF se despliegan como movimientos de cuenta. El piloto es de sólo lectura y puede desactivarse en Urban Soft. Sin migraciones nuevas. Instalación productiva pendiente.
Para restaurar, usar el respaldo de código generado por el instalador v53. Validar en QA los dos perfiles habilitados, otro perfil con el mismo nombre en otra distribuidora, el cambio entre kioscos, acceso directo a la URL, enlaces propios y el aviso con saldo $0.
