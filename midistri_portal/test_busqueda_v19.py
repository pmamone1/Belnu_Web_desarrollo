from django.test import TestCase
from .models import Distribuidora, Publicacion
class BusquedaTests(TestCase):
    def setUp(self):
        self.d=Distribuidora.objects.create(pk=20,nombre='QA')
        self.otra=Distribuidora.objects.create(pk=61,nombre='Otra')
        def prod(d,pid,name,precio,pvp,**kw):return Publicacion.objects.create(distribuidora=d,producto_id=pid,nombre=name,codigo='SKU'+str(pid),categoria='Bazar',precio=precio,pvp=pvp,imagenes=['https://example.test/a.jpg'],**kw)
        self.a=prod(self.d,1,'Termo térmico',100,400);self.b=prod(self.d,2,'Termos acero',300,350);self.c=prod(self.d,3,'Vaso grande',200,500)
        prod(self.otra,4,'Termo privado',1,2);prod(self.d,5,'Termo inactivo',10,20,activa=False)
    def test_plural_acento_error_leve_y_conteo_solo_tienda_actual(self):
        for query in ('termos','termico','trmo'):
            r=self.client.get('/portal/',{'distribuidora':20,'q':query})
            self.assertEqual(r.status_code,200)
            self.assertContains(r,'Termo térmico');self.assertNotContains(r,'Termo privado');self.assertNotContains(r,'Termo inactivo')
        self.assertContains(self.client.get('/portal/',{'distribuidora':20,'q':'termos'}),'2 productos encontrados')
    def test_orden_precio_vendedor_y_pvp_conservando_busqueda(self):
        for order,ids in [('precio_asc',[1,3,2]),('precio_desc',[2,3,1]),('pvp_asc',[2,1,3]),('pvp_desc',[3,1,2])]:
            r=self.client.get('/portal/',{'distribuidora':20,'orden':order})
            self.assertEqual([p.producto_id for p in r.context['productos']],ids)
        r=self.client.get('/portal/',{'distribuidora':20,'q':'termos','orden':'precio_desc'})
        self.assertEqual([p.producto_id for p in r.context['productos']],[2,1])
        self.assertContains(r,'name="orden"')
