from unittest.mock import patch
from django.test import TestCase,override_settings
from .test_operadores import PROFILE

@override_settings(MIDISTRI_ADMIN_ENABLED=True)
class MaterialesPanelTests(TestCase):
    def setUp(self):
        session=self.client.session;session['midistri_operador_token']='o'*32;session.save()
        self.profile=dict(PROFILE,permisos=['midistri.catalogo_gestionar'])
        self.data={'publicacion':3,'producto':'Parlante','videos':[{'id':1,'tipo':'mp4','descripcion':'Demo','seleccionado':False}]}
    def test_selector_y_revision_no_publican_en_get(self):
        with patch('midistri_portal.operadores.api',return_value=self.profile),patch('midistri_portal.materiales_views.api',return_value=self.data) as api:
            response=self.client.get('/portal/administrar/producto/314/videos/?distribuidora=20')
        self.assertContains(response,'Demo')
        self.assertEqual(api.call_args.args[0],'operator-media-products')
    def test_dist_ajena_rechazada(self):
        with patch('midistri_portal.operadores.api',return_value=self.profile):
            self.assertEqual(self.client.get('/portal/administrar/producto/314/videos/?distribuidora=61').status_code,403)
