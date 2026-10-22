from copy import deepcopy
from uuid import uuid4
from unittest.mock import patch
from django.test import TestCase,SimpleTestCase,override_settings
from .client import ApiError
from .contract import pedido_valido
from .models import Distribuidora,PedidoLocal
from .test_operadores import PROFILE
PROFILE=dict(PROFILE,financiero=True,permisos=['pedidos.gestionar','pedidos.remitos','pedidos.remitos_ver'])

def pedido():
    return {'id':str(uuid4()),'vendedor_id':7,'distribuidora_id':20,'vendedor':'Vendedor',
        'estado':'emitido','contrato_pedido':2,
        'items':[{'producto_id':1,'cantidad':10,'nombre':'Termo','codigo':'T1','precio':'25000.00','pvp':'30000.00'}],
        'atencion':{'version':1,'estado':'parcial','items':[{'producto_id':1,'cantidad_preparada':6,'cantidad_cancelada':4}],
            'total_solicitado':'250000.00','total_preparado':'150000.00'}}
PERFIL={'id':7,'nombre':'Vendedor','distribuidora_id':20,'distribuidora':'Belgrano','linea':'12'}

class ContratoParcialTests(SimpleTestCase):
    def test_valida_y_preserva_parcial_y_rechaza_todos_los_desajustes(self):
        p=pedido();self.assertEqual(pedido_valido(p,PERFIL)['atencion']['total_preparado'],'150000.00')
        for kind in ('total','extra','cantidades','precio','version','sin_contrato'):
            x=deepcopy(p)
            if kind=='total':x['atencion']['total_preparado']='180000.00'
            if kind=='extra':x['atencion']['items'].append({'producto_id':2,'cantidad_preparada':1,'cantidad_cancelada':0})
            if kind=='cantidades':x['atencion']['items'][0]['cantidad_cancelada']=3
            if kind=='precio':x['items'][0]['precio']='30000.00'
            if kind=='version':x['contrato_pedido']=99
            if kind=='sin_contrato':x.pop('contrato_pedido')
            with self.subTest(kind=kind),self.assertRaises(ApiError):pedido_valido(x,PERFIL)

@override_settings(MIDISTRI_ENABLED=True,MIDISTRI_ADMIN_ENABLED=True)
class PantallaParcialTests(TestCase):
    def setUp(self):
        self.d=Distribuidora.objects.create(id=20,nombre='Belgrano')
        self.p=pedido()
        self.local=PedidoLocal.objects.create(pk=self.p['id'],vendedor_id=7,distribuidora=self.d,estado='ok',
            datos={'items':self.p['items']})
        session=self.client.session;session['midistri_token']='a'*43;session.save()
    def test_detalle_refresca_sin_lista_y_total_preparado(self):
        def api(action,**kw):return PERFIL if action=='profile' else self.p
        with patch('midistri_portal.views.api',side_effect=api):
            r=self.client.get('/portal/pedido/'+self.p['id']+'/')
        self.assertContains(r,'150000');self.assertContains(r,'Canceladas por falta de stock')
        self.local.refresh_from_db();self.assertEqual(self.local.estado,'emitido')
    def test_red_no_sobrescribe_ultima_copia(self):
        self.local.respuesta=self.p;self.local.estado='emitido';self.local.save()
        def api(action,**kw):
            if action=='profile':return PERFIL
            raise ApiError('Sin red',503)
        with patch('midistri_portal.views.api',side_effect=api):
            r=self.client.get('/portal/pedido/'+self.p['id']+'/')
        self.assertContains(r,'Última información guardada')
        self.local.refresh_from_db();self.assertEqual(self.local.respuesta,self.p)
    def test_panel_envia_cantidades_solo_en_revision(self):
        session=self.client.session;session['midistri_operador_token']='x'*43;session.save()
        original=deepcopy(self.p);original['estado']='ok';original.pop('atencion');original.pop('contrato_pedido')
        calls=[]
        def api(action,**kw):
            calls.append((action,kw))
            if action=='capabilities':return {'version':1,'contrato_pedido':2,'preparacion_parcial':True,'acceso_por_contacto':True}
            return {'pedido':original,'revision':str(uuid4()),'preparacion_previa':self.p['atencion']}
        with patch('midistri_portal.operadores.api',return_value=PROFILE),patch('midistri_portal.operadores_views.api',side_effect=api):
            r=self.client.post('/portal/administrar/pedido/'+self.p['id']+'/',
                {'distribuidora':20,'accion':'revisar_preparacion','incluir':['1'],'preparada_1':'6'})
        self.assertEqual(r.status_code,200)
        data=[kw['data'] for action,kw in calls if action=='operator-order'][-1]
        self.assertEqual(data['cantidades'],[{'producto_id':1,'cantidad_preparada':6}])
        self.assertContains(r,'150000.00')

    def test_capacidad_legacy_solo_404_405_sin_edicion_parcial(self):
        session=self.client.session;session['midistri_operador_token']='x'*43;session.save()
        p=deepcopy(self.p);p['estado']='ok';p.pop('atencion');p.pop('contrato_pedido')
        def api(action,**kw):
            if action=='capabilities':raise ApiError('Anterior',405)
            return {'pedido':p}
        with patch('midistri_portal.operadores.api',return_value=PROFILE),patch('midistri_portal.operadores_views.api',side_effect=api):
            r=self.client.get('/portal/administrar/pedido/'+self.p['id']+'/?distribuidora=20')
        self.assertContains(r,'únicamente la preparación completa');self.assertNotContains(r,'name="preparada_')

    def test_capacidad_no_autorizada_no_cae_a_legacy(self):
        session=self.client.session;session['midistri_operador_token']='x'*43;session.save()
        with patch('midistri_portal.operadores.api',return_value=PROFILE),patch('midistri_portal.operadores_views.api',side_effect=ApiError('No autorizado',403)) as api:
            r=self.client.get('/portal/administrar/pedido/'+self.p['id']+'/?distribuidora=20')
        self.assertEqual(r.status_code,403);self.assertEqual(api.call_count,1)

    def test_respuesta_v2_inconsistente_no_sobrescribe_copia(self):
        x=deepcopy(self.p);x['atencion']['total_preparado']='1.00'
        def api(action,**kw):return PERFIL if action=='profile' else x
        with patch('midistri_portal.views.api',side_effect=api):
            r=self.client.get('/portal/pedido/'+self.p['id']+'/')
        self.local.refresh_from_db();self.assertEqual(self.local.respuesta,{})
        self.assertContains(r,'Última información guardada')
