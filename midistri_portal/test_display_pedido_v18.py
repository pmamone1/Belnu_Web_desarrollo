from unittest.mock import patch
from django.test import TestCase
from . import test_catalogo_v6 as fixture
from .models import PedidoLocal

class DisplayPedidoTests(TestCase):
    setUp=fixture.CatalogoTests.setUp
    def login(self):
        session=self.client.session;session['midistri_token']='a'*43;session.save()
    @patch('midistri_portal.views.api',return_value={'id':7,'nombre':'Vendedor','linea':'12','distribuidora_id':20,'distribuidora':'Belgrano'})
    def test_no_multiplo_no_modifica_carrito_valido(self,api):
        self.p.display=6;self.p.save();self.login()
        self.client.post('/portal/cantidad/',{'producto':1,'cantidad':6})
        self.client.post('/portal/cantidad/',{'producto':1,'cantidad':5})
        self.assertEqual(self.client.session['midistri_cart'],{'1':6})
        r=self.client.get('/portal/carrito/');self.assertEqual(r.context['total'],150000)
        self.assertContains(r,'x unidad');self.assertContains(r,'step="6"')
    @patch('midistri_portal.views.api',return_value={'id':7,'nombre':'Vendedor','linea':'12','distribuidora_id':20,'distribuidora':'Belgrano'})
    def test_checkout_cart_anterior_invalido_no_transmite(self,api):
        self.p.display=6;self.p.save();self.login()
        session=self.client.session;session['midistri_cart']={'1':5};session.save()
        r=self.client.get('/portal/carrito/');revision=r.context['revision']
        self.client.post('/portal/enviar/',{'revision':revision})
        self.assertFalse(PedidoLocal.objects.exists())
        self.assertFalse(any(c.args[0]=='orders' for c in api.call_args_list))
    @patch('midistri_portal.views.api',return_value={'id':7,'nombre':'Vendedor','linea':'12','distribuidora_id':20,'distribuidora':'Belgrano'})
    def test_sin_display_unidades_y_cero_quita(self,api):
        self.login();self.client.post('/portal/cantidad/',{'producto':1,'cantidad':5})
        self.assertEqual(self.client.session['midistri_cart'],{'1':5})
        self.p.display=6;self.p.save()
        self.client.post('/portal/cantidad/',{'producto':1,'cantidad':0})
        self.assertEqual(self.client.session['midistri_cart'],{})
