from copy import deepcopy
from unittest.mock import patch
from django.test import TestCase,override_settings
from .test_operadores import PROFILE
from .client import ApiError
PROFILE=dict(PROFILE,permisos=['pedidos.gestionar'])
MIME='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
@override_settings(MIDISTRI_ENABLED=True,MIDISTRI_ADMIN_ENABLED=True)
class AbastecimientoPortalTests(TestCase):
    def setUp(self):
        s=self.client.session;s['midistri_operador_token']='x'*43;s.save()
    def test_descarga_scoped_y_formulario(self):
        with patch('midistri_portal.operadores.api',return_value=PROFILE),patch('midistri_portal.operadores_views.api',return_value=b'validated-xlsx') as api:
            r=self.client.get('/portal/administrar/abastecimiento/?distribuidora=20')
            self.assertContains(r,'Excel para Urban Point')
            r=self.client.post('/portal/administrar/abastecimiento/',{'distribuidora':20,'desde':'2026-10-01','hasta':'2026-10-22','estado':'pendientes'})
        self.assertEqual(r.status_code,200);self.assertEqual(r['Content-Type'],MIME)
        self.assertEqual(api.call_args.args[0],'operator-order-supply')
        self.assertEqual(api.call_args.kwargs['binary_mime'],MIME)
        self.assertEqual(api.call_args.kwargs['data']['distribuidora'],20)
    def test_otra_tienda_o_permiso_insuficiente_no_consulta(self):
        for profile,did in ((PROFILE,65),(dict(PROFILE,permisos=['midistri.catalogo_gestionar']),20)):
            with patch('midistri_portal.operadores.api',return_value=profile),patch('midistri_portal.operadores_views.api') as api:
                r=self.client.post('/portal/administrar/abastecimiento/',{'distribuidora':did})
            self.assertEqual(r.status_code,403);api.assert_not_called()
    def test_binario_invalido_no_se_ofrece(self):
        with patch('midistri_portal.operadores.api',return_value=PROFILE),patch('midistri_portal.operadores_views.api',side_effect=ApiError('El Excel no es válido.')):
            r=self.client.post('/portal/administrar/abastecimiento/',{'distribuidora':20})
        self.assertEqual(r.status_code,503);self.assertNotIn('Content-Disposition',r)
