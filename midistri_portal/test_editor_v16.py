from copy import deepcopy
from unittest.mock import patch
from uuid import uuid4
from django.test import TestCase,override_settings
from django.core.exceptions import ValidationError
from . import tests_pagina_v11 as fixture
from .models import Publicacion

@override_settings(MIDISTRI_ADMIN_ENABLED=True,MIDISTRI_MULTIMEDIA_ENABLED=True)
class EditorTests(TestCase):
    setUp=fixture.PaginaTests.setUp
    remoto=fixture.PaginaTests.remoto
    def test_estilo_limites_y_escape(self):
        from .editor_estilos import validar_estilo,estilo_css
        d=validar_estilo({});self.assertEqual(d['alto_pc'],240);self.assertEqual(d['alto_movil'],160)
        for x in ({'alto_pc':9999},{'fondo':'red;position:fixed'},{'fuente':'url(http://bad)'},{'zona':'otra'},{'tamano':True}):
            with self.assertRaises(ValidationError):validar_estilo(x)
        self.assertNotIn('url',estilo_css(d))
    def test_ajax_guarda_con_estilo_sin_publicar_y_conflicto(self):
        from . import pagina as p
        session=self.client.session;session['midistri_operador_token']='x'*43;session.save()
        with patch('midistri_portal.operadores.api',return_value=self.perfil),patch.object(p,'api',side_effect=self.remoto):
            draft=p.borrador_tienda(self.perfil,20,'token');original=deepcopy(p.pagina_publica(self.d))
            data=deepcopy(draft.datos);data['bloques'][0]['estilo']={'alto_pc':180,'zona':'derecha','color':'#112233'}
            payload={'accion':'guardar','revision':draft.revision,'operacion':str(uuid4()),'datos':data}
            r=self.client.post('/portal/administrar/pagina/dinamica/?distribuidora=20',payload,content_type='application/json')
            self.assertEqual(r.status_code,200);self.assertEqual(r.json()['datos']['bloques'][0]['estilo']['alto_pc'],180)
            self.assertEqual(p.pagina_publica(self.d),original)
            self.assertEqual(self.client.post('/portal/administrar/pagina/dinamica/?distribuidora=20',payload,content_type='application/json').status_code,200)
            payload['operacion']=str(uuid4());payload['datos']['mensajes']['titulo']='Otro'
            self.assertEqual(self.client.post('/portal/administrar/pagina/dinamica/?distribuidora=20',payload,content_type='application/json').status_code,409)
    def test_producto_sin_foto_o_pvp_no_es_visible(self):
        from .catalogo_elegible import elegibles
        for ident,images,price,pvp in [(1,[],10,15),(2,['https://example.test/a.jpg'],10,0),(3,['https://example.test/a.jpg'],10,15)]:
            Publicacion.objects.create(producto_id=ident,distribuidora=self.d,nombre='P'+str(ident),precio=price,pvp=pvp,imagenes=images)
        self.assertEqual(list(elegibles(Publicacion.objects.all()).values_list('producto_id',flat=True)),[3])

    def test_ajax_tenant_ajeno_y_permiso_revocado_rechazados(self):
        from . import pagina as p
        session=self.client.session;session['midistri_operador_token']='x'*43;session.save()
        with patch('midistri_portal.operadores.api',return_value=self.perfil),patch.object(p,'api',side_effect=self.remoto):
            r=self.client.post('/portal/administrar/pagina/dinamica/?distribuidora=61',{'accion':'cargar'},content_type='application/json')
            self.assertEqual(r.status_code,403)
            self.assertEqual(self.client.post('/portal/administrar/pagina/dinamica/?distribuidora=20',[],content_type='application/json').status_code,400)
        with patch('midistri_portal.operadores.api',return_value=dict(self.perfil,permisos=['midistri.catalogo_gestionar'])):
            r=self.client.post('/portal/administrar/pagina/dinamica/?distribuidora=20',{'accion':'cargar'},content_type='application/json')
            self.assertEqual(r.status_code,403)
    def test_texto_editable_excluye_precios_y_producto(self):
        from django.template.loader import render_to_string
        from . import pagina as p
        pub=Publicacion.objects.create(producto_id=7,distribuidora=self.d,nombre='Nombre protegido',precio=77,pvp=99,imagenes=['https://example.test/foto.jpg'])
        data=p.inicial(self.t);data['bloques'].insert(0,dict(id='b1',tipo='banner',activo=True,titulo='Título',texto='Copy editable',diapositivas=[dict(publicacion=pub.pk,tipo='foto',url=pub.imagenes[0])]))
        html=render_to_string('midistri_portal/pagina_bloques.html',{'bloques':p.bloques_vigentes(p.validar_pagina(data,20),20),'pagina':data,'distribuidora':self.d})
        from html.parser import HTMLParser
        class TextParser(HTMLParser):
            def __init__(self):super().__init__();self.active=False;self.copy=''
            def handle_starttag(self,tag,attrs):
                if tag=='p' and ('data-copy-editable',None) in attrs:self.active=True
            def handle_endtag(self,tag):
                if tag=='p':self.active=False
            def handle_data(self,d):
                if self.active:self.copy+=d
        parser=TextParser();parser.feed(html);self.assertEqual(parser.copy,'Copy editable')
        self.assertIn('Nombre protegido',html);self.assertIn('77',html)

    def test_encabezado_configurable_sin_linea_descriptiva_en_saludo(self):
        from django.template.loader import render_to_string
        from . import pagina as p
        data=p.inicial(self.t);data['mensajes']['encabezado']='Mi tienda de kioscos'
        clean=p.validar_pagina(data,20)
        self.assertEqual(clean['mensajes']['encabezado'],'Mi tienda de kioscos')
        html=render_to_string('midistri_portal/base.html',{'titulo':'Predeterminado','pagina_mensajes':clean['mensajes'],'perfil':{'nombre':'Cerrutti','lin':121,'vv':194,'linea':'1126 - Saavedra'},'cart_count':0})
        self.assertIn('Mi tienda de kioscos',html);self.assertNotIn('LIN 121',html);self.assertIn('VV 194',html);self.assertNotIn('1126 - Saavedra',html)

    def test_revision_comercial_valida_cantidades_sin_tocar_pedido_original(self):
        from .contract import pedido_valido
        from .client import ApiError
        base={'id':str(uuid4()),'vendedor_id':7,'distribuidora_id':20,'vendedor':'QA','estado':'recibido','items':[{'producto_id':1,'cantidad':3,'nombre':'Foto producto','codigo':'QA','precio':'10.00','pvp':'15.00'}],'revision_comercial':{'numero':1,'motivo':'Falta stock','cantidades':[{'producto_id':1,'cantidad_preparada':2}]}}
        perfil={'id':7,'distribuidora_id':20}
        result=pedido_valido(base,perfil);self.assertEqual(result['items'][0]['cantidad'],3);self.assertEqual(result['revision_comercial']['cantidades'][0]['cantidad_preparada'],2)
        base['revision_comercial']['cantidades'][0]['cantidad_preparada']=4
        with self.assertRaises(ApiError):pedido_valido(base,perfil)

    def test_subida_con_respuesta_perdida_no_duplica_diapositiva(self):
        from . import pagina as p
        from django.core.files.uploadedfile import SimpleUploadedFile
        session=self.client.session;session['midistri_operador_token']='x'*43;session.save()
        ident=str(uuid4());op=str(uuid4())
        with patch('midistri_portal.operadores.api',return_value=self.perfil),patch.object(p,'api',side_effect=self.remoto),patch('midistri_portal.pagina_views.subir_material_tienda',return_value={'id':ident,'tipo':'foto','url':'https://sistema7000.belnu.com.ar/midistri-media/'+ident+'/'}) as upload:
            page=p.borrador_tienda(self.perfil,20,'token');data=deepcopy(page.datos);data['bloques'].insert(0,{'id':'b','tipo':'banner','titulo':'Foto','activo':True,'diapositivas':[]})
            page=p.guardar_borrador(self.perfil,20,data,page.revision,str(uuid4()),'token')
            def post(content=b'photo'):
                return self.client.post('/portal/administrar/pagina/subir/?distribuidora=20',{'accion':'archivo','revision':page.revision,'operacion':op,'bloque':'b','archivo':SimpleUploadedFile('qa.png',content,content_type='image/png')})
            first=post();self.assertEqual(first.status_code,200)
            again=post();self.assertEqual(again.status_code,200)
            self.assertEqual(again.json()['revision'],first.json()['revision']);self.assertEqual(len(again.json()['datos']['bloques'][0]['diapositivas']),1)
            self.assertEqual(upload.call_count,1)
            self.assertEqual(post(b'different').status_code,400)
