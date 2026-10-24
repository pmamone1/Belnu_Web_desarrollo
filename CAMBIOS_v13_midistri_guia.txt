# MiDistri-Pedidos v13 · Acceso a configurar la tienda
Estado: implementación local; instalación productiva pendiente. Requiere Urban Soft594. No se envió campaña.

## Guía de uso
1. Abrí tu tienda y elegí Acceso Distribuidor. Usás la misma cuenta de Urban Soft: si ya ingresaste allí, no necesitás otra contraseña.
2. Confirmá qué tienda vas a administrar. Se abre Configurar MiDistri: diseños, colores, mensajes, logo, fotos, banners y carruseles. Las opciones se ajustan a tus permisos vigentes.
3. Ver mi sitio abre la tienda pública. Pedidos lleva únicamente a la gestión de pedidos. Si no tenés el permiso de configurar, el panel explica qué debe habilitar tu responsable.
4. En Urban, MiDistri → Configurar mi sitio muestra seis pasos retomables: conexión, sitio, catálogo, Email, WhatsApp y revisión final. Cada distribuidora ve su configuración y pendientes.
5. Los vendedores eligen su distribuidora y piden un código a su Email registrado. El código vale 30 minutos, se usa una vez y sale de la casilla de esa tienda. Desde una tienda seleccionada se propone esa distribuidora.
6. Cada distribuidora usa su Email y WhatsApp propios para comunicaciones. Se conserva la excepción expresamente compartida entre 20 - Belgrano y 65 - Barracas. El Email de contacto público y el remitente de envío son datos distintos.
7. Datos completos en la guía no confirma entrega externa. Guardar configuración no envía remitos ni campañas; seguí la revisión habitual.
8. Los pedidos mantienen precio vendedor, disponibilidad, aceptación parcial y referencias históricas. Llegan a Urban en Salidas / Pedidos → Pedidos web de MiDistri.

## Instalación y operación técnica
Acumulativo sobre MiDistri8..12. Instalar primero Urban594 con migración aditiva bridge0014, luego este paquete13 con esquema0009 conservado. Sin nuevas migraciones propias ni dependencias.
El botón público delega autenticación a Urban; no captura contraseñas Urban en MiDistri. Cookie firmada por desafío guarda destino y tienda; callback exige origen, nonce, firma vigente, pase válido y tienda dentro del perfil delegado. Destinos internos de lista cerrada; pestañas paralelas separadas. Sin permiso tienda regresa al panel con explicación, sin otorgarlo.
Nuevo selector público de tienda en ingreso con código y capability login_codigo_tienda; los contactos no se revelan antes de validar código. Tienda inexistente o API antigua incompatible no solicita un código. Se conserva sesión por pestaña,30minutos y un uso.
Guía, almacenamientoSMTP y política de identidad se mantienen en Urban; el portal no copia ni guarda credenciales de envío.
Instalador Python3.7 verifica hashes y proyecto, plan exacto y respaldo privado, sin modificar venv ni configuración externa. No aplicar sobre archivos desconocidos. No revertir migraciones ni datos automáticamente; ante instalación parcial conservar salida y respaldo y preparar corrección hacia adelante.
Producción, SMTP/WhatsApp real y cPanel no fueron usados como pruebas. No activa nuevas distribuidoras ni campañas automáticamente.

## Pruebas manuales
Abrir Acceso Distribuidor desde tienda20 y65 y otra autorizada; verificar destino correcto y permisos. Probar dos entradas paralelas y recuperación de pantalla vencida. Confirmar que Pedidos no cambia de función y Configurar MiDistri abre editor. Elegir tienda en acceso vendedor, solicitar código sólo en prueba autorizada externa y comprobar remitente; no usar un Email real ajeno para probar. Verificar galería, carrito, precios y banners. Revisar guía de cada distribuidora en Urban.
