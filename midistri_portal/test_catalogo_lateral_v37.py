from copy import deepcopy
from unittest.mock import patch
from urllib.parse import parse_qs,urlsplit
from django.test import TestCase
from django.template.loader import render_to_string
from . import test_rotacion_v32 as fixtures
from .models import Tienda

class CatalogoLateralTests(TestCase):
    setUp=fixtures.CatalogoRotacionTests.setUp
    get=fixtures.CatalogoRotacionTests.get
    def test_48_inicial_y_tamanos_validados_con_sesion_estable(self):
        a=self.get();b=self.get(page=2);c=self.get()
        ids=lambda r:[p.pk for p in r.context['productos']]
        self.assertEqual(len(a.context['productos']),48);self.assertEqual(ids(a),ids(c));self.assertFalse(set(ids(a))&set(ids(b)))
        for size in ('24','48','96','192'):
            r=self.get(page_size=size);self.assertEqual(r.context['productos'].paginator.per_page,int(size))
        for bad in ('0','-1','500000','abc','24.0'):
            self.assertEqual(self.get(page_size=bad).context['productos'].paginator.per_page,48)
    def test_enlaces_preservan_filtros_tamano_y_orden_sin_cambiar_ids(self):
        r=self.get(categoria='Alimentos',subcategoria='Alfajores',orden='precio_desc',q='Producto',page_size=24)
        self.assertEqual(len(r.context['productos']),24)
        link=r.context['catalogo_siguiente'];q=parse_qs(urlsplit(link).query)
        self.assertEqual(q['subcategoria'],['Alfajores']);self.assertEqual(q['page_size'],['24']);self.assertEqual(q['orden'],['precio_desc'])
        self.assertEqual(q['page'],['2']);self.assertContains(r,'Relevancia');self.assertContains(r,'catalogo-lateral')
    def test_promociones_dos_margenes_se_reunen_en_orden_y_centro_permanece(self):
        r=self.get();context={k:r.context[k] for k in ('distribuidora','productos','pagina','pagina_mensajes','presentacion','q','categoria','subcategoria','orden','categorias','subcategorias')}
        context['bloques']=[dict(id='right',tipo='texto',titulo='PROMO DERECHA37',texto='',estilo={'zona':'derecha'}),dict(id='left',tipo='texto',titulo='PROMO IZQUIERDA37',texto='',estilo={'zona':'izquierda'}),dict(id='center',tipo='texto',titulo='CENTRAL37',texto='',estilo={'zona':'centro'}),dict(id='catalogo',tipo='catalogo')]
        before=deepcopy(context['bloques']);html=render_to_string('midistri_portal/pagina_bloques.html',context)
        self.assertEqual(html.count('PROMO DERECHA37'),1);self.assertEqual(html.count('PROMO IZQUIERDA37'),1)
        sidebar=html.split('class="catalogo-lateral"')[1].split('</aside>')[0]
        self.assertLess(sidebar.index('PROMO DERECHA37'),sidebar.index('PROMO IZQUIERDA37'));self.assertNotIn('CENTRAL37',sidebar);self.assertIn('CENTRAL37',html)
        self.assertEqual(context['bloques'],before)
    def test_preview_y_publica_usan_48_y_lateral_sin_escribir_pagina(self):
        from .editor_views import html_pagina
        from .pagina import inicial
        tienda=Tienda.objects.create(distribuidora=self.d);data=inicial(tienda);before=deepcopy(data)
        html=html_pagina(data,self.d)
        self.assertIn('catalogo-lateral',html);self.assertEqual(html.count('class="producto-info"'),48);self.assertEqual(data,before)
    def test_productos_retirados_y_ajenos_siguen_excluidos(self):
        a=self.get();pub=a.context['productos'][0];pub.activa=False;pub.save()
        b=self.get(page_size=192);self.assertNotIn(pub.pk,[p.pk for p in b.context['productos']]);self.assertNotContains(b,'Ajeno')
    def test_legado_inicial_usa_mismo_lateral_y_dos_paginaciones(self):
        from .pagina import pagina_publica
        page=pagina_publica(self.d);page['inicial_anterior']=True
        with patch('midistri_portal.pagina.pagina_publica',return_value=page):r=self.get()
        self.assertContains(r,'catalogo-lateral');self.assertContains(r,'class="catalogo-paginacion"',count=2)

    def test_entrada_publica_sin_tienda_no_reserva_lateral_vacio(self):
        r=self.client.get('/portal/')
        self.assertEqual(r.status_code,200);self.assertNotContains(r,'class="catalogo-lateral"')
