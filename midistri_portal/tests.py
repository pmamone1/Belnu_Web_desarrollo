from decimal import Decimal
from uuid import uuid4
from unittest.mock import patch
from django.test import TestCase, override_settings
from django.urls import reverse
from .models import Distribuidora, Publicacion, PedidoLocal, Sincronizacion
from .services import aplicar_snapshot
from .client import ApiError

@override_settings(MIDISTRI_ENABLED=True, URBAN_API_BASE='https://sistema7000.belnu.com.ar/midistri/api/')
class PortalTests(TestCase):
    def setUp(self):
        self.d=Distribuidora.objects.create(id=20,nombre='20 - Belgrano')
        self.otra=Distribuidora.objects.create(id=61,nombre='61 Recova')
        self.p=Publicacion.objects.create(producto_id=1,distribuidora=self.d,nombre='Pilas Urban',precio=100,pvp=150)
        Publicacion.objects.create(producto_id=2,distribuidora=self.otra,nombre='Solo Recova',precio=100,pvp=150)
        self.perfil={'id':7,'nombre':'Pablo','distribuidora_id':20,'distribuidora':'20 - Belgrano','linea':'12'}
        session=self.client.session;session['midistri_token']='a'*43;session.save()
    @patch('midistri_portal.views.api')
    def test_catalogo_segregado_y_nombre(self,api):
        api.return_value=self.perfil
        r=self.client.get('/portal/')
        self.assertContains(r,'MiDistri - Pedidos Online - 20 - Belgrano')
        self.assertContains(r,'Pilas Urban');self.assertNotContains(r,'Solo Recova')
    @patch('midistri_portal.views.api')
    def test_get_invitacion_no_consume(self,api):
        r=self.client.get('/portal/activar/'+'a'*43+'/')
        self.assertEqual(r.status_code,200);api.assert_not_called()
    def test_snapshot_incompleto_no_borra_catalogo(self):
        with self.assertRaises(ValueError):aplicar_snapshot({'version':1,'completo':False})
        self.assertEqual(Publicacion.objects.count(),2)
    def test_snapshot_completo_retira_bajas_y_preserva_historicos(self):
        data={'version':1,'completo':True,'distribuidoras':[{'id':20,'nombre':'20 - Belgrano'}],
            'publicaciones':[{'producto_id':1,'distribuidora_id':20,'nombre':'Pilas nuevas','codigo':'P1','categoria':'Pilas','precio':'110.00','pvp':'150.00','imagenes':[],'display':None}]}
        aplicar_snapshot(data)
        self.assertEqual(list(Publicacion.objects.filter(activa=True).values_list('nombre',flat=True)),['Pilas nuevas'])
        self.assertFalse(Distribuidora.objects.get(pk=61).activa)
    @patch('midistri_portal.views.api')
    def test_fallo_red_conserva_pedido_para_reintentar(self,api):
        def response(action,**kwargs):
            if action=='profile':return self.perfil
            raise ApiError('No se pudo conectar.',503)
        api.side_effect=response
        session=self.client.session;session['midistri_cart']={'1':2};session['midistri_cart_id']=str(uuid4());session.save()
        self.client.get('/portal/carrito/')
        r=self.client.post('/portal/enviar/',{'observaciones':'Test','revision':self.client.session['midistri_revision']})
        self.assertEqual(r.status_code,302)
        self.assertEqual(PedidoLocal.objects.count(),1)
        self.assertEqual(PedidoLocal.objects.get().estado,'pendiente')
    @patch('midistri_portal.views.api')
    def test_ruta_legacy_no_muestra_catalogo_antiguo(self,api):
        r=self.client.get('/store/category/colecciones-la-nacion/the-doors/')
        self.assertRedirects(r,'/portal/',fetch_redirect_response=False)
    @patch('midistri_portal.views.api')
    def test_otro_vendedor_no_accede_pedido(self,api):
        api.return_value=self.perfil
        p=PedidoLocal.objects.create(vendedor_id=99,distribuidora=self.d,datos={'items':[]})
        self.assertEqual(self.client.get('/portal/pedido/'+str(p.pk)+'/').status_code,404)

    @patch('midistri_portal.views.api')
    def test_producto_retirado_se_puede_quitar_del_carrito(self,api):
        api.return_value=self.perfil
        self.p.activa=False;self.p.save()
        session=self.client.session;session['midistri_cart']={'1':2};session.save()
        self.client.post('/portal/cantidad/',{'producto':'1','cantidad':'0','origen':'carrito'})
        self.assertEqual(self.client.session.get('midistri_cart',{}),{})

    @patch('midistri_portal.views.api')
    def test_cambio_precio_despues_de_revision_requiere_confirmar(self,api):
        api.return_value=self.perfil
        session=self.client.session;session['midistri_cart']={'1':2};session['midistri_cart_id']=str(uuid4());session.save()
        self.client.get('/portal/carrito/')
        revision=self.client.session.get('midistri_revision','')
        self.p.precio=120;self.p.save()
        self.client.post('/portal/enviar/',{'revision':revision})
        self.assertFalse(PedidoLocal.objects.exists())
