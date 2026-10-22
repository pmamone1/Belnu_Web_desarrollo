from decimal import Decimal
from uuid import uuid4
from unittest.mock import patch
from django.test import TestCase
from midistri_portal.models import Distribuidora, Publicacion, PedidoLocal
from midistri_portal.client import api, ApiError

class ContractTests(TestCase):
    def setUp(self):
        self.d=Distribuidora.objects.create(id=20,nombre='20 - Belgrano')
        self.p=Publicacion.objects.create(producto_id=5,distribuidora=self.d,nombre='Pilas',precio=123.45,pvp=456.78)
        self.perfil={'id':7,'nombre':'Vendedor','linea':'Ruta','lin':112,'vv':5,
            'distribuidora_id':20,'distribuidora':'20 - Belgrano'}
        session=self.client.session;session['midistri_token']='a'*43;session.save()
    def test_catalogo_anonimo_solo_pvp(self):
        session=self.client.session;session.flush()
        response=self.client.get('/portal/?distribuidora=20')
        self.assertEqual(response.status_code,200)
        self.assertNotContains(response,'Tu precio')
        self.assertNotContains(response,'123.45')
        self.assertContains(response,'456.78')
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
    def test_muestra_lin_y_vv_en_cabecera_personal(self,server):
        server.return_value=self.perfil
        response=self.client.get('/portal/')
        self.assertContains(response,'LIN 112')
        self.assertContains(response,'VV 5')
    def test_cabeceras_privadas(self):
        response=self.client.get('/portal/activar/'+'a'*43+'/')
        self.assertEqual(response['Cache-Control'],'private, no-store')
        self.assertEqual(response['Referrer-Policy'],'no-referrer')
    @patch('midistri_portal.client.requests.request')
    def test_html_200_no_se_trata_como_remito(self,request):
        response=request.return_value.__enter__.return_value
        response.status_code=200;response.iter_content.return_value=[b'<html>Error</html>']
        response.headers={'Content-Type':'text/html'}
        with self.assertRaises(ApiError):api('document/'+str(uuid4()),token='a'*43,binary=True)
