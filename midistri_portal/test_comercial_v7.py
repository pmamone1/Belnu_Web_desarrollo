from importlib.util import find_spec
from unittest.mock import patch
from django.test import TestCase,override_settings
from .test_operadores import PROFILE


@override_settings(MIDISTRI_ADMIN_ENABLED=True)
class ComercialPanelTests(TestCase):
    def setUp(self):
        self.assertIsNotNone(find_spec('midistri_portal.comercial_views'),'Falta configuración de mensajes en panel')
        session=self.client.session;session['midistri_operador_token']='op'*22;session.save()
        self.profile=dict(PROFILE,permisos=['midistri.tienda_configurar'])
        self.data={'version':1,'distribuidora_id':20,'revision':0,'nombre_comercial':'Mi Tienda',
            'email_respuesta':'reply@example.test','asunto_acceso':'Entrá al portal',
            'texto_acceso':'Podés hacer tu pedido','texto_entrega':''}

    def test_solo_perfil_autorizado_configura(self):
        with patch('midistri_portal.operadores.api',return_value=self.profile),patch('midistri_portal.comercial_views.api',return_value=self.data):
            r=self.client.get('/portal/administrar/comunicacion/?distribuidora=20')
        self.assertContains(r,'reply@example.test')
        with patch('midistri_portal.operadores.api',return_value=self.profile):
            r=self.client.get('/portal/administrar/comunicacion/?distribuidora=61')
        self.assertEqual(r.status_code,403)

    def test_api_caida_no_anuncia_guardado(self):
        from .client import ApiError
        with patch('midistri_portal.operadores.api',return_value=self.profile),patch('midistri_portal.comercial_views.api',side_effect=ApiError('No disponible',503)):
            r=self.client.post('/portal/administrar/comunicacion/',dict(self.data,distribuidora=20,operacion='test'))
        self.assertEqual(r.status_code,503)
