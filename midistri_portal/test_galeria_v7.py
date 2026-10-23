from django.test import TestCase,override_settings
from .models import Distribuidora,Publicacion
from .test_multimedia_v7 import PHOTO,VIDEO

@override_settings(MIDISTRI_ENABLED=True,MIDISTRI_MULTIMEDIA_ENABLED=True)
class GaleriaTests(TestCase):
    def setUp(self):
        self.d=Distribuidora.objects.create(pk=20,nombre='Belgrano')
        self.p=Publicacion.objects.create(producto_id=314,distribuidora=self.d,nombre='Producto </script><script>alert(1)</script>',
            precio='25000',pvp='30000',imagenes=[PHOTO],multimedia=[
            dict(id='1',tipo='foto',url=PHOTO,descripcion='Principal',principal=True,orden=0),
            dict(id='2',tipo='mp4',url=VIDEO,descripcion='Video',principal=False,orden=1)])

    def test_card_tiene_galeria_y_precios_correctos(self):
        response=self.client.get('/portal/?distribuidora=20')
        self.assertContains(response,'data-galeria="314"')
        self.assertContains(response,'Precio vendedor:')
        self.assertContains(response,'PVP:')
        self.assertEqual(response.context['productos'][0].precio,25000)
        self.assertEqual(response.context['productos'][0].pvp,30000)

    def test_json_script_escapa_titulos(self):
        response=self.client.get('/portal/?distribuidora=20')
        self.assertContains(response,'application/json')
        self.assertContains(response,r'\u003C/script\u003E')
        self.assertNotContains(response,'<script>alert(1)</script>')

    def test_sin_js_muestra_material_publico(self):
        response=self.client.get('/portal/?distribuidora=20')
        self.assertContains(response,'Ver todas las fotos y videos')
        self.assertContains(response,VIDEO)
        self.assertContains(response,'controls')
        self.assertNotContains(response,'autoplay')

    @override_settings(MIDISTRI_MULTIMEDIA_ENABLED=False)
    def test_flag_apagada_conserva_foto_legacy(self):
        response=self.client.get('/portal/?distribuidora=20')
        self.assertContains(response,PHOTO)
        self.assertNotContains(response,'data-galeria="314"')
