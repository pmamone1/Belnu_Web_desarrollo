from unittest.mock import patch
from django.test import TestCase,override_settings
from .models import Distribuidora,Publicacion,PedidoLocal
@override_settings(MIDISTRI_ENABLED=True)
class CatalogoTests(TestCase):
    def setUp(self):
        self.d=Distribuidora.objects.create(id=20,nombre='Belgrano')
        self.other=Distribuidora.objects.create(id=65,nombre='Barracas')
        self.p=Publicacion.objects.create(distribuidora=self.d,producto_id=1,nombre='Termo',categoria='Bazar',precio=25000,pvp=30000,imagenes=['https://sistema7000.belnu.com.ar/catalogo-imagenes/fixture.jpg'])
        Publicacion.objects.create(distribuidora=self.other,producto_id=2,nombre='Otro',categoria='Solo otra',precio=1,pvp=1,imagenes=['https://sistema7000.belnu.com.ar/catalogo-imagenes/fixture.jpg'])
    def test_publico_ve_ambos_precios_pero_no_puede_pedir(self):
        r=self.client.get('/portal/',{'distribuidora':20})
        self.assertContains(r,'Precio vendedor:');self.assertContains(r,'25000')
        self.assertContains(r,'30000')
        self.client.post('/portal/cantidad/',{'producto':1,'cantidad':2})
        self.assertFalse(self.client.session.get('midistri_cart'))
        self.client.post('/portal/enviar/');self.assertFalse(PedidoLocal.objects.exists())
    def test_categoria_y_busqueda_combinadas_solo_tienda_actual(self):
        Publicacion.objects.create(distribuidora=self.d,producto_id=3,nombre='Termo inactivo',categoria='Retirado',precio=1,pvp=1,activa=False,imagenes=['https://sistema7000.belnu.com.ar/catalogo-imagenes/fixture.jpg'])
        r=self.client.get('/portal/',{'distribuidora':20,'categoria':'Bazar','q':'Termo'})
        self.assertEqual(r.context['categoria'],'Bazar')
        self.assertEqual(list(r.context['categorias']),['Bazar'])
        self.assertEqual(len(r.context['productos']),1)
        r=self.client.get('/portal/',{'distribuidora':20,'categoria':'Solo otra'})
        self.assertEqual(len(r.context['productos']),0)
    @patch('midistri_portal.views.api')
    def test_sesion_fija_tienda_y_total_al_precio_vendedor(self,api):
        api.return_value={'id':7,'nombre':'Vendedor','linea':'12','distribuidora_id':20,'distribuidora':'Belgrano'}
        session=self.client.session;session['midistri_token']='a'*43;session.save()
        r=self.client.get('/portal/',{'distribuidora':65,'categoria':'Bazar','q':'Termo'})
        self.assertNotContains(r,'Solo otra')
        self.client.post('/portal/cantidad/',{'producto':1,'cantidad':2})
        r=self.client.get('/portal/carrito/')
        self.assertEqual(r.context['total'],50000)
        self.assertContains(r,'Total a precio vendedor')
        self.assertContains(r,'categoria=Bazar')
