# MiDistri-Pedidos v24 — Encabezado sin LIN

## Guía de uso
1. El saludo del vendedor muestra únicamente su nombre y número VV: por ejemplo, Hola, Cerrutti · VV194. La LIN deja de mostrarse en el encabezado del catálogo, carrito, historial y detalle de pedidos.
2. El nombre comercial y logo de la tienda siguen siendo configurables. No se cambia el número de vendedor, el perfil, sus permisos o la distribuidora.
3. Se conserva Entregado/Entregado parcialmente al emitirse el remito, cancelaciones y ranking por venta neta consignada. No hay que recalcular indicadores ni sincronizar por esta corrección de presentación.
4. Instalar sobre MiDistri23 y recargar el navegador. Urban606 se conserva; no requiere otro paquete Urban. No se envían campañas.

## Detalle técnico
Se elimina el segmento LIN del template base compartido, sin depender de la vista. Se actualizan las expectativas anteriores del contrato, editor e historial para conservar nombre/VV y exigir ausencia de LIN. El dato lin sigue en el contrato de perfil; no se modifica la información operativa de Urban Soft ni se cambia el alcance de acceso.

## Compatibilidad y rollback
Base MiDistri23, compatible con Urban606 instalado. No nuevas migraciones, rutas, variables, dependencias ni cambios de precios, pedidos, saldos, remitentes, WhatsApp o cron. El instalador revisa todos los destinos y plan vacío antes de copiar; respaldo automático de archivos reemplazados. Rollback mediante respaldo propio de archivos: vuelve a la presentación23; no revierte datos ni esquema. Instalación productiva pendiente.
