# Revisión final Urban594 / MiDistri13
Revisor independiente: gpt-6-astra, sólo lectura, sobre bases Urban593 y MiDistri12. Dictamen inicial: sin Critical;5Important y1Minor. No se realizó una segunda revisión: la pasada de correcciones se verifica con regresiones observadas RED y GREEN.

## Hallazgos y resolución
1. Identidad efectiva WhatsApp: Meta se compara por phone_number_id;360dialog por huella de su API Key, además del número normalizado. Dos rótulos no separan una misma identidad. Test test_identidad_efectiva_whatsapp_no_depende_rotulo, RED→GREEN.
2. Segunda pestaña sustituía sesión: conservar tokens delegados por tienda en sesión del servidor, nunca unir permisos. Cada petición obtiene el token de su tienda y se revalida enUrban. Cambiar usuario limpia accesos anteriores; salir revoca todos los tokens del navegador. Se usa bloqueo y recarga de sesiónDB al combinar callbacks del mismo usuario. Tests dos_callbacks_conservan_accesos_por_tienda y salida_revoca_todos..., RED→GREEN.
3. Selección autorizada cambiada: Urban envía la tienda efectivamente confirmada; callback exige origen/desafío/pase y que esté dentro del perfil delegado, sin insistir en la sugerencia inicial. Test cambio_autorizado_en_selector_abre_tienda_final, RED→GREEN.
4. Carrera de primer canal y mismoEmail en distintas tiendas: bloqueo común antes de leer/validar, más guardado transaccional común. Tests PostgreSQL con dos peticiones reales, dos_altas_simultaneas... y identidad_simultanea..., RED→GREEN. Una guarda y la otra recibe error de revisión/conflicto; no500 ni dos identidades duplicadas.
5. Formulario antiguo no validaba: la misma política reside en RemitenteForm.save, usada por ambas pantallas, con rollback del conflicto y error visible. Se serializan también los vínculos compartidos. Tests formulario_administrativo... y admin_post_conflicto..., RED→GREEN.
6. Selector ofrecía combinación imposible: recalificado Important por afectar el objetivo de acceso sencillo. Filtrar tiendas por la conexión elegida y mostrar un paso de elección sólo si hay varias. Test tiendas_filtradas_por_conexion_elegida, RED→GREEN.
No quedan hallazgos diferidos de esta revisión. El permiso de configuración no se otorga automáticamente.

## Decisiones de ejecución y compatibilidad
- Aprobación explícita de diseño y ejecución en este chat cubre planificación equivalente y publicaciónGitHub; no repetir autorizaciones. Riesgo si se interpreta mal: cambio de alcance; el diseño aprobado se conserva en el repositorio.
- Reutilizar repositorios de trabajo actuales, con ramas nuevas. Preservar el cambio ajeno forgotPassword sin incluirlo. Riesgo: mezclar archivos; inventario explícito y verificación de ZIP contra commit.
- El módulo comunicaciones_identidad existente se preservó; la política nueva usa comunicaciones_remitentes_identidad. La colisión inicial se detectó por tests y se restauró byte a byte antes del primer commit. Riesgo: imports rotos, cubierto por suite.
- Alcance del código como listaJSON cuyo primerID es tienda origen, sin nuevaFK. Riesgo: desplazar origen; tests de tienda/entrega y migración aditiva.
- Pruebas antiguas que centralizaban sin excepción o simulaban remitentes distintos usando la misma casilla se adaptan a la regla nueva. No se relajan permisos para satisfacer pruebas.
- Completar la vinculación revisada a una conexión existente, porque sólo existía creación de otra clave. Riesgo: ampliar catálogo; confirmación explicita, alcance, auditoría y límite10.000, sin activación durante instalación.
- Registro PowerShell equivalente de pasos, sin nuevos checkouts. Riesgo de continuidad: ledger propio y commits por tarea.

## Aspectos apartados por el revisor y resolución del implementador
- SMTP/Meta/360dialog, identidad externa y webhooks reales: no probar sin autorización de envío/credenciales. Mostrar datos completos, conexión externa sin verificar; no afirmar entrega.
- cPanel y reinicio efectivo: sólo pruebas en temporales; instalación productiva pendiente y comandos proporcionados.
- Datos/migraciones/backup productivos: no inspeccionados ni modificados en esta tarea. Fecha y conteo se apoyan en confirmaciones previas del usuario; no inferir instalaciones desde marcadores.
- ZIP final, hashes, Downloads yGitHub: el implementador verifica inventario, bytes contra commit, copia física y publicación al cerrar entrega; no certificarlos sólo con revisión de fuentes.
- UI y PDF: autor inspeccionó capturas Chrome1440/390 y páginas vigentes/unión; scripts conservan streams anteriores. No equivale a validación en todos los dispositivos/clientes.
- ConcurrenciaPostgreSQL: se añadieron y ejecutaron dos peticiones reales locales que reproducen los intercalados, y pruebas de bloqueos de pagos existentes. No producción.
- Rendimiento de muchos remitentes: no se afirma tiempo de respuesta medido; configuración poco frecuente serializa filas pequeñas y resolución conserva bloqueo ante conflicto. Evaluar volumen representativo si aumenta.
- Interrupciones/disco lleno/ediciones externas durante instalación: se conservan hashpreflight, reemplazo temporal y respaldo; no afirmar inyección física de fallos. No rollback automático de datos; corrección hacia adelante.
- Históricos/importes/campañas/sincronización/sesiones vendedor: conservar circuitos, pruebas relacionadas y suite del portal; no se declara suite globalUrban histórica verde.
- LoginUrban yTLS/cookies reales: reutilizar autenticación y controles existentes; no debilitar validaciones para simplificar UX. No auditoría completa de infraestructura ni cambios de claves.
