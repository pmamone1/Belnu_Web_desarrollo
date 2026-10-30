# Corrección de compatibilidad de intervalos MiDistri29

Causa confirmada: MariaDB omite la restricción única condicional de IntervaloAnalitico de0012. La instalación y activación de Urban621/MiDistri28 están confirmadas por el usuario el30/10/2026, con4intervalos abiertos. No se presume que sean duplicados.

Plan de corrección: prueba que reproduceW036 sin índices parciales; reemplazo por clave única ordinaria (tienda,marcador nullable) y coherencia de abierto/cerrado; migración nueva0013 que valida duplicados antes de DDL y conserva fechas, eventos y estado de captura; prueba en MariaDB local, regresión y revisión final; documentación/PDF, ZIP y GitHub del portal. Urban621 se conserva, sin nuevo paquete Urban. SQLMode y duplicados estáticos previos se informan separados, sin cambiar configuración del servidor.

La columna vale1 sólo para intervalos abiertos yNULL para cerrados; múltiplesNULL permiten conservar el historial. La corrección no modifica la0012 aplicada, no fusiona ni elimina intervalos y se detiene si hay abiertos duplicados. Se conserva la captura activa. Si falla DDL en MariaDB, conservar salida y respaldo y corregir hacia adelante, sin repetir a ciegas ni revertir esquema.
