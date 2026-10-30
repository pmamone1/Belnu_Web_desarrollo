# Validación de acceso recordado - 30/10/2026

Pruebas realizadas con datos sintéticos y sin SMTP real ni campañas.

- Urban: 103 pruebas seleccionadas en PostgreSQL17 local, todas aprobadas. Incluye autorización, acceso OTP, administración, analítica, pedidos, dispositivo y dos carreras reales (alta idempotente y restauración frente a revocación).
- Portal: 261 pruebas completas en MariaDB10.11, aprobadas con dos omisiones: prueba exclusiva de PostgreSQL y fixture de rebobinado antiguo reservado a SQLite. SQLMode existente conservado. SQLite260 antes del diagnóstico adicional: correcto con dos omisiones de motor.
- Navegador Chromium por HTTPS: primer OTP, cookie HttpOnly/Secure persistente, nueva sesión Django, reabrir contexto de navegador, perfiles múltiples, dos carritos separados, reintento ante caída y olvido sin conexión conservado tras reinicio. El selector encontró una carrera de submit con el catálogo; test observado fallar y luego pasar al detener propagación.
- JavaScript: cuatro suites (recordado, sesión, captura y galería) aprobadas.
- Contrato: el cliente real MiDistri consumió JSON del endpoint real de Urban vía RequestFactory. Verifica recordar, perfiles, restaurar, perfil y revocar. No representa una prueba HTTPS entre dos servidores productivos.
- PostgreSQL0019→0020: sesión anterior preservada con FK nula; no inventa confianza y repetir no cambia datos. Se completaron además los otros esquemas de la base de QA antes de validar el plan global estricto.
- MariaDB0013→0014: captura, intervalos, eventos y carrito anterior preservados; repetición idempotente. Una tabla de dispositivo creada parcialmente, sin registro de0014, bloqueó instalación y restauración antes de copiar.
- Instaladores y ZIP contra bytes de las bases: Urban29 pruebas y portal28 pruebas aprobadas. Rechazo de cambios ajenos, ruta/venv incorrecto, migración ajena, rollback de esquema y restauración incompatible.
- PDFs: capítulo actual y primera página heredada renderizados e inspeccionados. Urban257 páginas y portal32 páginas; páginas anteriores conservadas.

Durante la regresión amplia se detectó que la fixture v580 no publicaba foto del producto, requisito vigente desde antes de esta entrega. Se corrigió sólo la fixture con una imagen sintética pública, sin relajar la validación productiva. Regresión posterior103/103.

Entorno local de pruebas: Python3.12 y las versiones Django existentes de QA (Urban5.2, portal3.2). La sintaxis de archivos Python del payload se comprueba además con los niveles3.10/3.7 previstos para cPanel. No se ejecutaron aquí los intérpretes reales de cPanel ni se verificó el sitio instalado. La revisión independiente y publicación se documentan en la entrega, sin inferir instalación productiva.
