from django.test import TestCase,override_settings
from . import test_display_cero as fixture
from .models import Publicacion
from .services import aplicar_snapshot,validar_snapshot

@override_settings(URBAN_API_BASE='https://sistema7000.belnu.com.ar/midistri/api/',MIDISTRI_ENABLED=True,MIDISTRI_MULTIMEDIA_ENABLED=True)
class DescripcionTests(TestCase):
    def test_snapshot_con_descripcion(self):
        data=fixture.DisplayCeroTests.datos(self)
        data['publicaciones'][0]['descripcion']='Reseña del producto'
        ds,rows=validar_snapshot(data)
        self.assertEqual(rows[0][2].get('descripcion'),'Reseña del producto')

    def test_snapshot_legacy_y_rechazo_atomico_de_texto_invalido(self):
        from copy import deepcopy
        data=fixture.DisplayCeroTests.datos(self)
        aplicar_snapshot(data);self.assertEqual(Publicacion.objects.first().descripcion,'')
        data['publicaciones'][0]['descripcion']='Reseña conservada';original=deepcopy(data);aplicar_snapshot(data)
        self.assertEqual(data,original)
        before=list(Publicacion.objects.values())
        for invalid in [None,{},123,'x'*2001,'texto'+chr(0)]:
            broken=deepcopy(data);broken['publicaciones'][1]['descripcion']=invalid
            with self.assertRaises(ValueError):aplicar_snapshot(broken)
            self.assertEqual(before,list(Publicacion.objects.values()))
    def test_galeria_y_fallback_escapan_resena(self):
        import json
        from .test_multimedia_v7 import PHOTO
        from .models import Distribuidora
        d=Distribuidora.objects.create(pk=20,nombre='Tienda de prueba')
        malicious='Reseña </script><script>alert(1)</script>\nDescripción del producto'
        p=Publicacion.objects.create(producto_id=314,distribuidora=d,nombre='Producto de prueba',descripcion=malicious,precio=100,pvp=150,imagenes=[PHOTO],multimedia=[{'tipo':'foto','url':PHOTO,'descripcion':'Foto'}])
        response=self.client.get('/portal/?distribuidora=20')
        self.assertEqual(response.status_code,200)
        dto=response.context['productos'][0].galeria_datos
        self.assertEqual(dto['descripcion'],malicious)
        self.assertContains(response,r'\u003C/script\u003E')
        self.assertNotContains(response,'<script>alert(1)</script>')
        self.assertContains(response,'galeria-resena-alternativa')
        self.assertEqual(dto['items'][0]['descripcion'],'Foto')
    def test_borrado_se_refleja_sin_saldo_ni_pedido(self):
        from .models import PedidoLocal
        data=fixture.DisplayCeroTests.datos(self);data['publicaciones'][0]['descripcion']='Texto anterior';aplicar_snapshot(data)
        data['publicaciones'][0]['descripcion']='';aplicar_snapshot(data)
        self.assertEqual(Publicacion.objects.first().descripcion,'');self.assertFalse(PedidoLocal.objects.exists())

    def test_transporte_snapshot_grande_y_resto_conserva_limite(self):
        import json
        from unittest.mock import patch
        from .client import api,ApiError
        raw=json.dumps({'publicaciones':[{'descripcion':'x'*2000} for _ in range(8500)]},ensure_ascii=False).encode('utf-8')
        self.assertGreater(len(raw),16*1024*1024)
        class Response:
            status_code=200
            headers={'Content-Type':'application/json'}
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def iter_content(self,n):
                for i in range(0,len(raw),n):yield raw[i:i+n]
        with patch('midistri_portal.client.requests.request',return_value=Response()):
            result=api('snapshot');self.assertEqual(len(result['publicaciones']),8500)
            with self.assertRaises(ApiError):api('perfil')
            with patch('midistri_portal.client.MAX_SNAPSHOT_BYTES',1024):
                with self.assertRaises(ApiError):api('snapshot')
