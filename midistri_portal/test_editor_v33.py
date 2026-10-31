from copy import deepcopy
from unittest.mock import patch
from uuid import uuid4
from django.test import TestCase, SimpleTestCase, override_settings
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from . import pagina as p
from . import tests_pagina_v11 as fixture
from .models import Publicacion

class EstilosMensajeTests(SimpleTestCase):
    def test_independientes_y_css_seguro(self):
        from .mensaje_estilos import validar_mensajes, css_mensaje
        data={'titulo':{'tamano':36,'fuente':'georgia','color':'#112233','fondo':'#ffffff'},'subtitulo':{'tamano':16,'fuente':'arial','color':'#334455','fondo':'#ffeecc'}}
        clean=validar_mensajes(data)
        self.assertEqual(clean['titulo']['tamano'],36)
        self.assertIn('font-size:16px',css_mensaje(clean,'subtitulo'))
        self.assertEqual(css_mensaje(clean,'carrito'),'')
        for bad in ({'titulo':{'color':'red;position:fixed'}},{'titulo':{'tamano':True}},{'titulo':{'fuente':'url(https://evil)'}},{'otro':{}},{'titulo':{'css':'display:none'}}):
            with self.subTest(bad=bad), self.assertRaises(ValidationError):validar_mensajes(bad)
    def test_publico_sin_boton_administrativo(self):
        html=render_to_string('midistri_portal/base.html',{'pagina_mensajes':{'nav_distribuidor':'Acceso Distribuidor'}})
        self.assertNotIn('Acceso Distribuidor',html)

@override_settings(MIDISTRI_ADMIN_ENABLED=True,MIDISTRI_MULTIMEDIA_ENABLED=True)
class BorradorRecuperableTests(TestCase):
    setUp=fixture.PaginaTests.setUp
    remoto=fixture.PaginaTests.remoto
    def test_estilos_opcionales_no_cambian_contrato_antiguo(self):
        old=p.validar_pagina(p.inicial(self.t),20)
        self.assertNotIn('estilos_mensajes',old)
        self.assertEqual(p.huella(old),p.huella(p.validar_pagina(old,20)))
        data=deepcopy(old);data['estilos_mensajes']={'titulo':{'tamano':34}}
        self.assertEqual(p.validar_pagina(data,20)['estilos_mensajes']['titulo']['tamano'],34)
    def test_retirado_no_bloquea_borrador_pero_si_publicacion(self):
        session=self.client.session;session['midistri_operador_token']='x'*43;session.save()
        pub=Publicacion.objects.create(producto_id=7,distribuidora=self.d,nombre='Retirado',activa=False,precio=10,pvp=20,imagenes=['https://example.test/p.jpg'])
        with patch('midistri_portal.operadores.api',return_value=self.perfil),patch.object(p,'api',side_effect=self.remoto):
            draft=p.borrador_tienda(self.perfil,20,'token');data=deepcopy(draft.datos)
            data['bloques'].insert(0,dict(id='roto',tipo='banner',titulo='Promo anterior',activo=True,diapositivas=[dict(publicacion=pub.pk,tipo='foto',url=pub.imagenes[0])]))
            response=self.client.post('/portal/administrar/pagina/dinamica/?distribuidora=20',{'accion':'guardar','revision':draft.revision,'operacion':str(uuid4()),'datos':data},content_type='application/json')
            self.assertEqual(response.status_code,200,response.content)
            self.assertEqual(response.json()['advertencias'][0]['bloque'],'roto')
            self.assertIn('Promo anterior',response.json()['advertencias'][0]['texto'])
            with self.assertRaises(ValidationError):p.revisar_borrador(self.perfil,20,'token')
            # Removing a promotion keeps the protected catalog, and does not publish.
            data=response.json()['datos'];data['bloques']=[b for b in data['bloques'] if b['id']!='roto']
            saved=p.guardar_borrador(self.perfil,20,data,response.json()['revision'],str(uuid4()),'token')
            self.assertFalse(any(b['id']=='roto' for b in saved.datos['bloques']))
            self.assertEqual(saved.publicada.revision,0)

    def test_publicar_y_renderizar_estilos_por_mensaje_escapando_texto(self):
        from .editor_views import html_pagina
        with patch.object(p,'api',side_effect=self.remoto):
            draft=p.borrador_tienda(self.perfil,20,'token');data=deepcopy(draft.datos)
            data['mensajes']['titulo']='Tienda <segura>'
            data['estilos_mensajes']={'titulo':{'tamano':40,'fuente':'georgia','color':'#123456','fondo':'#ffff00'},'subtitulo':{'tamano':16}}
            page=p.guardar_borrador(self.perfil,20,data,draft.revision,str(uuid4()),'token')
            firma=p.revisar_borrador(self.perfil,20,'token');p.publicar_revision(self.perfil,20,firma,'token')
        public=p.pagina_publica(self.d);self.assertEqual(public['estilos_mensajes'],data['estilos_mensajes'])
        html=html_pagina(public,self.d);self.assertIn('font-size:40px',html);self.assertIn('font-size:16px',html);self.assertIn('Tienda &lt;segura&gt;',html)

    def test_servidor_impide_eliminar_u_ocultar_contacto_existente(self):
        with patch.object(p,'api',side_effect=self.remoto):
            page=p.borrador_tienda(self.perfil,20,'token')
            for action in ('eliminar','ocultar'):
                data=deepcopy(page.datos)
                if action=='eliminar':data['bloques']=[b for b in data['bloques'] if b['tipo']!='contacto']
                else:next(b for b in data['bloques'] if b['tipo']=='contacto')['activo']=False
                with self.subTest(action=action),self.assertRaises(ValidationError):p.guardar_borrador(self.perfil,20,data,page.revision,str(uuid4()),'token')
            page.refresh_from_db();self.assertEqual(page.revision,0)
    def test_formulario_clasico_no_muestra_campo_de_acceso_distribuidor(self):
        from .pagina_forms import PaginaForm
        html=PaginaForm().as_p()
        self.assertNotIn('Texto del botón Acceso Distribuidor',html)
