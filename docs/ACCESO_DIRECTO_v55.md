# MiDistri v55 · Acceso por enlaces directos

## Guía de uso

### Abrir un remito o el estado de cuenta
Desde el menú, ingresá a Mis remitos o Mi estado de cuenta. Si abrís el enlace directo en una pestaña nueva, MiDistri comprueba primero el acceso de esa pestaña y después muestra el contenido del kiosco activo.

## Detalle técnico

MiDistri v55 se instala sobre v54 con Urban Soft v690. La pantalla de acceso puede renderizarse desde middleware antes de que exista request.user. El contexto del carrito legado omite las rutas de MiDistri. El carrito del portal sigue mostrando la cantidad que calcula su propia sesión.

Sin migraciones. El instalador genera un respaldo del código y admite --restore con ese respaldo. Verificar en una pestaña nueva los enlaces /portal/remitos/ y /portal/estado-cuenta/, el cambio entre los dos vendedores del piloto y el contador del carrito.
