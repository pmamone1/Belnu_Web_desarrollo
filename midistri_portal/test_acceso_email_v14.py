from unittest.mock import patch
from uuid import uuid4
from django.test import TestCase,override_settings
from .models import Distribuidora,Publicacion,SesionVendedorPortal

@override_settings(MIDISTRI_LOGIN_CODIGO_ENABLED=True,MIDISTRI_ADMIN_ENABLED=True)
class AccesoEmailPortalTests(TestCase):
    def setUp(self):
        self.d=Distribuidora.objects.create(id=20,nombre='20 - Belgrano')
        Distribuidora.objects.create(id=61,nombre='61 - Recova')
        Publicacion.objects.create(producto_id=1,distribuidora=self.d,nombre='Pilas',precio=100,pvp=150,imagenes=['https://sistema7000.belnu.com.ar/catalogo-imagenes/fixture.jpg'])
        self.headers={'HTTP_X_MIDISTRI_TAB':str(uuid4()),'HTTP_X_MIDISTRI_TAB_PROOF':'a'*64}
        self.profile={'id':7,'nombre':'Kiosco','distribuidora_id':20,'distribuidora':self.d.nombre,'linea':'Línea12','lin':12,'vv':98}
        self.options=[{'seleccion':'s'*32,'nombre':'Kiosco · LIN12 · VV98','distribuidora':self.d.nombre,'tipo':'vendedor','distribuidora_id':20}]
        self.calls=[]
        p=patch('midistri_portal.acceso_views.api',side_effect=self.response)
        p.start();self.addCleanup(p.stop)
    def response(self,action,**kw):
        self.calls.append((action,kw))
        if action=='capabilities':return {'login_codigo':1,'sesion_pestana':1,'login_codigo_habilitado':True,'login_email_perfiles':1}
        if action=='login-code-email-request':return {'version':2,'solicitud':str(uuid4())}
        if action=='login-code-email-verify':return {'version':2,'ticket':'t'*43,'identidades':self.options}
        if action=='login-code-email-select':return {'tipo':'vendedor','perfil':self.profile,'session_token':'private-bearer-'+'x'*40}
        raise AssertionError(action)
    def iniciar(self):return self.client.post('/portal/acceso/iniciar/',{'email':'seller@example.test'},**self.headers)
    def test_portada_y_formulario_no_piden_distribuidora(self):
        for url in ('/portal/','/portal/acceso/','/portal/acceso/?distribuidora=61'):
            r=self.client.get(url)
            self.assertNotContains(r,'name="distribuidora"')
        self.assertContains(self.client.get('/portal/acceso/'),'name="email"')
    def test_solo_email_inicia_con_varias_tiendas_y_no_revela_perfiles(self):
        r=self.iniciar();self.assertEqual(r.status_code,200)
        self.assertEqual(set(r.json()),{'fase','mensaje'})
        payload=next(kw['data'] for a,kw in self.calls if a=='login-code-email-request')
        self.assertNotIn('distribuidora',payload)
        self.assertNotIn('Kiosco',r.content.decode())
    def test_un_perfil_entra_sin_otro_combo(self):
        self.iniciar();r=self.client.post('/portal/acceso/verificar/',{'codigo':'123456'},**self.headers)
        self.assertEqual(r.status_code,200);self.assertEqual(r.json(),{'fase':'dentro','url':'/portal/'})
        self.assertEqual(SesionVendedorPortal.objects.get().vendedor_id,7)
        self.assertNotIn('private-bearer',r.content.decode())
    def test_varios_perfiles_solo_despues_de_validar(self):
        self.options.append({'seleccion':'q'*32,'nombre':'Operador','distribuidora':'61 - Recova','tipo':'administracion','distribuidora_id':61})
        self.iniciar();r=self.client.post('/portal/acceso/verificar/',{'codigo':'123456'},**self.headers)
        self.assertEqual(r.json()['fase'],'elegir');self.assertEqual(len(r.json()['identidades']),2)
        self.assertEqual(r.json()['identidades'][1]['tipo'],'administracion')
        self.assertFalse(SesionVendedorPortal.objects.exists())
    def test_administracion_no_crea_sesion_vendedor_ni_staff_y_usa_cookie_de_desafio(self):
        self.options[0]['tipo']='administracion'
        original=self.response
        def api(action,**kw):
            if action=='login-code-email-select':return {'tipo':'administracion','continuacion':'c'*43,'distribuidora_id':20}
            return original(action,**kw)
        with patch('midistri_portal.acceso_views.api',side_effect=api):
            self.iniciar();r=self.client.post('/portal/acceso/verificar/',{'codigo':'123456'},**self.headers)
        self.assertEqual(r.status_code,200)
        self.assertTrue(r.json()['url'].startswith('https://sistema7000.belnu.com.ar/midistri/ingreso-email/?'))
        cookies=[c for n,c in r.cookies.items() if n.startswith('midistri_desafio_')]
        self.assertEqual(len(cookies),1);self.assertTrue(cookies[0]['httponly']);self.assertTrue(cookies[0]['secure'])
        self.assertFalse(SesionVendedorPortal.objects.exists())
    def test_capacidad_incompatible_detiene_sin_request(self):
        with patch('midistri_portal.acceso_views.api',return_value={'login_codigo':1,'sesion_pestana':1,'login_codigo_habilitado':True}):
            r=self.iniciar()
        self.assertEqual(r.status_code,503)
    def test_api_no_puede_proponer_tipo_de_perfil_desconocido(self):
        self.options[0]['tipo']='superusuario'
        self.iniciar();r=self.client.post('/portal/acceso/verificar/',{'codigo':'123456'},**self.headers)
        self.assertNotEqual(r.status_code,200);self.assertFalse(SesionVendedorPortal.objects.exists())
