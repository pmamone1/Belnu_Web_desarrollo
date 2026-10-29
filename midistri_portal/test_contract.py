from decimal import Decimal
from uuid import uuid4
from unittest.mock import patch
from django.test import TestCase
from midistri_portal.models import Distribuidora, Publicacion, PedidoLocal
from midistri_portal.client import api, ApiError

class ContractTests(TestCase):
    def setUp(self):
        self.d=Distribuidora.objects.create(id=20,nombre='20 - Belgrano')
        self.p=Publicacion.objects.create(producto_id=5,distribuidora=self.d,nombre='Pilas',precio=123.45,pvp=456.78,imagenes=['https://sistema7000.belnu.com.ar/catalogo-imagenes/fixture.jpg'])
        self.perfil={'id':7,'nombre':'Vendedor','linea':'Ruta','lin':112,'vv':5,
            'distribuidora_id':20,'distribuidora':'20 - Belgrano'}
        session=self.client.session;session['midistri_token']='a'*43;session.save()
    def test_catalogo_anonimo_precio_vendedor_y_pvp(self):
        session=self.client.session;session.flush()
        response=self.client.get('/portal/?distribuidora=20')
        self.assertEqual(response.status_code,200)
        self.assertNotContains(response,'Tu precio')
        self.assertContains(response,'123,45')
        self.assertContains(response,'456,78')
    @patch('midistri_portal.views.api')
    def test_perfil_malformado_no_produce_500(self,server):
        server.return_value={'id':7,'nombre':None,'linea':'Ruta','distribuidora_id':20,'distribuidora':'Belgrano'}
        response=self.client.get('/portal/')
        self.assertEqual(response.status_code,503)
    @patch('midistri_portal.views.api')
    def test_respuesta_de_otro_vendedor_conserva_pendiente(self,server):
        ident=str(uuid4())
        session=self.client.session;session['midistri_cart']={'5':2};session['midistri_cart_id']=ident;session.save()
        def answer(action,**kwargs):
            if action=='profile':return self.perfil
            return {'id':ident,'vendedor_id':999,'distribuidora_id':20,'vendedor':'OTRO PRIVADO','estado':'recibido','items':[]}
        server.side_effect=answer
        self.client.get('/portal/carrito/')
        self.client.post('/portal/enviar/',{'revision':self.client.session['midistri_revision']})
        order=PedidoLocal.objects.get()
        self.assertEqual(order.estado,'pendiente')
        self.assertNotIn('OTRO PRIVADO',str(order.respuesta))
    @patch('midistri_portal.views.api')
    def test_respuesta_pedido_incompleta_conserva_intento(self,server):
        session=self.client.session;session['midistri_cart']={'5':1};session['midistri_cart_id']=str(uuid4());session.save()
        server.side_effect=lambda action,**kwargs:self.perfil if action=='profile' else {'id':kwargs['data']['id']}
        self.client.get('/portal/carrito/')
        response=self.client.post('/portal/enviar/',{'revision':self.client.session['midistri_revision']})
        self.assertEqual(response.status_code,302)
        self.assertEqual(PedidoLocal.objects.get().estado,'pendiente')
    @patch('midistri_portal.views.api')
    def test_cabecera_personal_solo_nombre_sin_lin_ni_vv(self,server):
        server.return_value=self.perfil
        response=self.client.get('/portal/')
        self.assertNotContains(response,'LIN 112')
        self.assertNotContains(response,'VV 5')
    def test_cabeceras_privadas(self):
        response=self.client.get('/portal/activar/'+'a'*43+'/')
        self.assertEqual(response['Cache-Control'],'private, no-store')
        self.assertEqual(response['Referrer-Policy'],'same-origin')
    @patch('midistri_portal.client.requests.request')
    def test_html_200_no_se_trata_como_remito(self,request):
        response=request.return_value.__enter__.return_value
        response.status_code=200;response.iter_content.return_value=[b'<html>Error</html>']
        response.headers={'Content-Type':'text/html'}
        with self.assertRaises(ApiError):api('document/'+str(uuid4()),token='a'*43,binary=True)

    def test_contrato_codigo_de_80_y_limite_81(self):
        from midistri_portal.contract import pedido_valido
        data={'id':str(uuid4()),'vendedor_id':7,'distribuidora_id':20,'vendedor':'Vendedor',
            'estado':'recibido','items':[{'producto_id':5,'cantidad':1,'nombre':'Pilas',
            'codigo':'S'*80,'precio':'123.45','pvp':'456.78'}]}
        self.assertEqual(pedido_valido(data,self.perfil)['items'][0]['codigo'],'S'*80)
        data['items'][0]['codigo']='S'*81
        with self.assertRaises(ApiError):pedido_valido(data,self.perfil)

    @patch('midistri_portal.views.api')
    def test_activar_https_con_csrf_y_referencia_local(self,server):
        from django.test import Client
        client=Client(enforce_csrf_checks=True)
        url='/portal/activar/'+'a'*43+'/'
        page=client.get(url,secure=True)
        self.assertEqual(page['Referrer-Policy'],'same-origin')
        token=client.cookies['csrftoken'].value
        server.return_value={'session_token':'b'*43,'perfil':self.perfil}
        response=client.post(url,{'csrfmiddlewaretoken':token},secure=True,
            HTTP_ORIGIN='https://testserver',HTTP_REFERER='https://testserver'+url)
        self.assertEqual(response.status_code,302)
        self.assertEqual(client.session['midistri_token'],'b'*43)

    def test_activar_rechaza_sin_token_y_origen_externo(self):
        from django.test import Client
        client=Client(enforce_csrf_checks=True)
        url='/portal/activar/'+'a'*43+'/'
        client.get(url,secure=True)
        response=client.post(url,{},secure=True,HTTP_ORIGIN='https://testserver')
        self.assertEqual(response.status_code,403)
        token=client.cookies['csrftoken'].value
        for origin in ('https://otro.example.test','null'):
            with self.subTest(origin=origin):
                response=client.post(url,{'csrfmiddlewaretoken':token},secure=True,HTTP_ORIGIN=origin)
                self.assertEqual(response.status_code,403)
        self.assertNotIn('midistri_token',client.session)
