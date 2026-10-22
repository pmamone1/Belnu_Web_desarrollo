from django.test import TestCase,override_settings
from unittest.mock import patch
from .test_operadores import PROFILE
from .client import ApiError

@override_settings(MIDISTRI_ADMIN_ENABLED=True)
class AdministracionPortalTests(TestCase):
    def setUp(self):
        s=self.client.session;s['midistri_operador_token']='x'*43;s.save()
    def test_catalogo_panel_tiene_boton_catalogo_completo(self):
        with patch('midistri_portal.operadores.api',return_value=PROFILE),patch('midistri_portal.operadores_views.api',create=True) as api:
            api.return_value={'version':1,'total':1,'pagina':1,'paginas':1,
                'productos':[{'id':1,'nombre':'Pilas','sku':'P1','precio':'100.00','pvp':'150.00','imagenes':[],'publicado':True}],
                'proveedores':[{'id':1,'nombre':'Proveedor'}]}
            r=self.client.get('/portal/administrar/productos/?distribuidora=20')
            self.assertEqual(r.status_code,200);self.assertContains(r,'Publicar catálogo completo')
    def test_tienda_ajena_no_llama_operacion(self):
        with patch('midistri_portal.operadores.api',return_value=PROFILE),patch('midistri_portal.operadores_views.api',create=True) as api:
            r=self.client.get('/portal/administrar/productos/?distribuidora=61')
            self.assertEqual(r.status_code,403);api.assert_not_called()
    def test_sync_fallida_no_reconfirma_publicacion(self):
        with patch('midistri_portal.operadores.api',return_value=PROFILE),patch('midistri_portal.operadores_views.api',create=True) as api,patch('midistri_portal.operadores_views.sincronizar',create=True,side_effect=ApiError('Sin red')):
            api.return_value={'version':1,'guardado':True,'resumen':{'altas':1}}
            r=self.client.post('/portal/administrar/publicar/',{'distribuidora':20,'accion':'confirmar','operacion':'00000000-0000-4000-8000-000000000001'})
            self.assertEqual(r.status_code,302)
            self.assertEqual(api.call_count,1)
            self.assertTrue(self.client.session['midistri_sync_pendiente'])
    def test_respuesta_catalogo_invalida_no_muestra_ajenos(self):
        with patch('midistri_portal.operadores.api',return_value=PROFILE),patch('midistri_portal.operadores_views.api',create=True,return_value={'version':0,'productos':[{'nombre':'PRIVADO AJENO'}]}):
            r=self.client.get('/portal/administrar/productos/?distribuidora=20')
            self.assertEqual(r.status_code,503);self.assertNotContains(r,'PRIVADO AJENO',status_code=503)
