# MiDistri-Pedidos v25 — Saludo sólo con nombre

## Guía de uso
1. El encabezado queda como Hola, Cerrutti. Se eliminan LIN y VV del saludo en catálogo, carrito, historial y detalle. Esta guía reemplaza la indicación anterior de conservar VV en ese encabezado.
2. Se conservan el nombre comercial y logo configurables de la tienda. La identidad interna del vendedor, sus números, permisos, precios y documentos no se alteran; sólo cambia lo que se muestra en el saludo.
3. El estado Entregado/Entregado parcialmente y el ranking de venta neta consignada se conservan. No es necesario recalcular indicadores ni sincronizar por esta corrección.
4. Instalar este paquete acumulativo sobre MiDistri23 o24 y recargar el navegador. Urban606 no cambia. No se envían campañas.

## Detalle técnico
base.html conserva únicamente perfil.nombre dentro del saludo. El contrato de perfil conserva lin/vv; no se cambia la API ni se guardan datos del vendedor. Las regresiones de contrato, editor e historial se adaptan para exigir ausencia de ambos números y preservar nombre, título y logo.

## Compatibilidad y rollback
Paquete acumulativo revisado sobre commits de MiDistri23 y24, con inventario explícito y hashes aceptados de ambas bases. Conserva Urban606. Sin migraciones, rutas, variables o dependencias nuevas. No cambia saldos, pedidos, precios, remitos, remitentes, WhatsApp o cron. El preflight verifica archivos y plan vacío sin escribir; aplicación respalda los archivos antes de reemplazarlos. Rollback mediante respaldo propio de código: vuelve al saludo anterior de la base instalada; no revierte esquema ni datos. Instalación productiva pendiente.
