"""Portal assembly test; real cross-server HTTP is covered by local QA fixtures."""
from unittest.mock import patch
from . import test_codigo_v7 as fixture
from django.test import override_settings

@override_settings(MIDISTRI_LOGIN_CODIGO_ENABLED=True,MIDISTRI_MULTIMEDIA_ENABLED=True)
class FlujoPortalTests(fixture.CodigoPortalTests):
    def test_ingreso_carrito_galeria_y_salida_sin_perder_panel(self):
        self.login()
        session=self.client.session;session['midistri_operador_token']='operator-private';session.save()
        with patch('midistri_portal.views.api',return_value=self.profile):
            self.client.post('/portal/cantidad/',{'producto':'1','cantidad':'10'},**self.headers)
            response=self.client.get('/portal/carrito/',**self.headers)
        self.assertEqual(response.context['total'],1000)
        with patch('midistri_portal.views.api'):
            response=self.client.post('/portal/salir/',HTTP_ACCEPT='application/json',**self.headers)
        self.assertEqual(response.json()['url'],'/portal/')
        self.assertEqual(self.client.session['midistri_operador_token'],'operator-private')
        self.assertEqual(self.client.get('/portal/carrito/',**self.headers).status_code,403)
