# Filtro y encabezado MiDistri — Plan de implementación

> Ejecución inline mediante superpowers:executing-plans. Revisión independiente al finalizar.

## Requisitos y decisiones
El usuario pide filtro «Sólo pedidos de MiDistri», editar encabezado y logo y ver progreso de publicación. Confirma también editar los textos Catálogo/Acceso Distribuidor. Se reutilizan campos/JSON, validación de tenant y publicación firmada. No crear un segundo editor ni cambiar destinos de los enlaces. No enviar campaña ni tocar producción.

## Diseño acotado
Urban: checkbox origen=midistri con EXISTS sobre la relación Solicitud.pedidos, combinado con alcance activo, estados y demás filtros; no inferir origen de nombres ni observaciones. Mantener filtro en navegación y estadísticas.
Portal: sección Encabezado y logo al principio de la biblioteca: nombre, etiquetas Catálogo/Acceso Distribuidor, foto de logo, vista previa y quitar. Logo en cabecera pública y preview; no duplicarlo en bienvenida. Campos por tienda, texto escapado y límites. Etiquetas vacías usan defaults; rutas y permisos iguales.
Publicación: estado visible con spinner indeterminado (sin porcentaje inventado), bloqueo de clics dobles y de cierre del diálogo durante revisión/publicación, limpieza en éxito/error; conservar firma/reintento idempotente ante resultado incierto.
Paquetes independientes acumulativos Urban600/601→602 y MiDistri16/17/18→19. Conservar cambios previos, manuales, remitentes, WhatsApp, históricos y venv. Sin modelos nuevos propios; Urban requiere/aplica bridge0017 de601 si falta.

## Tareas
- [x] Pruebas RED de filtro combinado y alcance, sin duplicados y con anulación.
- [x] Implementar checkbox, queryset y persistencia de navegación.
- [x] Pruebas RED de encabezado/logo/etiquetas y publicación ocupada.
- [x] Implementar sección visual, defaults compatibles y spinner con recuperación.
- [x] Pruebas automatizadas y navegador local; check y esquema.
- [x] Documentar comportamiento real, manuales PDF y rollback; revisar de forma independiente.
- [x] Construir/verificar ZIP y publicar commits/PR separados; guardar ZIP en Downloads y entregar comandos completos.

## Riesgos a revisar
Filtro jamás amplía alcance; Pedido puede tener varias Solicitudes, no duplicar. Borradores previos carecen de nuevas etiquetas, usar valores por defecto. Logo privado en previa usa ruta autenticada y sólo se publica tras confirmación. Evitar doble publicación y permitir recuperación si respuesta se pierde. El spinner no debe quedar activo tras error ni dar éxito antes de respuesta.

Ampliaciones explícitas:9logoscomercio/transporte,faviconindependiente,búsqueda/conteo/orden,rankingtotalUrban,plazos24/48-96,últimasunidades1..9,Emailporproducto.CacheUrban0018yPortal0010,croncada5min. Sin campaña. Revisiónfinalcerrada;instalaciónproductivapendiente.
