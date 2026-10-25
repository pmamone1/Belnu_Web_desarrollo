from copy import deepcopy
from uuid import uuid4
from unittest.mock import patch
from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError
from . import tests_pagina_v11 as fixture

@override_settings(MIDISTRI_ADMIN_ENABLED=True,MIDISTRI_MULTIMEDIA_ENABLED=True)
class CabezalTests(TestCase):
    setUp=fixture.PaginaTests.setUp
    remoto=fixture.PaginaTests.remoto
    def test_logo_y_nombre_en_cabezal_sin_duplicar_bienvenida(self):
        from . import pagina as p
        from .editor_views import html_pagina
        data=p.inicial(self.t);data['mensajes']['encabezado']='Mi kiosco & tienda';data['presentacion']['logo']='https://example.test/logo.png'
        html=html_pagina(data,self.d)
        header=html.partition('<header')[2].partition('</header>')[0]
        self.assertIn('Mi kiosco &amp; tienda',header)
        self.assertIn('https://example.test/logo.png',header)
        self.assertEqual(html.count('src="https://example.test/logo.png"'),1)
    def test_logo_privado_en_preview_y_etiquetas_escapadas_con_rutas_protegidas(self):
        from . import pagina as p
        from .editor_views import html_pagina
        data=p.inicial(self.t);data['presentacion']['logo']='https://sistema7000.belnu.com.ar/midistri-media/'+str(uuid4())+'/'
        data['mensajes'].update(nav_catalogo='Productos <QA>',nav_distribuidor='Mi gestión')
        clean=p.validar_pagina(data,20);html=html_pagina(clean,self.d)
        header=html.partition('<header')[2].partition('</header>')[0]
        self.assertIn('/portal/administrar/promociones/material/20/',header)
        self.assertIn('Productos &lt;QA&gt;',header);self.assertIn('Mi gestión',header)
        self.assertIn('/portal/administrar/entrada/?destino=tienda',header)
    def test_etiquetas_se_guardan_publican_y_borradores_previos_tienen_defaults(self):
        from . import pagina as p
        from .editor_views import html_pagina
        with patch.object(p,'api',side_effect=self.remoto):
            draft=p.borrador_tienda(self.perfil,20,'token');data=deepcopy(draft.datos)
            data['mensajes'].update(nav_catalogo='Ver productos',nav_distribuidor='Administrar mi tienda')
            draft=p.guardar_borrador(self.perfil,20,data,draft.revision,str(uuid4()),'token')
            signature=p.revisar_borrador(self.perfil,20,'token');p.publicar_revision(self.perfil,20,signature,'token')
        self.assertEqual(p.pagina_publica(self.d)['mensajes'].get('nav_catalogo'),'Ver productos')
        for key in ('nav_catalogo','nav_distribuidor'):data['mensajes'].pop(key,None)
        old=p.validar_pagina(data,20);html=html_pagina(old,self.d)
        self.assertIn('>Catálogo</a>',html);self.assertIn('>Acceso Distribuidor</a>',html)
        data['mensajes']['nav_catalogo']='x'*81
        with self.assertRaises(ValidationError):p.validar_pagina(data,20)
    def test_editor_ofrece_cabezal_logo_y_progreso_publicacion(self):
        from . import pagina as p
        session=self.client.session;session['midistri_operador_token']='x'*43;session.save()
        with patch('midistri_portal.operadores.api',return_value=self.perfil),patch.object(p,'api',side_effect=self.remoto):
            response=self.client.get('/portal/administrar/pagina/?distribuidora=20')
        self.assertContains(response,'Encabezado y logo')
        self.assertContains(response,'data-encabezado="nav_catalogo"')
        self.assertContains(response,'id="editor-logo-archivo"')
        self.assertContains(response,'id="editor-progreso"')

    def test_marcas_comercio_y_favicon_independientes_por_tienda(self):
        from . import pagina as p
        from .editor_views import html_pagina
        for marca in ('bolsa','carrito','tienda','paquete','ofertas','kiosco','camion','furgon','logistica'):
            data=p.inicial(self.t);data['presentacion'].update(marca=marca,favicon_marca='ofertas')
            clean=p.validar_pagina(data,20);html=html_pagina(clean,self.d)
            header=html.partition('<header')[2].partition('</header>')[0]
            self.assertIn('/marcas/'+marca+'.svg',header)
            self.assertIn('rel="icon"',html);self.assertIn('/marcas/ofertas.svg',html.partition('</head>')[0])
        data['presentacion']['marca']='../../otro'
        with self.assertRaises(ValidationError):p.validar_pagina(data,20)
    def test_logo_propio_es_favicon_por_defecto_y_quitarlo_vuelve_al_preset(self):
        from . import pagina as p
        from .editor_views import html_pagina
        data=p.inicial(self.t);data['presentacion'].update(logo='https://example.test/propio.png',marca='carrito',favicon_marca='')
        html=html_pagina(p.validar_pagina(data,20),self.d)
        self.assertIn('href="https://example.test/propio.png"',html.partition('</head>')[0])
        data['presentacion']['logo']='';html=html_pagina(p.validar_pagina(data,20),self.d)
        self.assertIn('/marcas/carrito.svg',html.partition('<header')[2].partition('</header>')[0])
