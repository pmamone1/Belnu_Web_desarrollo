# MiDistri Pedidos Online v3: formularios y protección CSRF

## Causa y reproducción
En v580/v2 se agregó Referrer-Policy:no-referrer para proteger direcciones privadas.
En formularios de navegador esa política puede originar Origin:null y suprimir Referer.
Reproducido con Chromium en copia sintética: publicar devuelve403, motivo
Origin checking failed - null does not match any trusted origins.
Documentación oficial: https://docs.djangoproject.com/en/5.2/ref/csrf/#removing-the-referer-header

## Cambio integrado
Sólo midistri_portal.middleware.PortalMiddleware.process_response
cambia la cabecera a same-origin. El navegador conserva la referencia del mismo origen
y omite la de otros orígenes. No se agrega null, comodines ni dominios a CSRF_TRUSTED_ORIGINS.
No se agrega csrf_exempt, ni se desactiva middleware, ni se modifican cookies.
Cache-Control:private,no-store permanece. Noindex/nofollow y las sesiones privadas permanecen.

## Compatibilidad e instalación
Base exacta 8189c03821a79b1e1e38f92b03cd27ab4dd0caf1. Sólo archivos; migraciones nuevas:0.
Instalador verifica la migración midistri_portal.0002_publicacion_codigo_80 ya aplicada, el entorno
Python3.7 en belnuweb y hashes de archivos.
El plan de migración debe estar vacío en la base indicada; migrate no agrega ni altera tablas.
El otro proyecto, secretos, datos, snapshots, importes y saldos no se tocan.

## Recuperación
Restauración de código mediante --restore y respaldo privado generado por este instalador.
No revertir tablas ni bases ni migraciones. Volver al código anterior reintroduce el403.
Conservar flags apagados hasta configurar conexión y realizar piloto autorizado.
Después de instalar, abrir nuevamente la pantalla desde su enlace para obtener el formulario actual.

## Estado operativo confirmado
El usuario confirmó v2 y migraciones0001-0002. Respaldo de archivos /home/mcollini/respaldo_midistri_pedidos_hh8_ankz. MariaDB Strict Mode produjo advertencia no bloqueante; no se modifica aquí.
El piloto solicitado es20/65 con SKU LVL1978; todavía no se publicó ni se creó clave en producción.
