from unittest.mock import patch
from uuid import uuid4
from decimal import Decimal
from .test_codigo_v7 import CodigoPortalTests


class SesionPestanaTests(CodigoPortalTests):
    def test_recarga_navegacion_y_carrro_conservados_en_su_tab(self):
        self.login()
        with patch('midistri_portal.views.api',return_value=self.profile):
            r=self.client.post('/portal/cantidad/',{'producto':'1','cantidad':'2'},**self.headers)
            self.assertEqual(r.status_code,302)
            r=self.client.get('/portal/carrito/',**self.headers)
            self.assertEqual(r.context['total'],Decimal('200'))
            r=self.client.get('/portal/carrito/',**self.headers)
            self.assertEqual(r.context['total'],Decimal('200'))
        from .models import SesionVendedorPortal
        self.assertEqual(SesionVendedorPortal.objects.get(pk=self.tab).datos['midistri_cart'],{'1':2})

    def test_tab_nueva_cookie_sola_no_ve_identidad(self):
        self.login()
        for headers in ({},{'HTTP_X_MIDISTRI_TAB':str(uuid4()),'HTTP_X_MIDISTRI_TAB_PROOF':'a'*64}):
            r=self.client.get('/portal/carrito/',**headers)
            self.assertNotContains(r,'Vendedor personal',status_code=200 if not headers else 403)

    def test_salir_revoca_solo_esa_tab_y_no_panel(self):
        self.login()
        session=self.client.session;session['midistri_operador_token']='operator-private';session.save()
        with patch('midistri_portal.views.api'):
            r=self.client.post('/portal/salir/',**self.headers)
        self.assertEqual(r.status_code,302)
        self.assertEqual(self.client.session['midistri_operador_token'],'operator-private')
        from .models import SesionVendedorPortal
        self.assertTrue(SesionVendedorPortal.objects.get(pk=self.tab).revocado)
        self.assertEqual(self.client.get('/portal/carrito/',**self.headers).status_code,403)

    def test_no_recupera_credencial_cookie_legacy(self):
        session=self.client.session;session['midistri_token']='legacy-private';session.save()
        with patch('midistri_portal.views.api') as api:
            r=self.client.get('/portal/?distribuidora=20')
        self.assertNotContains(r,'Vendedor personal')
        self.assertFalse(api.called)

    def test_prueba_falsa_no_puede_leer_ni_cambiar_carrito(self):
        self.login()
        headers=dict(self.headers,HTTP_X_MIDISTRI_TAB_PROOF='b'*64)
        self.assertEqual(self.client.get('/portal/carrito/',**headers).status_code,403)
        self.assertEqual(self.client.post('/portal/cantidad/',{'producto':'1','cantidad':'2'},**headers).status_code,403)
