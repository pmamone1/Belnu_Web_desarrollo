from django.test import SimpleTestCase
from .client import ApiError

class ReferenciasTests(SimpleTestCase):
    def test_canonica_y_compatibilidad(self):
        from .referencias import validar_referencia
        self.assertEqual(validar_referencia({}),{})
        data=dict(referencia_version=1,numero=123,codigo='MP-000123',fecha_pedido='2026-10-23',referencia='23/10/2026 · MP-000123')
        self.assertEqual(validar_referencia(data),data)
        self.assertEqual(validar_referencia({},data),data)

    def test_contradiccion_no_sobrescribe(self):
        from .referencias import validar_referencia
        data=dict(referencia_version=1,numero=123,codigo='MP-000123',fecha_pedido='2026-10-23',referencia='23/10/2026 · MP-000123')
        for changes in ({'numero':124},{'fecha_pedido':'2026-10-24'},{'codigo':'UUID'},{'referencia':'Otro'}):
            with self.assertRaises(ApiError):validar_referencia(dict(data,**changes),data)
