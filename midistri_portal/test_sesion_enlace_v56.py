import re

from django.conf import settings
from django.test import Client, TestCase, override_settings
from unittest.mock import patch


@override_settings(MIDISTRI_LOGIN_CODIGO_ENABLED=True)
class SesionEnlaceTests(TestCase):
    def token(self, response):
        self.assertContains(response, 'csrfmiddlewaretoken')
        return re.search(rb'name="csrfmiddlewaretoken" value="([^"]+)"', response.content)[1].decode()

    def comprobar_que_post_acepta(self, client, token):
        with patch('midistri_portal.dispositivos.activo', return_value=False):
            resultado = client.post('/portal/acceso/recordado/', {'csrfmiddlewaretoken': token},
                                    secure=True, HTTP_REFERER='https://testserver/portal/remitos/')
        self.assertEqual(resultado.status_code, 200)
        self.assertEqual(resultado.json(), {'fase': 'deshabilitado'})

    def test_los_enlaces_directos_preparan_proteccion_csrf_para_acceso_recordado(self):
        for ruta in ('/portal/remitos/', '/portal/estado-cuenta/'):
            with self.subTest(ruta=ruta):
                client = Client(enforce_csrf_checks=True)
                response = client.get(ruta, secure=True)
                self.assertIn(settings.CSRF_COOKIE_NAME, response.cookies)
                self.comprobar_que_post_acepta(client, self.token(response))

    def test_un_enlace_directo_conserva_el_secreto_csrf_de_otra_pestana(self):
        client = Client(enforce_csrf_checks=True)
        anterior = self.token(client.get('/portal/acceso/', secure=True))
        client.get('/portal/remitos/', secure=True)
        self.comprobar_que_post_acepta(client, anterior)
