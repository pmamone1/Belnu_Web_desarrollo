from copy import deepcopy
from unittest.mock import patch
from django.test import TestCase, override_settings
from .models import Distribuidora, PedidoLocal
from .test_parciales_v6 import pedido, PERFIL

@override_settings(MIDISTRI_ENABLED=True)
class HistorialEntregadoTests(TestCase):
    def setUp(self):
        self.dist=Distribuidora.objects.create(id=20,nombre='Belgrano')
        self.data=pedido()
        self.profile=dict(PERFIL,lin=121,vv=194)
        self.local=PedidoLocal.objects.create(pk=self.data['id'],vendedor_id=7,distribuidora=self.dist,estado='ok',datos={'items':self.data['items']})
        session=self.client.session;session['midistri_token']='a'*43;session.save()
    def response(self,path):
        def remote(action,**kwargs):
            if action=='profile':return self.profile
            if action=='orders':return {'pedidos':[deepcopy(self.data)]}
            return deepcopy(self.data)
        with patch('midistri_portal.views.api',side_effect=remote):return self.client.get(path)
    def test_historial_actualiza_remito_emitido_y_omite_lin(self):
        self.data['atencion'].update(estado='total',total_preparado='250000.00')
        self.data['atencion']['items'][0].update(cantidad_preparada=10,cantidad_cancelada=0)
        r=self.response('/portal/pedidos/')
        self.assertContains(r,'<h3>Entregado</h3>',html=True)
        self.assertNotContains(r,'LIN 121');self.assertContains(r,'VV 194')
        self.local.refresh_from_db();self.assertEqual(self.local.estado,'emitido')
    def test_detalle_parcial_y_sin_linea(self):
        r=self.response('/portal/pedido/'+self.data['id']+'/')
        self.assertContains(r,'Pedido entregado parcialmente')
        self.assertNotContains(r,'LIN 121');self.assertNotContains(r,'Línea 12')
        self.assertContains(r,'150000');self.assertContains(r,'Canceladas por falta de stock: 4')
    def test_sin_remito_no_se_presenta_como_entregado(self):
        self.data.pop('atencion');self.data.pop('contrato_pedido')
        for state,label in [('recibido','Recibido por la distribuidora'),('ok','OK para preparar'),('cancelado','Cancelado por falta de stock')]:
            with self.subTest(state=state):
                self.data['estado']=state
                r=self.response('/portal/pedidos/')
                self.assertContains(r,label);self.assertNotContains(r,'Entregado')
    def test_catalogo_conserva_identidad_original(self):
        r=self.response('/portal/')
        self.assertContains(r,'LIN 121');self.assertContains(r,'VV 194')
