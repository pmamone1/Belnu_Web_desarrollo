# Belnu Web: reconciliación con cPanel

## Estado y alcance

Fuente: ZIP de `/home/mcollini/belnuweb`, confirmado por el propietario.
Aplicación publicada: `belnu.com.ar/`, Python 3.7.
El propietario confirmó `store` 0001–0017 aplicadas. Se conservan exactamente
las migraciones 0011–0017 del servidor; no se generan migraciones nuevas.

Esta rama incorpora el código, plantillas y JavaScript propios del servidor.
No incorpora bases, datos exportados, imágenes subidas, entornos virtuales,
archivos `.env`, copias de settings ni assets generados del administrador.
Los archivos existentes en Git que no se sustituyen se conservan.

Cambios adicionales mínimos: configuración privada desde `belnuweb/.env`,
DEBUG desactivado por defecto, STATIC_ROOT relativo al proyecto y declaración
de PyMySQL ya utilizado por `belnuweb/__init__.py` del servidor.

## Preparación antes de desplegar

No fusionar ni publicar esta rama hasta validar arranque y pruebas en un entorno
equivalente al servidor. No actualizar Python o Django durante esta conciliación.

1. Respaldar archivos y base desde cPanel, fuera de la carpeta pública.
2. Descargar únicamente `tools/prepare_environment.py` de esta rama y ejecutarlo
   sobre la instalación ANTIGUA, antes de reemplazar `settings.py` o las vistas:

```bash
source /home/mcollini/virtualenv/belnuweb/3.7/bin/activate
python /ruta/prepare_environment.py --root /home/mcollini/belnuweb
```

El script lee asignaciones literales sin importar ni ejecutar la aplicación.
Conserva la SECRET_KEY activa, conexión de base y credenciales SMTP en
`belnuweb/.env`, con permisos 600; respalda el `.env` previo con permisos 600.
No imprime sus valores. No reemplaza código ni modifica la base.
No ejecutarlo sobre el código nuevo: exige los valores literales antiguos.
Las variables del proceso tienen prioridad sobre `.env`: comprobar localmente
que no haya variables de cPanel contradictorias, sin publicar sus valores.

3. Probar la rama en una copia aislada con base de pruebas y correo deshabilitado.
   Conservar el `.env` privado al instalar el código. Verificar dependencias del
   entorno activo; el ZIP contiene otro `env` que no prueba el entorno Python 3.7.

```bash
python -m pip check
python -c "import django, pymysql; print(django.get_version())"
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py showmigrations store
```

No ejecutar `migrate` a ciegas: se espera que 0011–0017 sigan aplicadas.
Probar login, recuperación de contraseña, catálogo, edición, carrito, pedido,
correo y exportación Excel con cuentas de prueba antes de publicar.
Mantener `forgotPassword.html` y `forgotpassword.html`: Linux distingue mayúsculas.

4. Tras validar, fusionar y publicar mediante un procedimiento de despliegue
   acordado. No se ha configurado despliegue automático en esta rama.
   Conservar `.env`, media y base; recopilar estáticos y reiniciar solo al publicar.
   Ante un fallo, restaurar el código respaldado y la configuración correspondiente.

## Verificación efectuada fuera del servidor

- Sintaxis compatible con Python 3.7 comprobada mediante AST.
- Dos pruebas del script con credenciales ficticias: conservación, respaldo,
  permisos privados, ausencia de valores en salida y fallo sin modificar `.env`.
- Migraciones nuevas idénticas a las del ZIP, salvo finales de línea.
- Búsqueda de valores privados originales en todos los archivos propuestos.

Pendiente: arranque Django y pruebas funcionales en Python 3.7/MySQL; este
entorno de trabajo no tiene Django ni las dependencias del servidor instaladas.

## Defectos heredados para una siguiente etapa

No se alteró la lógica de pedidos durante esta captura de la versión publicada.
En `orders/views.py` el precio de línea se acumula y usa una referencia de carrito
de un bucle anterior: requiere pruebas de pedidos con varios productos/recargos.
Las operaciones de pedido/stock no son atómicas; revisar devoluciones tempranas.
En login, las consultas de cuenta activa no filtran siempre el mismo correo.
Revisar permisos de exportación/descarga y datos personales incluidos en URLs.
Estos problemas impiden considerar la captura una modernización funcional.

Hay credenciales históricas en código del servidor. No se copian a esta rama;
conviene rotarlas después de verificar el nuevo método de configuración.
La exclusión de datos nuevos no elimina datos o secretos del historial de Git.
