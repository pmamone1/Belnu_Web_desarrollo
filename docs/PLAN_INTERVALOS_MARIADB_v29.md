# Corrección de compatibilidad de intervalos MiDistri 29

Causa confirmada: MariaDB omite la restricción única condicional de IntervaloAnalitico de 0012. La instalación y activación de Urban 621/MiDistri 28 están confirmadas por el usuario el 30/10/2026, con 4 intervalos abiertos. No se presume que sean duplicados.

Plan de corrección: prueba que reproduce W036 sin índices parciales; reemplazo por clave única ordinaria (tienda, marcador nullable) y coherencia de abierto/cerrado; migración nueva 0013 que valida duplicados antes de DDL y conserva fechas, eventos y estado de captura; prueba en MariaDB local, regresión y revisión final; documentación/PDF, ZIP y GitHub del portal. Urban 621 se conserva, sin nuevo paquete Urban. SQLMode y duplicados estáticos previos se informan separados, sin cambiar configuración del servidor.

La columna vale 1 sólo para intervalos abiertos y NULL para cerrados; múltiples NULL permiten conservar el historial. La corrección no modifica la 0012 aplicada, no fusiona ni elimina intervalos y se detiene si hay abiertos duplicados. Se conserva la captura activa. Si falla DDL en MariaDB, conservar salida y respaldo y corregir hacia adelante, sin repetir a ciegas ni revertir esquema.
