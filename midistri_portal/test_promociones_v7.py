from importlib.util import find_spec
from uuid import uuid4
from unittest.mock import patch
from django.test import TestCase,override_settings
from django.core.exceptions import ValidationError
from .models import Distribuidora,Tienda
from .test_operadores import PROFILE

@override_settings(MIDISTRI_ADMIN_ENABLED=True,MIDISTRI_MULTIMEDIA_ENABLED=True)
class PromocionesTests(TestCase):
    def setUp(self):
        self.assertIsNotNone(find_spec('midistri_portal.promociones'))
        from . import promociones
        self.s=promociones;self.profile=dict(PROFILE,permisos=['midistri.tienda_configurar'])
        self.d=Distribuidora.objects.create(pk=20,nombre='Belgrano')
        self.t=Tienda.objects.create(distribuidora=self.d)
        self.data=dict(titulo='Oferta <script>',texto='Consultá disponibilidad',enlace='https://example.com/oferta',
            tipo='texto',material_id='',url='',orden=0,activo=True)
    def guardar(self,data=None,**kw):
        with patch('midistri_portal.promociones.api') as api:
            api.side_effect=lambda action,**kwargs:self.profile if action=='operator-profile' else {'ok':True,'revision':kw.get('revision',0)+1}
            return self.s.guardar_promocion(self.profile,20,data or self.data,kw.get('revision',0),kw.get('operacion',str(uuid4())),'op'*22,bloque_id=kw.get('bloque'))
    def test_siete_temas_y_preferencia_por_tienda(self):
        from .presentacion import TiendaForm
        choices=dict(TiendaForm.base_fields['tema'].choices)
        self.assertEqual(set(choices),{'claro','nocturno','azul','verde','terracota','violeta_pastel','ambar_pastel'})
        self.assertEqual(self.t.tema,'claro')
    def test_maximo_diez_y_revision_obsoleta(self):
        a=self.guardar()
        self.assertRaises(ValidationError,self.guardar,bloque=str(a.pk),revision=0)
        for i in range(9):self.guardar()
        self.assertRaises(ValidationError,self.guardar)
    def test_reintento_y_archivo_conservan_historial(self):
        oid=str(uuid4());bid=str(uuid4());a=self.guardar(operacion=oid,bloque=bid)
        b=self.guardar(operacion=oid,bloque=bid);self.assertEqual(a.pk,b.pk)
        self.guardar(dict(self.data,activo=False),revision=1,bloque=bid)
        a.refresh_from_db();self.assertFalse(a.activo)
        from .models import CambioPromocional
        self.assertEqual(CambioPromocional.objects.count(),2)
    def test_markup_escapado_enlaces_sin_ssrf(self):
        a=self.guardar()
        response=self.client.get('/portal/?distribuidora=20')
        self.assertContains(response,'Oferta &lt;script&gt;')
        self.assertNotContains(response,'Oferta <script>')
        for url in ('javascript:alert(1)','http://example.com/','https://u:p@example.com/'):
            self.assertRaises(ValidationError,self.guardar,dict(self.data,enlace=url))
    def test_dist_ajena_permiso_revocado_rechaza(self):
        from .client import ApiError
        with patch('midistri_portal.promociones.api',return_value=dict(self.profile,permisos=['pedidos.gestionar'])):
            self.assertRaises(ApiError,self.s.guardar_promocion,self.profile,20,self.data,0,str(uuid4()),'x'*32)

    def test_material_producto_puede_archivarse_sin_reseleccion(self):
        from .models import Publicacion
        photo='https://sistema7000.belnu.com.ar/catalogo-imagenes/abbeddef-abcd-4444-aaaa-123456789012/'+'a'*64+'/'
        p=Publicacion.objects.create(distribuidora=self.d,producto_id=3,nombre='Producto',precio=10,pvp=15,
            multimedia=[dict(tipo='foto',url=photo,id='1',orden=0,principal=True)])
        a=self.guardar(dict(self.data,material_producto=str(p.pk)+':0'))
        p.activa=False;p.save()
        self.guardar(dict(self.data,tipo='foto',url=photo,material_id='',activo=False),bloque=str(a.pk),revision=1)
        a.refresh_from_db();self.assertFalse(a.activo)

    def test_operacion_durable_antes_de_llamar_y_reintento_tras_timeout(self):
        from .models import CambioPromocional,BloquePromocional
        from .client import ApiError
        oid=str(uuid4());bid=str(uuid4());calls=[]
        def remote(action,**kwargs):
            if action=='operator-profile':return self.profile
            calls.append(kwargs['data']['operacion'])
            self.assertTrue(CambioPromocional.objects.filter(pk=oid,estado='pendiente').exists())
            if len(calls)==1:raise ApiError('Respuesta incierta',503)
            return {'ok':True,'revision':1}
        with patch('midistri_portal.promociones.api',side_effect=remote):
            self.assertRaises(ApiError,self.s.guardar_promocion,self.profile,20,self.data,0,oid,'op'*22,bloque_id=bid)
            self.assertFalse(BloquePromocional.objects.get(pk=bid).activo)
            self.assertRaises(ValidationError,self.s.guardar_promocion,self.profile,20,self.data,0,str(uuid4()),'op'*22,bloque_id=bid)
            row=self.s.guardar_promocion(self.profile,20,self.data,0,oid,'op'*22,bloque_id=bid)
        self.assertTrue(row.activo)
        self.assertEqual(calls,[oid,oid])
        self.assertEqual(CambioPromocional.objects.get(pk=oid).estado,'confirmado')

    def test_retirar_producto_o_material_oculta_promocion(self):
        from .models import Publicacion
        url='https://www.youtube.com/watch?v=demo'
        product=Publicacion.objects.create(distribuidora=self.d,producto_id=7,nombre='Demo',precio=10,pvp=15,
            multimedia=[dict(tipo='youtube',url=url,id='x',orden=0,principal=False)])
        a=self.guardar(dict(self.data,material_producto=str(product.pk)+':0'))
        self.assertEqual([x.pk for x in self.s.promociones_publicas(self.d)],[a.pk])
        product.activa=False;product.save()
        self.assertFalse(self.s.promociones_publicas(self.d))
        product.activa=True;product.multimedia=[];product.save()
        self.assertFalse(self.s.promociones_publicas(self.d))

    def test_vista_previa_privada_no_guarda_ni_publica(self):
        from .models import BloquePromocional
        session=self.client.session;session['midistri_operador_token']='op'*22;session.save()
        with patch('midistri_portal.operadores.api',return_value=self.profile):
            r=self.client.post('/portal/administrar/promociones/',dict(self.data,distribuidora=20,accion='revisar',
                operacion=str(uuid4()),nuevo_bloque=str(uuid4()),revision='0'))
        self.assertContains(r,'Confirmar promoción revisada')
        self.assertContains(r,'name="accion" value="revisar"')
        self.assertContains(r,'Oferta &lt;script&gt;')
        self.assertFalse(BloquePromocional.objects.exists())

    def test_previa_firmada_no_admite_modificacion_y_confirma_una_vez(self):
        from .models import BloquePromocional
        session=self.client.session;session['midistri_operador_token']='op'*22;session.save()
        with patch('midistri_portal.operadores.api',return_value=self.profile):
            r=self.client.post('/portal/administrar/promociones/',dict(self.data,distribuidora=20,accion='revisar',
                operacion=str(uuid4()),nuevo_bloque=str(uuid4()),revision='0'))
            signed=r.context['firma_previa']
            with patch('midistri_portal.promociones.api') as remote:
                remote.side_effect=lambda action,**kwargs:self.profile if action=='operator-profile' else {'ok':True,'revision':1}
                for _ in range(2):
                    r=self.client.post('/portal/administrar/promociones/',dict(distribuidora=20,accion='confirmar',previa=signed,titulo='Inyectado'))
                    self.assertEqual(r.status_code,302)
        self.assertEqual(BloquePromocional.objects.count(),1)
        self.assertEqual(BloquePromocional.objects.get().titulo,self.data['titulo'])

    def test_transporte_previa_solo_acepta_archivo_y_operacion_fijos(self):
        from unittest.mock import MagicMock
        from .client import api,ApiError
        raw=b'\x89PNG\r\n\x1a\nsynthetic'
        response=MagicMock();response.status_code=200;response.headers={'Content-Type':'image/png'}
        response.iter_content.return_value=[raw]
        with patch('midistri_portal.client.requests.request') as request:
            request.return_value.__enter__.return_value=response
            self.assertEqual(api('operator-promotion-preview',binary_media=True),(raw,'image/png'))
            self.assertRaises(ApiError,api,'profile',binary_media=True)
