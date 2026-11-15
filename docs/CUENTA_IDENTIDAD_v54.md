# MiDistri-Pedidos v54 · Saludo personal y estado de cuenta piloto

## Guía de uso

### Ver quién está conectado
Entrá con tu correo verificado. El encabezado muestra Hola, seguido de tu nombre cuando está disponible. En otro renglón, Vendedor identifica el kiosco activo. Si no hay nombre personal registrado, el saludo muestra Hola.

### Consultar la cuenta piloto
Los perfiles 98 y Cerrutti de Belgrano ven Mi estado de cuenta en el menú. Abrí la opción para consultar los saldos y los movimientos del kiosco activo.

## Detalle técnico

- Instalar Urban Soft v690 antes de MiDistri v54. La ruta conserva la autorización privada por token y devuelve un aviso cuando el servicio no puede entregar el resumen.
- El campo opcional nombre_persona se valida antes de renderizar. El nombre y los permisos del vendedor conservan sus campos de origen. El saludo nunca construye el nombre a partir de un correo.
- Paquete acumulativo desde v50 a v53, sin migraciones. Para revertir, usar --restore con el respaldo de v54. Validar el nombre del contacto, el perfil activo, un acceso sin nombre y la denegación a otro kiosco.

Revisión r2 del paquete: el instalador admite todas las versiones base documentadas. Las comprobaciones de huellas y migraciones siguen vigentes.
