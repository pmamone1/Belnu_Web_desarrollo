from types import SimpleNamespace as NS
from django.template.loader import render_to_string
from django.test import SimpleTestCase
from django.core.paginator import Paginator

class SkuCatalogoTests(SimpleTestCase):
    def render(self,code,**extra):
        p=NS(nombre='Producto de prueba',codigo=code,producto_id=141,precio=900,pvp=1100,display=1,imagenes=[],multimedia=[],categorias_catalogo=['Alimentos'],subcategoria_catalogo='',cantidad_carrito=0,indicadores={})
        data={'distribuidora':NS(pk=1),'productos':Paginator([p],50).page(1),'perfil':{'vendedor':1},'orden':'nombre'}
        data.update(extra)
        return render_to_string('midistri_portal/catalogo_productos.html',data)

    def test_sku_visible_en_letra_secundaria(self):
        html=self.render('ALM-0001')
        self.assertIn('<small class="producto-sku">SKU: ALM-0001</small>',html)
        self.assertIn('Cantidad de Producto de prueba',html)
        self.assertIn('Agregar / actualizar',html)

    def test_codigo_escapado_sin_insertar_html(self):
        html=self.render('<script>27</script>')
        self.assertIn('SKU: &lt;script&gt;27&lt;/script&gt;',html)
        self.assertNotIn('<script>27</script>',html)

    def test_sin_codigo_no_muestra_leyenda_vacia(self):
        self.assertNotIn('producto-sku',self.render(''))

    def test_catalogo_publico_tambien_muestra_codigo(self):
        html=self.render('PIL-083',perfil=None)
        self.assertIn('SKU: PIL-083',html)
        self.assertNotIn('Agregar / actualizar',html)

    def test_destacados_del_catalogo_tambien_muestran_sku(self):
        p=NS(nombre='Destacado',codigo='DEST-27',precio=900,pvp=1100,display=None)
        html=render_to_string('midistri_portal/destacados.html',{'destacados':[p],'distribuidora':NS(pk=1)})
        self.assertIn('<small class="producto-sku">SKU: DEST-27</small>',html)
