# MiDistri v56 · Acceso recordado desde enlaces directos

## Guía de uso

### Abrir un enlace al portal
Podés abrir Mis remitos o Mi estado de cuenta directamente desde un enlace. MiDistri comprueba tu acceso y abre la página para el kiosco activo. Si la sesión necesita verificarse de nuevo, elegí Entrar con mi Email.

### Revisar el kiosco activo
Usá Cambiar de kiosco para elegir otro perfil asociado a tu acceso. Mi estado de cuenta aparece en el menú de los kioscos habilitados en el piloto.

## Detalle técnico

La pantalla inicial que devuelve el middleware de pestaña pasa por el decorador ensure_csrf_cookie de Django. El decorador carga el secreto previo cuando existe y emite una cookie compatible con los formularios de acceso recordado. Los permisos por pestaña, kiosco y distribuidora siguen aplicándose al consultar remitos y saldos.

Requiere MiDistri v55 y Urban Soft v690 para el piloto. Sin migraciones. El instalador genera un respaldo de código. Para revertir archivos, ejecutar el instalador v56 con --restore y la ruta del respaldo. Comprobar enlaces directos en pestaña nueva, una pestaña previa que continúa navegando y cambio de kiosco.
