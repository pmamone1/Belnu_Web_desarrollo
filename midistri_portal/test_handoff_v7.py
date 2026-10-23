from unittest.mock import patch
from urllib.parse import urlsplit, parse_qs
from django.core import signing
from django.test import TestCase, override_settings
from .test_operadores import PROFILE


@override_settings(MIDISTRI_ADMIN_ENABLED=True)
class HandoffV7Tests(TestCase):
    def start(self):
        r = self.client.get('/portal/administrar/entrada/')
        return parse_qs(urlsplit(r['Location']).query)['desafio'][0], r

    @patch('midistri_portal.operadores.api')
    def test_dos_desafios_no_se_pisan(self, api):
        api.return_value = {'perfil': PROFILE, 'session_token': 's' * 43}
        first, _ = self.start()
        second, _ = self.start()
        for nonce in (first, second):
            r = self.client.post('/portal/administrar/entrar/',
                {'codigo': 'c' * 43, 'desafio': nonce},
                HTTP_ORIGIN='https://sistema7000.belnu.com.ar')
            self.assertEqual(r.status_code, 302)
            self.assertEqual(r['Location'], '/portal/administrar/')

    def test_expirado_missing_cookie_origin_y_nonce_no_se_confunden(self):
        from . import operadores_views as views
        self.assertTrue(hasattr(views, 'clasificar_desafio'), 'Falta diagnóstico seguro por rama')
        from django.test import RequestFactory
        factory = RequestFactory()
        def request(cookie=None, origin='https://sistema7000.belnu.com.ar', nonce='n' * 43):
            r = factory.post('/portal/administrar/entrar/', {'desafio': nonce, 'codigo': 'c' * 43}, HTTP_ORIGIN=origin)
            if cookie is not None:
                r.COOKIES[views.nombre_cookie_desafio(nonce)] = cookie
            return r
        self.assertEqual(views.clasificar_desafio(request())[1], 'cookie_missing')
        self.assertEqual(views.clasificar_desafio(request(origin='https://evil.example'))[1], 'origin_invalid')
        self.assertEqual(views.clasificar_desafio(request('bad'))[1], 'signature_invalid')
        wrong = signing.dumps('w' * 43, salt=views.SALT)
        self.assertEqual(views.clasificar_desafio(request(wrong))[1], 'challenge_mismatch')
        with patch('django.core.signing.time.time', return_value=1000000000):
            old = signing.dumps('n' * 43, salt=views.SALT)
        with patch('django.core.signing.time.time', return_value=1000000601):
            self.assertEqual(views.clasificar_desafio(request(old))[1], 'challenge_expired')

    @patch('midistri_portal.operadores.api')
    def test_reinicio_no_reenvia_pase(self, api):
        response = self.client.post('/portal/administrar/entrar/',
            {'codigo': 'secret-c' * 6, 'desafio': 'secret-n' * 6},
            HTTP_ORIGIN='https://sistema7000.belnu.com.ar')
        self.assertContains(response, 'Iniciar de nuevo desde Urban Soft', status_code=403)
        self.assertContains(response, '/portal/administrar/entrada/', status_code=403)
        self.assertNotContains(response, 'secret-c', status_code=403)
        self.assertNotContains(response, 'secret-n', status_code=403)
        self.assertFalse(api.called)

    def test_cookies_acotadas_y_validacion_dura_diez_minutos(self):
        from . import operadores_views as views
        self.assertTrue(hasattr(views, 'nombre_cookie_desafio'), 'Falta cookie por desafío')
        for _ in range(12):
            nonce, response = self.start()
            cookie = response.cookies[views.nombre_cookie_desafio(nonce)]
            self.assertEqual(cookie['max-age'], 600)
            self.assertTrue(cookie['secure'])
            self.assertTrue(cookie['httponly'])
        active = [c for name, c in self.client.cookies.items()
                  if name.startswith('midistri_desafio_') and c.value]
        self.assertLessEqual(len(active), 10)

    @patch('midistri_portal.operadores.api')
    def test_referencia_segura_y_get_callback_recuperable(self, api):
        with self.assertLogs('midistri.handoff', level='WARNING') as captured:
            r = self.client.get('/portal/administrar/entrar/')
        self.assertEqual(r.status_code, 403)
        self.assertContains(r, 'Referencia', status_code=403)
        self.assertIn('cookie_missing', ' '.join(captured.output))
        self.assertFalse(api.called)

    @patch('midistri_portal.operadores.api')
    def test_entrada_y_salida_admin_conservan_navegador_y_login_pendiente(self, api):
        api.return_value={'perfil':PROFILE,'session_token':'s'*43}
        session=self.client.session
        session['midistri_browser']='browser-existing'
        session['midistri_login_pending']={'tab':{'vence':9999999999}}
        session['midistri_token']='legacy-seller'
        session.save()
        nonce,_=self.start()
        r=self.client.post('/portal/administrar/entrar/',{'codigo':'c'*43,'desafio':nonce},
            HTTP_ORIGIN='https://sistema7000.belnu.com.ar')
        self.assertEqual(r.status_code,302)
        self.assertEqual(self.client.session.get('midistri_browser'),'browser-existing')
        self.assertIn('tab',self.client.session.get('midistri_login_pending',{}))
        self.assertNotIn('midistri_token',self.client.session)
        self.client.post('/portal/administrar/salir/')
        self.assertEqual(self.client.session.get('midistri_browser'),'browser-existing')
        self.assertNotIn('midistri_operador_token',self.client.session)
