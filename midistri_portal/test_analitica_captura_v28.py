from importlib import import_module,util
from types import SimpleNamespace
from uuid import uuid4
from datetime import timedelta
from unittest.mock import patch
from django.test import TestCase,RequestFactory
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Distribuidora,Publicacion

class CapturaAnaliticaTests(TestCase):
    def setUp(self):
        self.d=Distribuidora.objects.create(pk=20,nombre='Tienda')
        self.p=Publicacion.objects.create(distribuidora=self.d,producto_id=11,nombre='Conito',codigo='CON-11',precio=1000,pvp=1200,
            imagenes=['https://example.test/f.jpg'],multimedia=[{'tipo':'foto','url':'https://example.test/f.jpg'},{'tipo':'mp4','url':'https://example.test/v.mp4'}])
        self.perfil={'id':7,'nombre':'Vendedor','distribuidora_id':20,'distribuidora':'Tienda'}
        self.r=RequestFactory().get('/portal/');self.r.session={'midistri_token':'x'*43};self.r.midistri_tab=SimpleNamespace(pk=uuid4());self.r.midistri_perfil=self.perfil
    def servicio(self):
        self.assertIsNotNone(util.find_spec('midistri_portal.analitica_captura'),'Falta captura analítica')
        return import_module('midistri_portal.analitica_captura')
    def test_captura_inicialmente_apagada_y_cobertura_real(self):
        s=self.servicio();self.assertIsNone(s.registrar(self.r,self.perfil,'catalogo'))
        self.assertEqual(s.EventoAnalitico.objects.count(),0)
        s.cambiar_estado(True);s.registrar(self.r,self.perfil,'catalogo')
        self.assertEqual(s.EventoAnalitico.objects.count(),1);self.assertEqual(s.IntervaloAnalitico.objects.filter(hasta__isnull=True).count(),1)
        s.cambiar_estado(False);self.assertFalse(s.IntervaloAnalitico.objects.filter(hasta__isnull=True).exists())
        self.assertEqual(s.EventoAnalitico.objects.count(),1)
    def test_dedup_y_payload_distinto_no_sobrescribe(self):
        s=self.servicio();s.cambiar_estado(True);ident=str(uuid4())
        event={'id':ident,'tipo':'foto_ampliada','producto':11,'recurso':0}
        s.recibir_lote(self.r,self.perfil,[event]);s.recibir_lote(self.r,self.perfil,[event])
        self.assertEqual(s.EventoAnalitico.objects.count(),1)
        with self.assertRaises(ValidationError):s.recibir_lote(self.r,self.perfil,[dict(event,tipo='producto_consulta')])
    def test_visita_30min_no_cierra_sesion_y_pestanas_separadas(self):
        s=self.servicio();s.cambiar_estado(True);t=timezone.now()
        with patch('midistri_portal.analitica_captura.timezone.now',return_value=t):a=s.registrar(self.r,self.perfil,'catalogo')
        with patch('midistri_portal.analitica_captura.timezone.now',return_value=t+timedelta(minutes=31)):b=s.registrar(self.r,self.perfil,'catalogo')
        self.assertNotEqual(a.visita,b.visita);self.assertEqual(self.r.session['midistri_token'],'x'*43)
        self.r.midistri_tab=SimpleNamespace(pk=uuid4());c=s.registrar(self.r,self.perfil,'catalogo');self.assertNotEqual(b.visita,c.visita)
    def test_actor_recurso_y_tipo_cliente_invalidos(self):
        s=self.servicio();s.cambiar_estado(True)
        for event in [dict(id=str(uuid4()),tipo='ingreso'),dict(id=str(uuid4()),tipo='foto_ampliada',producto=999,recurso=0),dict(id=str(uuid4()),tipo='foto_ampliada',producto=11,recurso=1),dict(id=str(uuid4()),tipo='catalogo',vendedor_id=123)]:
            with self.subTest(event=event),self.assertRaises(ValidationError):s.recibir_lote(self.r,self.perfil,[event])
        self.assertEqual(s.EventoAnalitico.objects.count(),0)
    def test_anonimo_admin_y_fallo_no_rompen_negocio(self):
        s=self.servicio();s.cambiar_estado(True)
        self.assertIsNone(s.registrar(self.r,None,'catalogo'))
        self.r.path='/portal/administrar/pagina/';self.assertIsNone(s.registrar(self.r,self.perfil,'catalogo'))
        self.r.path='/portal/'
        with patch('midistri_portal.analitica_captura._registrar',side_effect=RuntimeError('db offline')):
            self.assertIsNone(s.registrar(self.r,self.perfil,'catalogo'))
        self.assertEqual(self.r.session['midistri_token'],'x'*43)
    def test_lote_excesivo_y_orden_de_campos_no_duplican(self):
        s=self.servicio();s.cambiar_estado(True)
        with self.assertRaises(ValidationError):s.recibir_lote(self.r,self.perfil,[dict(id=str(uuid4()),tipo='producto_consulta',producto=11)]*21)
        row=dict(id=str(uuid4()),tipo='producto_consulta',producto=11)
        s.recibir_lote(self.r,self.perfil,[row]);s.recibir_lote(self.r,self.perfil,[dict(reversed(list(row.items())))])
        self.assertEqual(s.EventoAnalitico.objects.count(),1)

    def test_reactivar_conserva_intervalos_y_nueva_tienda(self):
        s=self.servicio();s.cambiar_estado(True);s.cambiar_estado(True)
        self.assertEqual(s.IntervaloAnalitico.objects.count(),1)
        s.cambiar_estado(False);s.cambiar_estado(True)
        self.assertEqual(s.IntervaloAnalitico.objects.count(),2)
        d=Distribuidora.objects.create(pk=21,nombre='Futura');p=dict(self.perfil,distribuidora_id=21)
        self.r.midistri_perfil=p;s.registrar(self.r,p,'catalogo')
        self.assertTrue(s.IntervaloAnalitico.objects.filter(distribuidora=d,hasta__isnull=True).exists())
    def test_error_de_lote_revierte_todos_sus_eventos(self):
        s=self.servicio();s.cambiar_estado(True)
        good=dict(id=str(uuid4()),tipo='producto_consulta',producto=11)
        bad=dict(id=str(uuid4()),tipo='foto_ampliada',producto=11,recurso=99)
        with self.assertRaises(ValidationError):s.recibir_lote(self.r,self.perfil,[good,bad])
        self.assertFalse(s.EventoAnalitico.objects.exists())

    def test_fallo_total_de_base_conserva_marca_privada_hasta_conciliar(self):
        from tempfile import TemporaryDirectory
        from django.test import override_settings
        from django.db import DatabaseError,transaction
        from .analitica_cobertura import marcar_fallo,marcador,congelar,conciliar_fallo
        with TemporaryDirectory() as folder,override_settings(BASE_DIR=folder):
            with patch('midistri_portal.analitica_cobertura.IncidenciaAnalitica.objects.create',side_effect=DatabaseError('offline')):marcar_fallo(20)
            self.assertTrue(marcador().exists())
            data=congelar([20],timezone.now());self.assertEqual(data['incidencias'][0]['distribuidora_id'],20)
            self.assertNotIn('vendedor',marcador().read_text())
            with self.captureOnCommitCallbacks(execute=True):
                with transaction.atomic():conciliar_fallo()
            self.assertFalse(marcador().exists())
            self.assertTrue(self.servicio().EventoAnalitico.objects.count()==0)
