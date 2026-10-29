Estado vigente: diseño aprobado por el usuario e implementado en Urban621/MiDistri28; instalación productiva pendiente. El texto de la fase de diseño se conserva debajo como antecedente.

# MiDistri · Analítica de vendedores, productos y pedidos

Fecha: 29/10/2026. Estado: diseño revisado para construcción, pendiente de aprobación del usuario. No implementado ni instalado. Fuentes inspeccionadas: Urban Soft v1.18.620 y MiDistri v27; la instalación productiva de esas versiones no se presume. Sin envíos ni campañas.

## Intención y decisiones del usuario

El distribuidor necesita saber cuántos vendedores usan MiDistri, quiénes son, qué productos consultan/amplían y cuántos pedidos generan por período, para seguir la adopción y el interés comercial.
El usuario confirmó incluir a los vendedores sin ingresos registrados y a quienes ingresaron sin hacer pedidos. Eligió resumen general, ficha por vendedor y un historial detallado de acciones con fecha y hora. No pidió automatizar recordatorios ni comunicaciones.

## Enfoques considerados

1. Resumen y ficha por vendedor: menos detalle almacenado; permite seguir adopción e interés agregado, pero no explicar una secuencia concreta.
2. Resumen, ficha e historial individual de acciones: enfoque elegido por el usuario. Conserva el recorrido comercial verificable y exige registro propio, deduplicación, permisos, paginación e índices.

Se integra en MiDistri con sus identidades existentes. No se incorpora un proveedor externo de seguimiento. El enlace desde Urban Soft reutilizará el ingreso de Distribuidor existente y abrirá este mismo tablero; no se crea un segundo informe con cálculos distintos. Esta última integración es propuesta técnica, no una instrucción expresamente dada por el usuario.

## Alcance visible

Nueva opción «Estadísticas» en la administración de MiDistri. Acceso sólo administrativo: los vendedores no ven el comportamiento de otros vendedores.
Filtros: Hoy, últimos 7 días, últimos 30 días, este mes y fechas Desde/Hasta. Búsqueda por nombre, LIN o VV del vendedor; producto por nombre o SKU; tipo de acción para el historial. Valores predeterminados propuestos: últimos 30 días, zona horaria de Argentina, tablas de 50 filas. Son elecciones de diseño, modificables antes de implementar.
- Resumen: vendedores distintos que tuvieron actividad, ingresos con perfil validado, visitas, consultas de productos, ampliaciones de fotos, interacciones con videos y pedidos realizados; unidades e importes de pedidos separados por estado.
- Listado de vendedores: nombre e identificación administrativa, estado actual del vendedor/Email, último acceso acreditado, visitas, productos consultados y pedidos del período. No mostrar Email completo por defecto; basta indicador de contacto registrado.
- Ficha: indicadores del vendedor, productos consultados (nombre/SKU), fotos/videos abiertos, pedidos con la referencia MP que ve en su historial y enlaces al detalle autorizado.
- Historial paginado: fecha/hora, vendedor, acción, producto/SKU cuando corresponda, cantidad si es un cambio de carrito válido y referencia del pedido cuando exista. Las acciones no se presentan como compras efectivas.
- Excel: resumen, vendedores, productos y acciones, aplicando el mismo alcance/filtros. Una exportación grande debe paginarse o prepararse de forma acotada; nunca truncarse silenciosamente.
No incluye un tablero global de todas las distribuidoras, seguimiento de visitantes anónimos, grabación de pantalla, movimientos del mouse ni estimaciones de tiempo de lectura.

## Distribuidoras y autorización

Cada perfil puntual consulta únicamente su distribuidora.20 y65 funcionan como el bloque operativo conjunto vigente, con consolidado sin duplicar y desglose por distribuidora; no se exponen otras tiendas por ser SuperUsuario.
El backend revalida en cada consulta y exportación el operador, conexión, alcance y permisos de Urban Soft. IDs enviados por navegador no conceden acceso. La revalidación incluye búsquedas, ficha individual, datos cacheados y exportaciones.
Propuesta conservadora: exigir los permisos existentes pedidos.gestionar y midistri.tienda_configurar para consultar el tablero y sus fuentes; ambos se comprueban en servidor. No se concede un rol nuevo ni se amplían permisos existentes por instalar. Los importes se limitan a precios vendedor del pedido autorizado, nunca costos del proveedor o rentabilidad privada de Urban Point.
Las visitas del editor, vistas previas, personal administrativo y visitantes sin perfil Vendedor autenticado se excluyen. Un operador con sesión de Distribuidor no genera actividad comercial por editar/publicar ni por abrir este tablero. Si una persona entra realmente como vendedor mediante su identidad de vendedor, su actividad sí pertenece a esa identidad; no se deduce el rol por Email o nombre.

## Qué significa cada métrica

- Vendedor: identidad (distribuidora_id,vendedor_id), no Email. Un Email puede corresponder a varios kioscos; cada identidad se cuenta por separado. Un mismo vendedor desde varias pestañas se cuenta una sola vez como vendedor distinto.
- Ingreso: autenticación completada y perfil Vendedor seleccionado correctamente. Solicitar un código, fallar su verificación o abrir el selector no cuenta. Repetir una respuesta/reintento no crea otro ingreso.
- Actividad/entró en el período: identidad con una acción comercial acreditada durante el período, aunque la sesión se haya iniciado antes. Así un vendedor que conserva abierta su pestaña puede aparecer activo sin iniciar sesión otra vez.
- Visita: recorrido de un vendedor en una pestaña. Como propuesta técnica, una pausa de 30 minutos inicia otra visita analítica al volver; esto no vence ni cierra su sesión de acceso. Dos pestañas pueden ser dos visitas y un solo vendedor distinto. El tablero explica esta definición.
- Producto consultado: abrir su detalle o galería. Renderizar tarjetas al cargar el catálogo no prueba que el vendedor las haya mirado y no incrementa consultas individuales.
- Foto ampliada: foto de galería mostrada con éxito por una acción del vendedor; no se cuenta un error de imagen, el desplazamiento automático de un carrusel ni una miniatura cargada de fondo. Varias fotos de un producto pueden generar varias acciones; «productos consultados distintos» sigue deduplicado.
- Video: MP4 del portal informa inicio real de reproducción (evento play), evitando repetir pausas/reanudaciones del mismo recurso abierto. Para YouTube/Vimeo se informa «Abrió enlace de video»; no se afirma reproducción ni finalización en una web externa.
- Carrito: agregar/actualizar/quitar una cantidad que el servidor aceptó, conservando la validación actual de producto, display y alcance. Un intento rechazado no se registra como cambio conseguido.
- Pedido realizado: UUID aceptado por Urban Soft. No se cuenta el botón pulsado, un borrador local pendiente de transmitir ni un reintento del mismo UUID. Si luego se cancela, sigue constando que se realizó, con su estado cancelado claramente separado.
- Conversión a pedido enviado: vendedores con actividad en el período y al menos un pedido aceptado en ese mismo período, divididos por vendedores con actividad registrada en ese período. No es conversión a venta debitada. Si no hay actividad, mostrar «Sin datos», no dividir por cero. Los pedidos sin visita registrada aparecen como tales y no fuerzan la conversión por encima de 100%.
- Unidades/importes: mostrar «solicitado» desde items históricos de la solicitud y «confirmado/preparado» desde atención/preparación acreditada; los cancelados y las cantidades retiradas no se suman al confirmado. No usar precios actuales ni confundir emitido con venta efectivamente cobrada. Los estados deben tener leyenda y fecha de consulta.
Las cifras de pedidos por período se asignan por creado original de Urban Soft, no por la fecha en que el portal actualizó su copia local. Los estados son los actuales al consultar; no se promete reconstruir cómo estaba cada pedido en una fecha pasada sin evidencia histórica.

## Grupos de vendedores y cobertura temporal

El padrón lo provee Urban Soft, limitado al alcance autorizado. Se incluyen los vendedores activos no depósito del alcance; sin Email/contacto habilitado se identifican como «Sin contacto para ingresar», no como falla del portal. En ficha/historial se conservan acciones de vendedores hoy inactivos dentro de su distribuidora de origen, identificando el estado actual sin reasignarles datos de otra tienda.
Se distingue:
1. «Sin ingresos registrados desde [inicio de medición]»: no hay un ingreso ni actividad acreditada en ese intervalo. No se lo etiqueta como «nunca ingresó» en toda su vida.
2. «Sin actividad en el período»: puede haber ingresado anteriormente; no es el grupo anterior.
3. «Ingresaron sin pedidos en el período»: tuvieron actividad, pero no un pedido aceptado durante ese período, aunque tengan pedidos anteriores.
4. «Sin pedidos MiDistri registrados»: no existen solicitudes aceptadas para esa identidad en todo el histórico disponible. Una solicitud cancelada cuenta como pedido histórico; el filtro «Sin pedidos vigentes» podrá derivarse de estados pero no cambia esta etiqueta.
5. «Con pedidos»: tienen pedidos aceptados, separando pendientes, OK, preparados/entregados y cancelados según el contrato actual y su atención.
Los pedidos existentes pueden aportar histórico desde su fuente original. El seguimiento de acciones empieza al habilitar esta función y muestra la fecha y cobertura real. No se inventan acciones antiguas desde la última actividad de una sesión, ni se igualan un carrito abandonado y un pedido cancelado.
Las sesiones antiguas sirven como evidencia positiva de que existió un acceso, cuando sus campos lo acrediten. Podrán mostrarse como «Acceso previo acreditado por sesión existente» separado del historial nuevo; no se reconstruye su secuencia, número de visitas ni fecha de ingreso exacta a partir de un registro reutilizado. No rellenan métricas detalladas anteriores al inicio.
Si no se obtiene el padrón completo o el histórico de pedidos de Urban Soft, los grupos negativos quedan «No disponible / fuente incompleta». Nunca convertir una caída de API o una página incompleta en «nunca ingresó» o «no hizo pedidos».

## Registro y fuentes técnicas propuestas

MiDistri conserva el registro de acciones; Urban Soft conserva la autoridad de vendedores, permisos y pedidos. No se duplica ni se modifica el circuito económico.
- Nuevo registro aditivo en el portal: inicio de medición, visita analítica y acción con UUID idempotente, fecha/hora UTC asignada por servidor, distribuidora, vendedor y referencia de sesión/visita; producto/recurso o UUID de pedido según el tipo. Guardar nombre/SKU mínimo acreditado para que un cambio de maestro no desplace el historial de tienda. No guardar tokens, códigos, contraseñas, IP completa, huellas nuevas del dispositivo, Email completo ni texto libre del vendedor en la telemetría.
- Identidad de actor obtenida exclusivamente de la sesión autenticada y perfil revalidado. Para un recurso, validar la publicación/pertenencia en esa tienda antes de aceptar su evento. No aceptar un vendedor/distribuidora/nombre arbitrario proporcionado por JavaScript.
- Ingreso y carrito se registran desde los puntos de éxito del servidor. Consultas de galería/fotos/videos usan solicitudes pequeñas agrupables, protegidas con CSRF, prueba de pestaña existente, tipos permitidos, tamaños/límites y control de frecuencia. Elegir valores concretos queda al implementador y a pruebas de carga acotadas; deben impedir que un navegador bloquee los pedidos o llene indefinidamente la cola. No usar una petición externa a Urban por cada foto.
- Un evento reintentado con el mismo UUID es único; si cambia actor/tipo/recurso, se rechaza en lugar de sobrescribir. Las acciones distintas e intencionales sí permanecen. No registrar cambios automáticos de banners como clics del vendedor.
- Fecha/hora: almacenar UTC y mostrar America/Argentina/Buenos_Aires. Desde/Hasta inclusivos para el usuario se convierten en límites UTC semiabiertos de días locales. El reloj del celular no fija la fecha oficial. No afirmar orden exacto entre dos acciones recibidas fuera de orden; conservar referencia de visita y hora de recepción.
- Captura de fotos/videos es informativa y puede perder acciones por bloqueo de JavaScript, desconexión o cierre inmediato. Mostrar «Actividad registrada» y su inicio; no prometer medición perfecta o tiempo exacto de lectura.
- Fallos del registro analítico se aíslan con transacciones/savepoints o cola acotada: no deben impedir ingresar, agregar al carrito o enviar el pedido. El tablero distingue pérdida de cobertura de ausencia de actividad. Los pedidos se cuentan desde Urban, aun si su evento informativo local falta.
- Urban agregará una consulta privada de sólo lectura que entregue padrón mínimo e indicadores de solicitudes por vendedor y por período, además de referencias históricas necesarias para la ficha. Paginar el padrón completo sin tope silencioso de 100 pedidos, conservar un corte/estado de consulta coherente y reportar si falta alguna página. El endpoint actual orders del vendedor, limitado a100, no sirve como fuente del agregado global.
- Composición del tablero: cruzar el padrón completo autorizado con las acciones locales y solicitudes de Urban. Filtrar los grupos después de completar ese cruce, no después de descargar sólo la primera página. Cachear resultados por operador/alcance/filtros y fecha de corte; revalidar permisos antes de entregarlos. Ante fallo de una fuente, mostrar fecha del último dato válido y estado de incompleto.
- Tablas y Excel comparten la misma definición de indicadores, fuentes y corte; no exportar identificadores de sesión, claves o contactos ajenos. Preparación/paginación acotada para grandes volúmenes, sin bloquear el guardado de pedidos.

## Rendimiento, conservación y operación

Índices por distribuidora+fecha, vendedor+fecha y producto+fecha; consultas agrupadas y paginadas. Evitar N+1 por vendedor y descargar imágenes/videos para generar estadísticas. No registrar cada movimiento de scroll.
Propuesta inicial: conservar el historial nuevo sin una purga automática. Una política de retención futura requerirá documentar su ventana y conservar la cobertura/resúmenes; no borrar silenciosamente el detalle solicitado. Tablero permite intervalos amplios con paginación; el implementador medirá volumen/consultas y podrá usar agregados auxiliares conciliables sin cambiar el resultado.
Bandera de activación coordinada: instalar código no empieza a emitir correos ni a cambiar permisos. Desactivar captura detiene eventos nuevos, conserva los anteriores y marca el corte de cobertura; no afecta login/pedidos. Las interrupciones de captura se registran como intervalos, no se confunden con cero visitas.
No se necesitan servicios externos. Reutilizar el cron existente sólo si la implementación elige precalcular agregados; no cambiar cron sin documentar su necesidad real. El dato de pedidos debe mostrar su actualización efectiva.
No se envían recordatorios ni campañas a los grupos detectados. Exportar una lista no autoriza comunicarla ni despachar un mensaje.

## Compatibilidad, migración y rollback seguro

Cambios aditivos en ambos proyectos: tablas/índices de analítica del portal y contrato privado de lectura en el bridge; nueva navegación y páginas de estadísticas. No editar migraciones aplicadas ni reconstruir económicos/históricos. Mantener Python 3.7/Django 3.2 del portal y Python 3.10/Django actual de Urban, según entornos productivos ya declarados.
Orden propuesto: Urban con endpoint/permisos compatibles, portal con modelos/rutas y captura inicialmente apagada, comprobar contrato y después habilitar captura. Sin datos previos de seguimiento, mostrar inicio real; sólo reutilizar pedidos históricos acreditados. La base exacta de cada ZIP se definirá al implementar a partir del código y la instalación confirmada, no se inventa una versión instalada.
Ante incidente: desactivar captura y enlace de estadísticas, conservar tablas/eventos/cobertura y pedidos, corregir hacia adelante. Restaurar sólo código compatible con el esquema; nunca borrar tablas o retroceder migraciones para ocultar un error. Respaldo automático de archivos y frecuencia de respaldo completo ya acordada.
Entrega posterior a aprobación: documentación técnica, manuales/PDF, VERSION_DOCUMENTADA y CAMBIOS reales, pruebas, revisión final, ZIP separados Urban/MiDistri para cPanel y commits/PR publicados en GitHub. Esta fase de diseño no incluye un ZIP instalable ni una prueba con vendedores reales.

## Validación exigida antes de entregar

- Login correcto/un perfil/múltiples perfiles/reintento: ingreso único sin contar solicitud fallida de código. Una pestaña conservada registra actividad en otro día sin forzar login nuevo.
- Pestañas/visitas: vendedor distinto sin duplicar; nueva visita tras 30 minutos sin vencer sesión; reintento de evento no duplica.
- Galería: foto efectiva, fallida, miniaturas, varios recursos, carrusel automático, fallback y video externo/MP4 con etiquetas veraces. Sin JavaScript, no fabricar actividad de fotos.
- Carrito: sólo éxito válido, display respetado, actor falsificado/tipo/recurso/tienda ajena rechazados. Falla de analítica no rompe el pedido.
- Pedidos: histórico completo de más de 100, doble transmisión, pendientes locales, cancelación completa/parcial, precio histórico y referencia MP idéntica. Conversión con denominador 0, pedido sin evento de visita y ventana con sesión anterior.
- Grupos: padrón activo con/sin Email, inactivos, pedidos anteriores, sesiones previas sin detalle, API caída/paginación incompleta y transferencia de vendedor entre tiendas. No asignar datos históricos por distribuidora actual del maestro.
- Alcance: 20/65 consolidado/desglosado; otro perfil puntual sin referencias a terceras distribuidoras, incluso SuperUsuario, caches y Excel. Ambos permisos exigidos; revocar acceso invalida también consultas preparadas.
- Períodos: medianoche Argentina, Desde/Hasta, límites/orden de acciones recibidas, filtro/Excel y totales coherentes. Tablas con paginación sin truncado silencioso.
- Navegador local: resumen, filtros, ficha, historial y descarga; móvil sin desbordamientos y carga/error/ausencia de datos diferenciados.
- Instaladores: exactas bases aceptadas, plan de migraciones aditivo, comprobación sin escritura, reintento y recuperación compatible. Manuales y páginas de unión PDF verificados.

## Estado al terminar este documento

Revisión independiente de construcción completada el29/10/2026: no quedaron preguntas importantes pendientes para preparar un plan. No es una prueba ni revisión de implementación. Pendiente de aprobación del diseño antes de preparar el plan y la implementación. No se ejecutaron migraciones, captura, cambios de permisos, campañas ni movimientos en producción.
