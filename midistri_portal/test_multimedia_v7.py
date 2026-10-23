from importlib.util import find_spec
from copy import deepcopy
from django.test import TestCase,override_settings
from . import test_display_cero as fixture
from .models import Publicacion
from .services import aplicar_snapshot

BASE='https://sistema7000.belnu.com.ar'
PHOTO=BASE+'/catalogo-imagenes/abbeddef-abcd-4444-aaaa-123456789012/'+'a'*64+'/'
VIDEO=BASE+'/midistri-media/abbeddef-abcd-4444-aaaa-123456789012/'

@override_settings(URBAN_API_BASE=BASE+'/midistri/api/',MIDISTRI_MULTIMEDIA_ENABLED=True)
class MultimediaContractTests(TestCase):
    def setUp(self):
        self.assertIsNotNone(find_spec('midistri_portal.multimedia_contract'))
        from .multimedia_contract import validar_multimedia
        self.validar=validar_multimedia

    def item(self,tipo='foto',url=PHOTO,**kwargs):
        result=dict(id='abbeddef-abcd-4444-aaaa-123456789012',tipo=tipo,url=url,descripcion='Producto',orden=0,principal=True)
        result.update(kwargs);return result

    def test_snapshot_legacy_fotos_funciona(self):
        aplicar_snapshot(fixture.DisplayCeroTests.datos(self))
        self.assertEqual(Publicacion.objects.first().multimedia,[])

    def test_multimedia_tipada_limites_y_deduplicacion(self):
        item=self.item();self.assertEqual(self.validar([item,item],BASE),[item])
        self.assertRaises(ValueError,self.validar,[self.item(id=str(i)) for i in range(31)],BASE)
        self.assertRaises(ValueError,self.validar,[self.item(orden=True)],BASE)
        self.assertRaises(ValueError,self.validar,[self.item(principal=1)],BASE)
        self.assertEqual(self.validar([self.item(tipo='mp4',url=VIDEO,principal=False)],BASE)[0]['tipo'],'mp4')

    def test_url_privada_host_ajeno_redirect_y_javascript_rechaza(self):
        for url in ('/media/privado.mp4','javascript:alert(1)','https://evil.test/midistri-media/a/',
            VIDEO+'?next=https://evil.test',VIDEO+'#x','https://u:p@sistema7000.belnu.com.ar/midistri-media/a/',
            VIDEO.replace('.ar/','.ar:8443/'),BASE+'/productos/1/videos/2/',BASE+'/midistri-media/../privado'):
            with self.subTest(url=url):self.assertRaises(ValueError,self.validar,[self.item(tipo='mp4',url=url)],BASE)

    def test_snapshot_invalido_no_vacia_catalogo(self):
        data=fixture.DisplayCeroTests.datos(self);aplicar_snapshot(data)
        original=list(Publicacion.objects.values_list('pk','activa','nombre'))
        data['publicaciones'][0]['multimedia']=[self.item(tipo='mp4',url='https://evil.test/a.mp4')]
        self.assertRaises(ValueError,aplicar_snapshot,data)
        self.assertEqual(original,list(Publicacion.objects.values_list('pk','activa','nombre')))
