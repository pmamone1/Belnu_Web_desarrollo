from copy import deepcopy
from unittest.mock import patch
from django.test import SimpleTestCase, TestCase, override_settings
from .client import ApiError
from .contract import pedido_valido
from .models import Distribuidora, PedidoLocal
from .test_parciales_v6 import pedido, PERFIL
from .test_modalidades_v39 import modalidades


def propia(admite=True):
    return {'pedido_id':101,'modalidad':'consignado','plazo_dias':14,
        'fecha_confirmacion':'2026-11-02T10:00:00-03:00','vencimientos':[],
        'devoluciones_permitidas':admite,'gestion':'pedido','fecha_debito':'2026-11-16',
        'devolucion_productos':[{'producto_id':1,'admite_devolucion':admite}]}


def respuesta():
    data=pedido();data['pedidos']=[101];data['modalidades_pedidos']=[propia()]
    return data


class ContratoPedidoPropioTests(SimpleTestCase):
    def test_propio_con_o_sin_devolucion_se_conserva_sin_referencias_mutables(self):
        for admite in (True,False):
            data=respuesta();data['modalidades_pedidos']=[propia(admite)]
            result=pedido_valido(data,PERFIL)
            self.assertEqual(result['modalidades_pedidos'],[propia(admite)])
            data['modalidades_pedidos'][0]['devolucion_productos'][0]['admite_devolucion']=not admite
            self.assertEqual(result['modalidades_pedidos'][0]['devolucion_productos'][0]['admite_devolucion'],admite)

    def test_propio_acepta_plazos_y_fechas_configuradas_sin_calcularlas(self):
        for days in (7,14,21,30):
            data=respuesta();data['modalidades_pedidos'][0]['plazo_dias']=days
            data['modalidades_pedidos'][0]['fecha_debito']='2026-12-25'
            result=pedido_valido(data,PERFIL)
            self.assertEqual(result['modalidades_pedidos'][0]['fecha_debito'],'2026-12-25')

    def test_extension_incompleta_incoherente_o_privada_se_rechaza(self):
        changes=[('gestion','salida'),('gestion',True),('plazo_dias',35),('plazo_dias',True),
            ('modalidad','firme'),('fecha_debito','2026-02-30'),('fecha_debito','2026-11-16T10:00:00'),
            ('fecha_debito',None),('devoluciones_permitidas',False),('devolucion_productos',[]),
            ('devolucion_productos',None),('fecha_pago','2026-12-01'),('costo_proveedor','10.00'),
            ('vencimientos',[{'salida_id':2,'fecha_devolucion':'2026-11-16'}])]
        invalid=[]
        for key,value in changes:
            row=propia();row[key]=value;invalid.append(row)
        for key in ('gestion','fecha_debito','devolucion_productos'):
            row=propia();del row[key];invalid.append(row)
        for mutation in ({'producto_id':True},{'producto_id':0},{'producto_id':99},
                {'admite_devolucion':'true'},{'admite_devolucion':1},{'costo':'10.00'}):
            row=propia();row['devolucion_productos'][0].update(mutation);invalid.append(row)
        row=propia();row['devolucion_productos'].append(deepcopy(row['devolucion_productos'][0]));invalid.append(row)
        for row in invalid:
            with self.subTest(row=row):
                data=respuesta();data['modalidades_pedidos']=[row]
                with self.assertRaises(ApiError):pedido_valido(data,PERFIL)

    def test_dto_legado_permanece_igual_y_no_infiere_extension(self):
        data=pedido();data['pedidos']=[101,102];data['modalidades_pedidos']=modalidades()
        result=pedido_valido(data,PERFIL)
        self.assertEqual(result['modalidades_pedidos'],modalidades())
        self.assertNotIn('gestion',result['modalidades_pedidos'][0])
        data['modalidades_pedidos'][0]['devoluciones_permitidas']=False
        with self.assertRaises(ApiError):pedido_valido(data,PERFIL)


@override_settings(MIDISTRI_ENABLED=True)
class PantallaPedidoPropioTests(TestCase):
    def setUp(self):
        self.data=respuesta()
        self.data.pop('contrato_pedido');self.data.pop('atencion')
        self.data['items'].append({'producto_id':2,'cantidad':2,'nombre':'Bolsa','codigo':'B1','precio':'100.00','pvp':'200.00'})
        self.data['modalidades_pedidos'][0]['devolucion_productos'].append({'producto_id':2,'admite_devolucion':False})
        dist=Distribuidora.objects.create(id=20,nombre='Belgrano')
        self.local=PedidoLocal.objects.create(pk=self.data['id'],vendedor_id=7,distribuidora=dist,estado='ok',datos={'items':self.data['items']})
        session=self.client.session;session['midistri_token']='a'*43;session.save()

    def response(self,path):
        def api(action,**kwargs):
            if action=='profile':return PERFIL
            return {'pedidos':[deepcopy(self.data)]} if action=='orders' else deepcopy(self.data)
        with patch('midistri_portal.views.api',side_effect=api):return self.client.get(path)

    def test_historial_y_detalle_fecha_debito_y_devolucion_por_producto(self):
        for path in ('/portal/pedidos/','/portal/pedido/'+self.data['id']+'/'):
            with self.subTest(path=path):
                response=self.response(path)
                self.assertContains(response,'Fecha de débito')
                self.assertContains(response,'16/11/2026')
                self.assertContains(response,'Admite devolución')
                self.assertContains(response,'No admite devolución')
                self.assertContains(response,'14 días')
                self.assertNotContains(response,'La fecha de devolución todavía no está informada')
                self.assertNotContains(response,'por su salida')
                self.assertNotContains(response,'Urban')
                self.assertNotContains(response,'fecha_pago')
        self.local.refresh_from_db()
        self.assertEqual(self.local.datos['items'][0]['precio'],'25000.00')

    def test_metadata_invalida_preserva_ultima_respuesta_valida_y_precios(self):
        self.response('/portal/pedidos/')
        self.data['modalidades_pedidos'][0]['fecha_pago']='2099-01-01'
        response=self.response('/portal/pedido/'+self.data['id']+'/')
        self.assertContains(response,'Última información guardada')
        self.assertContains(response,'16/11/2026')
        self.assertNotContains(response,'2099')
        self.local.refresh_from_db()
        self.assertNotIn('fecha_pago',self.local.respuesta['modalidades_pedidos'][0])
        self.assertEqual(self.local.respuesta['items'][0]['precio'],'25000.00')
