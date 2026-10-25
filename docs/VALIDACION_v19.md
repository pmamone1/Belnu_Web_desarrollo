# Validación MiDistri-Pedidos v19

Fecha local24/10/2026. Python3.12/Django3.2.15/SQLite aislados. Sintaxis destinoPython3.7 verificada al construir. Sin producción ni SMTP real.

Suite portal completa182casos:181aprobados,1omitido. Incluye encabezado/navegación escapados conrutas fijas, logo privado enpreview/público sólo alpublicar,9presets/logo propio/favicon independiente, límite80, borradoresprevios, búsqueda plural/acentos/error leve yscope, conteo/ordenprecio+PVP, contratos indicadores inválidos, catálogo antiguo+moderno sin duplicación de logo y display. JSON0010aditivo, precios/snapshots/tenant conservados. Django check y makemigrations limpios.

JavaScript unitario:18casos aprobados de código/sesión, estado/autosave/conflicto/replay y progreso. Una invocación exploratoria con todos test*.cjs incluyó dos guiones de navegador antiguos, tools/test_banners_browser_v12.cjs y tools/test_pagina_browser_v11.cjs, que no arrancaron por falta del paquetePlaywright; no se afirma que hayan pasado. QA actual se realizó con el navegador de estechat y datos locales, sin instalar otro navegador/dependencias.

QA visual real local: cambio de nombre y textos de navegación guardado/preview; selecciónCarrito yCamión mostrada encabezal; faviconOfertas independiente comprobado enDOM; revisión/publicación con spinner y ambos botonesdeshabilitados hastarespuesta; mensajePublicado despuésdelresultado. Consulta términos→Termo de demostración,1resultado,ordenprecio_desc. Trofeo, secciónmásvendidos,entrega24/48 yúltimasunidades:colorwhite rgb255 yfondorojo rgb186,23,40. Capturasguardadasfuera delZIP. Publicación exclusivamente de tienda sintética local;ningún cambio en sitio productivo.

Instalador/paquete:25casos aprobados, basesexactas16/17/18, migración0010realmente invocada, guardiaMigrationRecorder antesde restaurar, sin saltar preflight. Pruebas usandirectorios temporalesyoperaciones simuladas. Manualprincipal21páginas,20anteriorespreservadas;capítulo1yunión2renderizadosyrevisados. Inventariocompletoincluye9SVGyexcluyeforgotPasswordajeno.

Revisión independiente sin defectos críticos/importantes abiertos. InstalarUrban602primero, portal19despuésycoordinadorpara refrescar; producciónHTTPS yteléfono físico pendientes. No seenvían campañas ni se implementaMiDistri-Puntos.
