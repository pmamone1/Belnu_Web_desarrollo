from unittest.mock import patch
from django.test import TestCase,Client,override_settings
from django.core import signing
from midistri_portal.client import ApiError

PROFILE={'version':1,'rol':'distribuidor','operador_id':7,'nombre':'Operador',
 'distribuidoras':[{'id':20,'nombre':'20 - Belgrano'}],
 'permisos':['midistri.catalogo_gestionar'],'financiero':False,'vence':'2099-01-01T00:00:00+00:00'}

@override_settings(MIDISTRI_ADMIN_ENABLED=True)
class OperadoresPortalTests(TestCase):
    def test_inicio_crea_desafio_y_destino_fijo(self):
        r=self.client.get('/portal/administrar/entrada/')
        self.assertEqual(r.status_code,302)
        self.assertTrue(r['Location'].startswith('https://sistema7000.belnu.com.ar/midistri/administrar/?desafio='))
        cookie=next(c for name,c in r.cookies.items() if name.startswith('midistri_desafio_'))
        self.assertTrue(cookie['secure'])
        self.assertTrue(cookie['httponly'])
        self.assertEqual(cookie['samesite'],'None')

    @patch('midistri_portal.operadores.api')
    def test_callback_rota_sesion_y_no_crea_usuario(self,api):
        from django.contrib.auth import get_user_model
        api.return_value={'perfil':PROFILE,'session_token':'private-session'*4}
        s=self.client.session;s['midistri_token']='vendedor';s['midistri_cart']={'1':5};s.save()
        count=get_user_model().objects.count()
        self.client.cookies['midistri_desafio']=signing.dumps('z'*43,salt='midistri.operador.desafio.v1')
        r=self.client.post('/portal/administrar/entrar/',{'codigo':'c'*43,'desafio':'z'*43},
                           HTTP_ORIGIN='https://sistema7000.belnu.com.ar')
        self.assertEqual(r.status_code,302)
        self.assertNotIn('midistri_token',self.client.session)
        self.assertNotIn('midistri_cart',self.client.session)
        self.assertEqual(self.client.session['midistri_operador_token'],'private-session'*4)
        self.assertEqual(get_user_model().objects.count(),count)

    def test_callback_sin_desafio_o_origen_ajeno_falla(self):
        for origin in ('https://evil.example',''):
            r=self.client.post('/portal/administrar/entrar/',{'codigo':'x'*43,'desafio':'z'*43},HTTP_ORIGIN=origin)
            self.assertEqual(r.status_code,403)

    @patch('midistri_portal.operadores.api')
    def test_caida_api_no_concede_panel(self,api):
        api.side_effect=ApiError('No disponible',503)
        s=self.client.session;s['midistri_operador_token']='x'*43;s.save()
        r=self.client.get('/portal/administrar/')
        self.assertEqual(r.status_code,503)

    def test_csrf_panel_y_staff_no_sustituye_sesion_delegada(self):
        c=Client(enforce_csrf_checks=True)
        self.assertEqual(c.post('/portal/administrar/salir/').status_code,403)
        self.assertEqual(self.client.get('/portal/administrar/').status_code,302)

    @patch('midistri_portal.operadores.api')
    def test_logout_revoca_y_limpia(self,api):
        api.return_value={'ok':True}
        s=self.client.session;s['midistri_operador_token']='x'*43;s.save()
        r=self.client.post('/portal/administrar/salir/')
        self.assertEqual(r.status_code,302)
        self.assertNotIn('midistri_operador_token',self.client.session)
        api.assert_called_once_with('operator-logout',method='POST',operator_token='x'*43)

    def test_bandera_apagada_bloquea_intercambio(self):
        with override_settings(MIDISTRI_ADMIN_ENABLED=False):
            self.assertEqual(self.client.get('/portal/administrar/entrada/').status_code,503)

    @patch('midistri_portal.operadores.api')
    def test_panel_con_distribuidora_ajena_no_da_500(self,api):
        api.return_value=PROFILE
        s=self.client.session;s['midistri_operador_token']='x'*43;s.save()
        response=self.client.get('/portal/administrar/?distribuidora=61')
        self.assertEqual(response.status_code,403)
