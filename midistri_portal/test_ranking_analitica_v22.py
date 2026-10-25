from django.test import TestCase
from . import test_orden_ventas_v20 as fixtures
from .models import Publicacion

class RankingAnaliticaTests(TestCase):
 def setUp(self):fixtures.OrdenVentasTests.setUp(self)
 def test_mas_vendidos_no_incluye_productos_sin_venta(self):
    r=self.client.get('/portal/',{'distribuidora':20,'orden':'ventas'})
    self.assertEqual([p.producto_id for p in r.context['productos']],[3,2])
    self.assertNotContains(r,'Alfa sin ventas');self.assertContains(r,'importe')
 def test_sin_ranking_no_se_disfraza_catalogo_alfabetico(self):
    Publicacion.objects.filter(distribuidora=self.d).update(indicadores={})
    r=self.client.get('/portal/',{'distribuidora':20,'orden':'ventas'})
    self.assertEqual(list(r.context['productos']),[])
    self.assertContains(r,'Ver todos los productos');self.assertNotContains(r,'se muestran los productos por nombre')
 def test_catalogo_por_nombre_sigue_incluyendo_productos_nuevos(self):
    r=self.client.get('/portal/',{'distribuidora':20,'orden':'nombre'})
    self.assertEqual([p.producto_id for p in r.context['productos']],[1,3,2])
