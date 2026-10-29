import json
from uuid import uuid4
from unittest.mock import patch
from django.test import TestCase,Client,override_settings
from . import test_codigo_v7 as fixture
from .models import Publicacion,SesionVendedorPortal,PedidoLocal
from .analitica_captura import cambiar_estado,EventoAnalitico

@override_settings(MIDISTRI_LOGIN_CODIGO_ENABLED=True,MIDISTRI_MULTIMEDIA_ENABLED=True)
class IntegracionAnaliticaTests(TestCase):
    setUp=fixture.CodigoPortalTests.setUp
    response=fixture.CodigoPortalTests.response
    login=fixture.CodigoPortalTests.login
    def preparar(self):
        cambiar_estado(True)
        Publicacion.objects.update(multimedia=[{'tipo':'foto','url':'https://example.test/f.jpg'}])
        self.login()
    def test_ingreso_y_catalogo_solo_perfil_validado(self):
        self.preparar();self.assertEqual(EventoAnalitico.objects.filter(tipo='ingreso').count(),1)
        with patch('midistri_portal.views.api',return_value=self.profile):r=self.client.get('/portal/',**self.headers)
        self.assertContains(r,'analitica-contexto');self.assertEqual(EventoAnalitico.objects.filter(tipo='catalogo').count(),1)
        self.assertNotContains(r,'SECRET_URBAN_TOKEN')
    def test_lote_firmado_usa_actor_real_sin_llamar_api_por_foto(self):
        self.preparar()
        with patch('midistri_portal.views.api',return_value=self.profile):r=self.client.get('/portal/',**self.headers)
        firma=r.context['analitica_contexto']['firma']
        payload={'firma':firma,'eventos':[{'id':str(uuid4()),'tipo':'foto_ampliada','producto':1,'recurso':0}]}
        with patch('midistri_portal.views.api') as api:
            response=self.client.post('/portal/actividad/eventos/',json.dumps(payload),content_type='application/json',**self.headers)
        self.assertEqual(response.status_code,200);api.assert_not_called()
        event=EventoAnalitico.objects.get(tipo='foto_ampliada');self.assertEqual(event.vendedor_id,7);self.assertEqual(event.distribuidora_id,20)
        bad=dict(payload,vendedor_id=999)
        self.assertEqual(self.client.post('/portal/actividad/eventos/',json.dumps(bad),content_type='application/json',**self.headers).status_code,400)
    def test_csrf_y_firma_invalida_no_graban(self):
        self.preparar();n=EventoAnalitico.objects.count()
        payload={'firma':'manipulada','eventos':[{'id':str(uuid4()),'tipo':'foto_ampliada','producto':1,'recurso':0}]}
        self.assertEqual(self.client.post('/portal/actividad/eventos/',json.dumps(payload),content_type='application/json',**self.headers).status_code,403)
        c=Client(enforce_csrf_checks=True);c.cookies=self.client.cookies
        self.assertEqual(c.post('/portal/actividad/eventos/',json.dumps(payload),content_type='application/json',**self.headers).status_code,403)
        self.assertEqual(EventoAnalitico.objects.count(),n)
    def test_carrito_valido_pedido_aceptado_y_reintento_unico(self):
        self.preparar()
        def api(action,**kw):
            if action=='profile':return self.profile
            if action=='orders':return {'id':kw['data']['id'],'vendedor_id':7,'distribuidora_id':20,'vendedor':self.profile['nombre'],'estado':'recibido','items':kw['data']['items']}
            raise AssertionError(action)
        with patch('midistri_portal.views.api',side_effect=api):
            self.client.post('/portal/cantidad/',{'producto':1,'cantidad':2},**self.headers)
            self.client.get('/portal/carrito/',**self.headers)
            revision=SesionVendedorPortal.objects.get(pk=self.tab).datos['midistri_revision']
            self.assertEqual(self.client.post('/portal/enviar/',{'revision':revision},**self.headers).status_code,302)
            self.client.post('/portal/enviar/',{'revision':revision},**self.headers)
        self.assertEqual(EventoAnalitico.objects.filter(tipo='carrito').count(),1)
        self.assertEqual(EventoAnalitico.objects.filter(tipo='pedido').count(),1)
        self.assertEqual(PedidoLocal.objects.count(),1)
    def test_error_analitico_no_impide_ingreso_o_carrito(self):
        cambiar_estado(True)
        with patch('midistri_portal.analitica_captura._registrar',side_effect=RuntimeError('offline')):
            self.assertEqual(self.login().status_code,200)
            with patch('midistri_portal.views.api',return_value=self.profile):
                self.assertEqual(self.client.post('/portal/cantidad/',{'producto':1,'cantidad':2},**self.headers).status_code,302)
        self.assertEqual(SesionVendedorPortal.objects.get(pk=self.tab).datos['midistri_cart'],{'1':2})
