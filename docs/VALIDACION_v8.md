# Validación MiDistri-Pedidos v8

## Evidencia local
- Suite completa de Django (manage.py test --settings=midistri_portal.test_settings --noinput): 114 pruebas OK (última ejecución: 0,821 s; ejecución anterior: 9,451 s). Cubre catálogo, precios, preparación parcial, autenticación, sesiones, permisos, multimedia, promociones y nuevas fotos de pedidos.
- Regresión roja previa: seis pruebas focales, cinco fallos esperados por falta de fotos y existencia de siete temas. Un control de acceso ya funcionaba.
- Instalador: 17 pruebas OK, 0,592 s, en carpetas temporales. No es una instalación productiva.
- JavaScript: cinco escenarios de preferencias ejecutando el script real; temas retirados con tienda Azul/Verde/Nocturno vuelven a Claro, un tema vigente se conserva y ausencia de preferencia respeta la tienda.
- Django check sin incidencias; makemigrations --check --dry-run: sin cambios.
- Revisión independiente: fotos segregadas por distribuidora y snapshots intactos. Se corrigió la preferencia retirada almacenada en el navegador; seguimiento del revisor confirmó el hallazgo resuelto.
- Navegador: catálogo con cuatro opciones, cambio a Nocturno, texto Kiosco y aviso simplificado; carrito y detalle renderizados con fotos, precios y botón correcto. Datos sintéticos, fotos locales y API simulada; ninguna operación en producción ni campaña.
- PDF: 10 páginas. Capítulo v8 de una página delante; nueve páginas anteriores conservadas por contenido. Portada vigente y unión renderizadas e inspeccionadas sin recortes.

## Límites y entrega
QA Python 3.12 / Django 3.2; constructor comprueba sintaxis Python 3.7. Instalación en belnuweb Python 3.7, MariaDB y verificación del usuario en su navegador: pendientes. No se asegura un despliegue por VERSION.
Ensayo del ZIP verificado: 30 archivos de payload y dos entradas de instalador/manifiesto. El ZIP usa inventario cerrado y hashes, sin bases, credenciales, media privada, venv ni el cambio ajeno de forgotPassword.html. El manifiesto identifica el commit fuente. Validar ZIP final contra los bytes del commit y publicar su hash en la entrega.
Sin modelo/migración nueva, cambio de contrato ni operación económica. Sólo paquete MiDistri; no actualizar Urban Soft para esta entrega. Campaña sin enviar.
