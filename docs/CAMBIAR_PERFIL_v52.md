# Cambiar de kiosco · MiDistri v52

## Guía de uso

### Elegir otro kiosco
En el menú, tocá Cambiar perfil. Elegí el kiosco y pulsá Continuar. Si el dispositivo ya tiene acreditados los dos kioscos, el cambio no requiere otro código. Al entrar, el encabezado muestra el kiosco activo; Mis pedidos y Mis remitos corresponden a ese perfil.

### Cuando falta un kiosco
Si ves un solo perfil o el dispositivo todavía no está reconocido, verificá el Email con el que accedés a tus kioscos. Elegí el perfil cuando termine la verificación. Si el kiosco sigue faltando, revisá con tu distribuidora que el Email esté habilitado para ese perfil.

## Detalle técnico

MiDistri v52 se instala sobre v50 o v51. Incluye el filtro de devoluciones de v51 y usa el mismo contrato de acceso de Urban Soft. No incorpora migraciones. Si se parte de v50, Urban Soft v679 es necesario para aplicar el filtro Devolución a ambos tipos de remito.

El POST recordado con elegir=1 omite la selección automática de un único perfil y conserva el acceso actual hasta que haya una selección validada. Los pedidos y remitos se consultan con el token del perfil elegido. Se usan el dispositivo reconocido y la prueba de la pestaña para validar el cambio. Sin dispositivo reconocido se mantiene disponible el ingreso por Email. La habilitación de un kiosco nuevo requiere la verificación ya existente, con las comprobaciones de cliente y proveedor de identidad.

Al cambiar de kiosco se aplica el aislamiento de sesión existente. El carrito y los filtros del kiosco anterior no se trasladan al nuevo. Otras pestañas con sesión propia conservan su identidad en un cambio mediante el dispositivo recordado. La recuperación por Email sigue el circuito habitual de alta del dispositivo. Si se restaura el respaldo del instalador, recopilar los estáticos y validar el retorno a la versión base.

Validar en ancho móvil y escritorio el menú, la elección entre dos kioscos, el caso de un único perfil y el caso sin dispositivo reconocido. Luego de cambiar, comprobar encabezado, Mis pedidos y Mis remitos.
