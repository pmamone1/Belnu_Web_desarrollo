from unittest.mock import patch
from django.test import TestCase,override_settings
from . import test_codigo_v7 as fixture
from .models import Distribuidora
@override_settings(MIDISTRI_LOGIN_CODIGO_ENABLED=True)
class CodigoTiendaPortalTests(TestCase):
    setUp=fixture.CodigoPortalTests.setUp
    response=fixture.CodigoPortalTests.response
    def test_selector_publico_sin_revelar_contactos(self):
        Distribuidora.objects.create(id=61,nombre='61 - Recova')
        r=self.client.get('/portal/acceso/?distribuidora=61')
        self.assertContains(r,'Elegí tu distribuidora')
        self.assertContains(r,'value="61" selected')
        self.assertNotContains(r,'seller@example.test')
    def test_tienda_viaja_a_urban(self):
        calls=[]
        def api(action,**kw):
            calls.append((action,kw))
            if action=='capabilities':return dict(self.response(action),login_codigo_tienda=1)
            return self.response(action,**kw)
        with patch('midistri_portal.acceso_views.api',side_effect=api):
            r=self.client.post('/portal/acceso/iniciar/',{'email':'seller@example.test','distribuidora':'20'},**self.headers)
        self.assertEqual(r.status_code,200)
        self.assertEqual(next(kw['data']['distribuidora'] for a,kw in calls if a=='login-code-request'),20)
    def test_tienda_inexistente_no_envia(self):
        with patch('midistri_portal.acceso_views.api',side_effect=self.response) as api:
            r=self.client.post('/portal/acceso/iniciar/',{'email':'seller@example.test','distribuidora':'999'},**self.headers)
        self.assertEqual(r.status_code,400)
        self.assertFalse(any(c.args[0]=='login-code-request' for c in api.call_args_list))
    def test_multitienda_exige_elegir(self):
        Distribuidora.objects.create(id=61,nombre='61 - Recova')
        r=self.client.post('/portal/acceso/iniciar/',{'email':'seller@example.test'},**self.headers)
        self.assertEqual(r.status_code,400)
