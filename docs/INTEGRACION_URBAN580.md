# MiDistri v2 — contrato con Urban Soft v580
Diseño aprobado22/10/2026. Instalación y habilitación productiva pendientes.

## Bases y entornos
Urban: e5501cb8b748b5b6c88931b98fd56cddfa1865a2 (v579), /home/mcollini/sistema7000,
Python /home/mcollini/virtualenv/sistema7000/3.10/bin/python (3.10.20, Django5.2.16).
MiDistri:10b49c4267fb234cd02791dfcdbac9f578da8a6c, /home/mcollini/belnuweb,
Python /home/mcollini/virtualenv/belnuweb/3.7/bin/python (3.7.12, Django3.2.15).
Se contrastaron seis archivos Urban y siete MiDistri con huellas coincidentes. Los entornos Urban3.12/3.13 no sirven el sitio; no se modifican.

## Arquitectura y permisos
Apps nuevas midistri_bridge y midistri_portal, repositorios/ZIP/bases separados.
Urban /midistri/catalogo/ exige urban.integraciones y productos.editar para publicar.
No consulta vendedores. Publicar20/65 incluye sólo miembros permitidos del grupo.
Urban /midistri/ exige pedidos.gestionar y alcance privado; invitación/revocación exige vendedores.gestionar.
Emisión exige además autorización financiera y pedidos.remitos, tanto en servicio como interfaz.
Conserva SuperUsuario efectivo, privacidad de Urban Point común y reglas actuales del middleware.
Ruta externa /midistri/api/ exige credencial de aplicación y conexión/distribuidora activas.
No autoriza por sesión staff ni amplía el catálogo público anterior.

## Contrato privado v1
snapshot GET completo por distribuidora, producto activo/proveedor activo, precio vendedor y PVP,
display e imágenes publicables. Nunca costo proveedor, contactos, saldos o matrícula.
activate POST consume invitación aleatoria hash48h; GET de portal no consume.
profile GET valida sesión personal revocable90d y devuelve ID, nombre, distribuidora, línea, LIN y VV.
orders GET/POST: UUID estable, huella, precios y publicaciones revalidados al recibir.
Nombre/LIN/VV/orden/productos/precios/proveedor congelados; id repetido con otro contenido se rechaza.
Respuesta incluye vendedor_id y distribuidora_id; portal valida propietario, formato y estado antes de guardar.
document/UUID GET sólo de vendedor/distribuidora/conexión emisora. PDF nativo verificado, sin matrícula.
logout POST revoca sesión. API y portal no-cache; enlaces personales con no-referrer.
Catálogo anónimo muestra PVP. Precio vendedor y carrito requieren enlace personal.
Sin registro, pago, reserva ni control automático de disponibilidad física.

## Emisión y documentos
Recibido/OK/Excel/cancelado no generan débito. Emitir bloquea solicitud/vendedor,
crea Pedido/PedidoProducto/PedidoAsignacion nativos por proveedor y llama aplicar_saldo_pedido(usuario).
Saldo firmado previo negativo se netea por el servicio existente; no se reinterpreta el campo legado
credito_saldo_vencido. Emisión repetida conserva pedido, cargo y documento.
RemitoPedidoComunicacion y DocumentoEnvio nativos se congelan en la transacción.
Un proveedor entrega copia PDF idéntica; varios proveedores reúnen copias nativas con límite10MiB.
No se reescriben documentos ni precios históricos. Cancelación posterior se gestiona por circuito nativo.

## Email e invitaciones
MIDISTRI_BRIDGE_ENABLED, MIDISTRI_EMAIL_ENABLED y COMUNICACIONES_ENVIOS_HABILITADOS deben habilitarse
expresamente. Instalación no los configura ni envía Email.
Remitente resuelto por distribuidora/vínculo central actual, configuración cifrada/servidor existente.
Contactos habilitados, preferencia principal/todos y bajas de remitos respetadas.
Invitación requiere seleccionar contacto y confirmar Email exacto; token no se guarda en texto reutilizable.
Avisos recibido/cancelado/emitido tienen outbox propio y estado por contacto.
Claim persistido antes de SMTP; Message-ID estable; aceptados no se repiten.
Rechazo confirmado queda pendiente con demora; excepción ambigua queda por_conciliar y no se reintenta.
Proceso interrumpido queda enviando; esperar15min y verificar con proveedor.
Conciliar exige permiso, ámbito privado, confirmación y motivo10–500 caracteres; registra actor/fecha/resultado.
Aceptar resultado o declarar no enviado no manda Email ni modifica saldos.
Avisos de tareas diarios08h existentes no se reemplazan por esta cola comercial.
Cron propio opcional midistri_enviar_avisos sólo pendientes; no instala cron ni toca los anteriores.

## Migración y compatibilidad
Urban requiere consignaciones0121 aplicada; crea sólo midistri_bridge0001–0004.
0001 depende de0121. No modifica migraciones anteriores de consignaciones.
Compatibilidad de lectura con registro legado adicional0015 informado, sin borrar ni editar ese registro.
Portal requiere store0017_alter_variation_precio_ed aplicada; crea sólo midistri_portal0001.
Archivos presentes no demuestran aplicación; preflight consulta MigrationRecorder antes de copiar.
Tras copiar, plan de migración sólo puede contener pasos hacia adelante de la app propia.
Flags apagados por defecto y app nueva sin permisos automáticos ni publicaciones iniciales.

## Instaladores y rollback
Formato ZIP: instalar.py, release_manifest.json y payload/ exclusivo de cada repositorio.
Verifica proyecto, marcador manage.py, Python/prefix/destino exactos, inventario, rutas sin symlink,
hash de contenido y hash normalizado LF de cada base. Archivo nuevo desconocido o diferencia bloquea.
Preflight es de lectura, no crea respaldo ni reemplaza archivos. --apply respalda archivos en carpeta
privada de /home/mcollini, detiene su Python App, escribe atómicamente, check/modelos/plan/migrate,
collectstatic y start confirmado por cPanel. No instala dependencias ni cambia secretos/venv/base ajena.
Ante fallo se conserva respaldo y estado explícito; no restaurar bases ni revertir cargos automáticamente.
Restauración de código verifica proyecto/ruta/hash posterior, detiene aplicación y conserva esquema/tablas.
Para volver atrás, apagar flags y cron de integración antes de restaurar archivos.
Reutilizar respaldo Urban21/10/2026 dentro de15d o30instalaciones confirmadas; no contar publicación.
MiDistri necesita respaldo propio antes de su primera instalación; el respaldo de Urban no cubre su base.

## Entrega y límites
Dos commits/PRs y ZIP distintos. Ninguna instalación, SMTP real ni piloto se acredita por publicar código.
QA usa bases y usuarios sintéticos. Runtime localPython3.12 con Django5.2 y3.2 separados;
sintaxis mínima comprobada3.10/3.7. Pruebas en motores productivos y runtime3.7 real pendientes.
Mantener flags apagados hasta conectar, sincronizar, verificar ámbitos y autorizar piloto concreto.

Revisión final: SKU/código hasta80 mediante migración aditiva0002; contrato de pedido alineado con Urban. Recuperación de instalación parcial comprueba hashes originales y nuevos antes de restaurar. No edita migraciones anteriores.
