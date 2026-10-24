from io import BytesIO
import importlib.util
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase,override_settings
from django.core.exceptions import ValidationError
from PIL import Image
from .test_operadores import PROFILE
from .client import ApiError
from .models import Distribuidora

@override_settings(MIDISTRI_ADMIN_ENABLED=True)
class PresentacionTests(TestCase):
    def setUp(self):
        self.d=Distribuidora.objects.create(id=20,nombre='20 - Belgrano')
        self.perfil=dict(PROFILE,permisos=['midistri.tienda_configurar'])
    def modulo(self):
        self.assertIsNotNone(importlib.util.find_spec('midistri_portal.presentacion'),'Falta presentación de tienda')
        from . import presentacion
        return presentacion
    def test_logo_valido_recodificado_y_corrupto_rechazado(self):
        m=self.modulo();out=BytesIO();Image.new('RGB',(80,80),'red').save(out,format='JPEG')
        f=m.validar_logo(SimpleUploadedFile('../../logo.jpg',out.getvalue()))
        self.assertTrue(f.name.endswith('.png'));self.assertNotIn('..',f.name)
        self.assertTrue(f.read().startswith(b'\x89PNG'))
        for raw in (b'<svg></svg>',b'bad',b'x'*(2*1024*1024+1)):
            with self.assertRaises(ValidationError):m.validar_logo(SimpleUploadedFile('logo.png',raw))
    def test_revision_y_autorizacion_fresca(self):
        m=self.modulo()
        with patch('midistri_portal.presentacion.api',return_value=self.perfil):
            t=m.guardar_tienda(self.perfil,20,{'email':'contacto@example.test','telefono':'123','bienvenida':'Hola','instrucciones':'Pedir'},
                revision=0,operacion_id='00000000-0000-4000-8000-000000000001',token='x'*43)
            self.assertEqual(t.revision,1)
            with self.assertRaises(ValidationError):
                m.guardar_tienda(self.perfil,20,{},revision=0,operacion_id='00000000-0000-4000-8000-000000000002',token='x'*43)
        with patch('midistri_portal.presentacion.api',side_effect=ApiError('Sin red')):
            with self.assertRaises(ApiError):m.guardar_tienda(self.perfil,20,{},revision=1,
                operacion_id='00000000-0000-4000-8000-000000000003',token='x'*43)
    def test_evidencia_fallida_no_repite_guardado(self):
        m=self.modulo()
        def remoto(action,**kwargs):
            if action=='operator-profile':return self.perfil
            raise ApiError('Sin respuesta')
        data={'email':'','telefono':'','bienvenida':'<script>peligro()</script>','instrucciones':''}
        with patch('midistri_portal.presentacion.api',side_effect=remoto):
            t=m.guardar_tienda(self.perfil,20,data,revision=0,operacion_id='00000000-0000-4000-8000-000000000004',token='x'*43)
            self.assertEqual(t.revision,1)
            again=m.guardar_tienda(self.perfil,20,data,revision=0,operacion_id='00000000-0000-4000-8000-000000000004',token='x'*43)
            self.assertEqual(again.revision,1)
        self.assertFalse(t.cambios.first().confirmado_urban)
        r=self.client.get('/portal/?distribuidora=20')
        self.assertContains(r,'&lt;script&gt;');self.assertNotContains(r,'<script>peligro()')

    def test_mismo_uuid_con_otro_contenido_no_finge_guardado(self):
        m=self.modulo();ident='00000000-0000-4000-8000-000000000005'
        with patch('midistri_portal.presentacion.api',return_value=self.perfil):
            m.guardar_tienda(self.perfil,20,{'bienvenida':'Primera'},revision=0,operacion_id=ident,token='x'*43)
            with self.assertRaises(ValidationError):
                m.guardar_tienda(self.perfil,20,{'bienvenida':'Diferente'},revision=0,operacion_id=ident,token='x'*43)

    def test_pantalla_antigua_no_publica_archivo_sin_revision(self):
        from .models import Tienda
        session=self.client.session;session['midistri_operador_token']='x'*43;session.save()
        with patch('midistri_portal.operadores.api',return_value=self.perfil):
            response=self.client.post('/portal/administrar/tienda/',{'distribuidora':20,'bienvenida':'No publicar'})
        self.assertEqual(response.status_code,302)
        self.assertIn('/administrar/pagina/',response['Location'])
        self.assertFalse(Tienda.objects.exists())
