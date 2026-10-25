from django.test import TestCase
from .models import Distribuidora, Publicacion
class IndicadoresTests(TestCase):
    def test_catalogo_muestra_distintivo_ranking_plazo_y_ultimas_unidades(self):
        d=Distribuidora.objects.create(pk=20,nombre='Tienda QA')
        Publicacion.objects.create(distribuidora=d,producto_id=1,nombre='Termo campeón',codigo='QA1',precio=100,pvp=150,imagenes=['https://example.test/termo.jpg'],indicadores={'ranking':1,'entrega':'24/48','ultimas_unidades':True})
        r=self.client.get('/portal/',{'distribuidora':20})
        self.assertContains(r,'Más vendidos en tu distribuidora');self.assertContains(r,'🏆');self.assertContains(r,'Entrega en 24/48 hs');self.assertContains(r,'¡Últimas unidades!');self.assertContains(r,'stock-ultimas')
    def test_contrato_rechaza_indicadores_invalidos_y_no_filtra_stock_privado(self):
        from .services import validar_snapshot
        data={'version':1,'completo':True,'distribuidoras':[{'id':20,'nombre':'QA'}],'publicaciones':[{'producto_id':1,'distribuidora_id':20,'nombre':'Termo','codigo':'Q','categoria':'','precio':'10.00','pvp':'15.00','imagenes':[],'indicadores':{'ranking':1,'entrega':'96','ultimas_unidades':False}}]}
        _,rows=validar_snapshot(data);self.assertEqual(rows[0][2]['indicadores']['ranking'],1)
        for invalid in ({'ranking':True,'entrega':'96','ultimas_unidades':False},{'ranking':11,'entrega':'96','ultimas_unidades':False},{'ranking':None,'entrega':'24','ultimas_unidades':False},{'ranking':1,'entrega':'96','ultimas_unidades':True},{'ranking':1,'entrega':'96','ultimas_unidades':False,'disponible':8}):
            data['publicaciones'][0]['indicadores']=invalid
            with self.assertRaises(ValueError):validar_snapshot(data)

    def test_tienda_antigua_mantiene_promociones_y_comparte_catalogo_actual(self):
        from .models import Tienda
        d=Distribuidora.objects.create(pk=61,nombre='Tienda antigua')
        Tienda.objects.create(distribuidora=d,bienvenida='Bienvenida anterior')
        Publicacion.objects.create(distribuidora=d,producto_id=2,nombre='Termo anterior',precio=10,pvp=20,imagenes=['https://example.test/a.jpg'],indicadores={'ranking':1,'entrega':'24/48','ultimas_unidades':True},display=6)
        from unittest.mock import patch
        with patch('midistri_portal.views.identificar',return_value={'id':7,'nombre':'QA','linea':'Ruta QA','lin':1,'vv':2,'distribuidora_id':61,'distribuidora':d.nombre}):
            r=self.client.get('/portal/',{'distribuidora':61})
        self.assertTemplateUsed(r,'midistri_portal/catalogo_inicial.html')
        for text in ('Bienvenida anterior','name="orden"','1 producto encontrado','Más vendidos en tu distribuidora','¡Últimas unidades!','step="6"'):
            self.assertContains(r,text)
        self.assertEqual(r.content.decode().count('alt="Logo de la tienda"'),1)
