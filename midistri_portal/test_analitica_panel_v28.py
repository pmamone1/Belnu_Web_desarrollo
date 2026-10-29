from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from .test_analitica_informes_v28 import PROFILE
from .client import ApiError

class PanelAnaliticaTests(TestCase):
    def test_panel_y_doble_permiso(self):
        url='/portal/administrar/estadisticas/?distribuidora=20'
        with patch('midistri_portal.operadores.perfil_operador',return_value=PROFILE):
            r=self.client.get(url);self.assertEqual(r.status_code,200);self.assertContains(r,'Estadísticas de vendedores');self.assertContains(r,'Desde')
        with patch('midistri_portal.operadores.perfil_operador',return_value=dict(PROFILE,permisos=['pedidos.gestionar'])):
            self.assertEqual(self.client.get(url).status_code,403)
    def test_preparacion_csrf_owner_y_metodos(self):
        with patch('midistri_portal.operadores.perfil_operador',return_value=PROFILE):
            self.assertEqual(self.client.get('/portal/administrar/estadisticas/iniciar/').status_code,405)
            r=self.client.post('/portal/administrar/estadisticas/iniciar/',dict(distribuidora=20,desde='2026-10-01',hasta='2026-10-29'))
            self.assertEqual(r.status_code,200);ident=r.json()['id']
        with patch('midistri_portal.operadores.perfil_operador',return_value=dict(PROFILE,operador_id=99)):
            self.assertEqual(self.client.get('/portal/administrar/estadisticas/'+ident+'/').status_code,403)
            self.assertEqual(self.client.get('/portal/administrar/estadisticas/'+ident+'/excel/').status_code,403)
