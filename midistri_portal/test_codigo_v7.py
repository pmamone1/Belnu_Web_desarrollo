from importlib.util import find_spec
from unittest.mock import patch
from uuid import uuid4
from django.test import TestCase,override_settings
from .models import Distribuidora,Publicacion
from .client import ApiError


@override_settings(MIDISTRI_LOGIN_CODIGO_ENABLED=True)
class CodigoPortalTests(TestCase):
    def setUp(self):
        self.assertIsNotNone(find_spec('midistri_portal.acceso_views'),'Falta ingreso con código')
        self.d=Distribuidora.objects.create(id=20,nombre='20 - Belgrano')
        Publicacion.objects.create(producto_id=1,distribuidora=self.d,nombre='Pilas',precio=100,pvp=150)
        self.profile={'id':7,'nombre':'Vendedor personal','distribuidora_id':20,'distribuidora':self.d.nombre,'linea':'12','lin':12,'vv':98}
        self.tab=str(uuid4());self.proof='a'*64
        self.headers={'HTTP_X_MIDISTRI_TAB':self.tab,'HTTP_X_MIDISTRI_TAB_PROOF':self.proof}
        self.patch=patch('midistri_portal.acceso_views.api',side_effect=self.response)
        self.patch.start();self.addCleanup(self.patch.stop)

    def response(self,action,**kwargs):
        if action=='capabilities':return {'login_codigo':1,'sesion_pestana':1,'login_codigo_tienda':1,'login_codigo_habilitado':True}
        if action=='login-code-request':return {'version':1,'solicitud':str(uuid4()),'mensaje':'Si ese Email está habilitado, recibirás un código para ingresar.'}
        if action=='login-code-verify':return {'version':1,'ticket':'t'*43,'identidades':[{'seleccion':'s'*32,'nombre':self.profile['nombre'],'distribuidora':self.d.nombre}]}
        if action=='login-code-select':return {'perfil':self.profile,'session_token':'SECRET_URBAN_TOKEN_'+'x'*40}
        raise AssertionError(action)

    def login(self):
        a=self.client.post('/portal/acceso/iniciar/',{'email':'seller@example.test'},**self.headers)
        self.assertEqual(a.status_code,200)
        return self.client.post('/portal/acceso/verificar/',{'codigo':'004321'},**self.headers)

    def test_otp_30min_no_es_timeout_sesion(self):
        self.assertContains(self.client.get('/portal/acceso/'),'30 minutos')
        result=self.login()
        self.assertEqual(result.status_code,200)
        self.assertEqual(result.json()['fase'],'dentro')
        self.assertNotIn('SECRET_URBAN_TOKEN',result.content.decode())
        from .models import SesionVendedorPortal
        row=SesionVendedorPortal.objects.get(pk=self.tab)
        self.assertFalse(row.revocado)
        self.assertEqual(row.vendedor_id,7)
        self.assertNotEqual(row.prueba_hash,self.proof)

    def test_cookie_sola_no_identifica(self):
        self.login()
        with patch('midistri_portal.views.api',return_value=self.profile):
            r=self.client.get('/portal/?distribuidora=20')
            self.assertNotContains(r,'Vendedor personal')
            r=self.client.get('/portal/?distribuidora=20',**self.headers)
            self.assertContains(r,'Vendedor personal')

    def test_seleccion_sin_ticket_no_entra(self):
        r=self.client.post('/portal/acceso/seleccionar/',{'seleccion':'s'*32},**self.headers)
        self.assertEqual(r.status_code,403)

    def test_contactos_ajenos_no_se_revelan(self):
        r=self.client.post('/portal/acceso/iniciar/',{'email':'unknown@example.test'},**self.headers)
        self.assertEqual(set(r.json()),{'fase','mensaje'})
        self.assertNotIn('Vendedor personal',r.content.decode())

    def test_api_caida_no_hace_login_legacy(self):
        with patch('midistri_portal.acceso_views.api',side_effect=ApiError('No disponible',503)):
            r=self.client.post('/portal/acceso/iniciar/',{'email':'seller@example.test'},**self.headers)
        self.assertEqual(r.status_code,503)
        from .models import SesionVendedorPortal
        self.assertFalse(SesionVendedorPortal.objects.exists())

    def test_eleccion_dos_vendedores_al_final_del_codigo_tiene_su_propio_plazo(self):
        original=self.response
        def response(action,**kwargs):
            result=original(action,**kwargs)
            if action=='login-code-verify':
                result['identidades'].append(dict(result['identidades'][0],seleccion='z'*32,nombre='Otro'))
            return result
        with patch('midistri_portal.acceso_views.api',side_effect=response):
            with patch('midistri_portal.acceso_views.time.time',return_value=10000):
                self.client.post('/portal/acceso/iniciar/',{'email':'seller@example.test'},**self.headers)
            with patch('midistri_portal.acceso_views.time.time',return_value=11799):
                r=self.client.post('/portal/acceso/verificar/',{'codigo':'004321'},**self.headers)
                self.assertEqual(r.json()['fase'],'elegir')
            with patch('midistri_portal.acceso_views.time.time',return_value=11801):
                r=self.client.post('/portal/acceso/seleccionar/',{'seleccion':'s'*32},**self.headers)
                self.assertEqual(r.status_code,200)
