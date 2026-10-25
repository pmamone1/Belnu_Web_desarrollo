from copy import deepcopy
from unittest.mock import patch
from django.test import TestCase,override_settings
from . import tests_pagina_v11 as fixture
from .models import Publicacion,Distribuidora

@override_settings(MIDISTRI_ADMIN_ENABLED=True,MIDISTRI_MULTIMEDIA_ENABLED=True)
class EditorNavegacionTests(TestCase):
    setUp=fixture.PaginaTests.setUp
    remoto=fixture.PaginaTests.remoto
    def test_azar_solo_catalogo_propio_valido_sin_duplicados_ni_publicar(self):
        from . import pagina as p
        from .pagina_models import EdicionPagina
        other=Distribuidora.objects.create(pk=61,nombre='Otra tienda')
        own=[]
        for i in range(4):
            own.append(Publicacion.objects.create(distribuidora=self.d,producto_id=i+1,nombre='P'+str(i),precio=10,pvp=15,imagenes=['https://example.test/foto'+str(i)+'.jpg'],multimedia=[{'tipo':'youtube','url':'https://www.youtube.com/watch?v=abc123'}]))
        Publicacion.objects.create(distribuidora=other,producto_id=99,nombre='Ajeno',precio=10,pvp=15,imagenes=['https://example.test/ajeno.jpg'])
        Publicacion.objects.create(distribuidora=self.d,producto_id=98,nombre='Inactivo',activa=False,precio=10,pvp=15,imagenes=['https://example.test/no.jpg'])
        Publicacion.objects.create(distribuidora=self.d,producto_id=97,nombre='Sin PVP',precio=10,pvp=0,imagenes=['https://example.test/no.jpg'])
        session=self.client.session;session['midistri_operador_token']='x'*43;session.save()
        with patch('midistri_portal.operadores.api',return_value=self.perfil),patch.object(p,'api',side_effect=self.remoto):
            page=p.borrador_tienda(self.perfil,20,'token');before=deepcopy(page.datos)
            r=self.client.post('/portal/administrar/pagina/dinamica/?distribuidora=20',{'accion':'aleatorio','cantidad':3},content_type='application/json')
            self.assertEqual(r.status_code,200)
            selected=r.json()['diapositivas'];self.assertEqual(len(selected),3)
            self.assertEqual(len(set(s['publicacion'] for s in selected)),3)
            self.assertTrue({s['publicacion'] for s in selected}<={a.pk for a in own})
            self.assertTrue(all(s['tipo']=='foto' for s in selected))
            page.refresh_from_db();self.assertEqual(page.datos,before);self.assertEqual(EdicionPagina.objects.count(),0)
            r=self.client.post('/portal/administrar/pagina/dinamica/?distribuidora=20',{'accion':'aleatorio','cantidad':20},content_type='application/json')
            self.assertEqual(len(r.json()['diapositivas']),4)
            for n in [0,21,True,'3']:
                self.assertEqual(self.client.post('/portal/administrar/pagina/dinamica/?distribuidora=20',{'accion':'aleatorio','cantidad':n},content_type='application/json').status_code,400)
            self.assertEqual(self.client.post('/portal/administrar/pagina/dinamica/?distribuidora=61',{'accion':'aleatorio','cantidad':2},content_type='application/json').status_code,403)
    def test_preview_cabezal_comercial_y_catalogo_seleccionable(self):
        from . import pagina as p
        from .editor_views import html_pagina
        data=p.inicial(self.t);data['mensajes']['titulo']='Título del catálogo'
        html=html_pagina(p.validar_pagina(data,20),self.d)
        self.assertIn('MiDistri - Pedidos Online - Belgrano</h1>',html)
        self.assertIn('data-editor-block="catalogo"',html)
