from types import SimpleNamespace
from django.test import SimpleTestCase
from django.template.loader import render_to_string

class PresentacionCatalogoTests(SimpleTestCase):
    def test_selector_solo_mas_vendidos_sin_cambiar_criterio(self):
        html=render_to_string('midistri_portal/catalogo_productos.html',{'distribuidora':SimpleNamespace(pk=20),'orden':'ventas','ranking_disponible':True})
        self.assertIn('value="ventas" selected>Más vendidos</option>',html)
        self.assertNotIn('Más vendidos (consignación)',html)
    def test_boton_lateral_breve_y_centro_conserva_etiquetas(self):
        product=SimpleNamespace(nombre='Producto promocionado',precio=10,pvp=15,display=None)
        for zone in ['izquierda','derecha','centro']:
            block={'id':'promo','tipo':'banner','titulo':'Promoción','estilo':{'zona':zone},'enlace':'https://example.invalid/tienda','boton':'Consultar promoción de la semana','diapositivas':[{'tipo':'foto','titulo':'Foto promoción','texto':'Oferta','url':'https://example.invalid/foto.png','producto':product,'enlace':'https://example.invalid/oferta','boton':'Ver toda la promoción de este producto'}]}
            html=render_to_string('midistri_portal/pagina_bloque.html',{'b':block,'distribuidora':SimpleNamespace(pk=20)})
            from html.parser import HTMLParser
            class Links(HTMLParser):
                def __init__(self):super().__init__();self.labels=[];self.active=False
                def handle_starttag(self,tag,attrs):
                    if tag=='a' and ('class','button') in attrs:self.active=True;self.labels.append('')
                def handle_data(self,data):
                    if self.active:self.labels[-1]+=data
                def handle_endtag(self,tag):
                    if tag=='a':self.active=False
            parser=Links();parser.feed(html)
            with self.subTest(zone=zone):
                self.assertEqual([s.strip() for s in parser.labels],['Ver','Ver'] if zone!='centro' else ['Ver producto y pedir','Ver toda la promoción de este producto'])
                self.assertIn('https://example.invalid/oferta',html)
