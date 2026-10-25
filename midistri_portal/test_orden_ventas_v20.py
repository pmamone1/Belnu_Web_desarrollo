from django.test import TestCase
from .models import Distribuidora,Publicacion

class OrdenVentasTests(TestCase):
    def setUp(self):
        self.d=Distribuidora.objects.create(pk=20,nombre='Tienda QA')
        self.other=Distribuidora.objects.create(pk=61,nombre='Tienda ajena')
        for pid,name,pos in [(1,'Alfa sin ventas',None),(2,'Zeta vendido',12),(3,'Beta campeon',1)]:
            Publicacion.objects.create(distribuidora=self.d,producto_id=pid,nombre=name,precio=10,pvp=20,imagenes=['https://example.test/a.jpg'],indicadores={'ranking':pos if pos and pos<=10 else None,'entrega':'96','ultimas_unidades':False,'orden_ventas':pos})
        Publicacion.objects.create(distribuidora=self.other,producto_id=4,nombre='Venta ajena',precio=10,pvp=20,imagenes=['https://example.test/a.jpg'],indicadores={'orden_ventas':1})
    def test_orden_ventas_completo_no_solo_top_diez_y_no_amplia_alcance(self):
        r=self.client.get('/portal/',{'distribuidora':20,'orden':'ventas'})
        self.assertEqual([p.producto_id for p in r.context['productos']],[3,2])
        self.assertContains(r,'value="ventas" selected');self.assertNotContains(r,'Venta ajena')
    def test_sin_datos_completos_informa_que_no_inventa_ranking(self):
        Publicacion.objects.filter(distribuidora=self.d).update(indicadores={})
        r=self.client.get('/portal/',{'distribuidora':20,'orden':'ventas'})
        self.assertContains(r,'No hay productos con ranking de ventas disponible')
        self.assertEqual(list(r.context['productos']),[])
    def test_orden_opcional_compatible_con_snapshot_v19_y_rechaza_booleanos(self):
        from .services import validar_snapshot
        data={'version':1,'completo':True,'distribuidoras':[{'id':20,'nombre':'QA'}],'publicaciones':[{'producto_id':1,'distribuidora_id':20,'nombre':'Producto','codigo':'Q','categoria':'','precio':'10.00','pvp':'20.00','imagenes':[],'indicadores':{'ranking':None,'entrega':'96','ultimas_unidades':False},'orden_ventas':12}]}
        _,rows=validar_snapshot(data);self.assertEqual(rows[0][2]['indicadores'].get('orden_ventas'),12)
        data['publicaciones'][0]['orden_ventas']=True
        with self.assertRaises(ValueError):validar_snapshot(data)
