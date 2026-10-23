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
