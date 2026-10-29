from django.test import TestCase
from .models import Distribuidora,Publicacion
class CatalogoLecturaTests(TestCase):
    def setUp(self):
        self.d=Distribuidora.objects.create(pk=20,nombre='Tienda')
        for pid,name in [(1,'Conitos Chocolate'),(2,'Cony Dulce'),(3,'Termo Acero')]:
            Publicacion.objects.create(distribuidora=self.d,producto_id=pid,nombre=name,codigo='PRD'+str(pid),precio='12500.00',pvp='16750.50',imagenes=['https://example.test/f.jpg'])
    def test_precios_con_miles_decimales_y_simbolo_inseparable(self):
        r=self.client.get('/portal/',{'distribuidora':20})
        self.assertContains(r,'class="importe-moneda">$&nbsp;12.500,00</span>',html=False)
        self.assertContains(r,'class="importe-moneda">$&nbsp;16.750,50</span>',html=False)
    def test_coni_variantes_y_error_leve(self):
        for q in ('coni','coní','koni'):
            with self.subTest(q=q):
                r=self.client.get('/portal/',{'distribuidora':20,'q':q,'orden':'nombre'})
                self.assertContains(r,'Conitos Chocolate');self.assertNotContains(r,'<h3>Termo Acero</h3>')
        self.assertContains(self.client.get('/portal/',{'distribuidora':20,'q':'coni','orden':'nombre'}),'Cony Dulce')
    def test_similitud_no_salta_filtros_y_busqueda_vacia_de_letras_no_rompe(self):
        Publicacion.objects.create(distribuidora=self.d,producto_id=4,nombre='Conito oculto',codigo='X',precio=100,pvp=200,activa=False,imagenes=['https://example.test/f.jpg'])
        Publicacion.objects.create(distribuidora=self.d,producto_id=5,nombre='Conito sin foto',codigo='Y',precio=100,pvp=200)
        r=self.client.get('/portal/',{'distribuidora':20,'q':'koni','orden':'nombre'})
        self.assertNotContains(r,'Conito oculto');self.assertNotContains(r,'Conito sin foto')
        self.assertEqual(self.client.get('/portal/',{'distribuidora':20,'q':'!!!','orden':'nombre'}).status_code,200)
