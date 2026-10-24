from unittest.mock import patch
from django.test import TestCase,override_settings
from urllib.parse import urlsplit,parse_qs
from .test_operadores import PROFILE
from .models import Distribuidora

@override_settings(MIDISTRI_ENABLED=True,MIDISTRI_ADMIN_ENABLED=True)
class AccesoGuiaTests(TestCase):
    def entrada(self,did=20):
        return self.client.get('/portal/administrar/entrada/?destino=tienda&distribuidora='+str(did))
    def completar(self,response,api):
        nonce=parse_qs(urlsplit(response['Location']).query)['desafio'][0]
        api.return_value={'perfil':dict(PROFILE,permisos=['midistri.tienda_configurar','pedidos.gestionar']),'session_token':'s'*43}
        return self.client.post('/portal/administrar/entrar/',{'codigo':'c'*43,'desafio':nonce},HTTP_ORIGIN='https://sistema7000.belnu.com.ar')
    def test_publico_tiene_acceso_distribuidor(self):
        r=self.client.get('/portal/')
        self.assertContains(r,'Acceso Distribuidor')
    @patch('midistri_portal.operadores.api')
    def test_entrada_directa_editor(self,api):
        r=self.completar(self.entrada(),api)
        self.assertEqual(r['Location'],'/portal/administrar/pagina/?distribuidora=20')
    @patch('midistri_portal.operadores.api')
    def test_tienda_ajena_no_se_cambia_por_primera(self,api):
        r=self.completar(self.entrada(61),api)
        self.assertEqual(r.status_code,403)
        self.assertNotIn('midistri_operador_token',self.client.session)
    @patch('midistri_portal.operadores.api')
    def test_dos_pestanas_no_pisan_destino(self,api):
        a=self.entrada(20);self.entrada(65)
        r=self.completar(a,api)
        self.assertEqual(r['Location'],'/portal/administrar/pagina/?distribuidora=20')
    @patch('midistri_portal.operadores.api')
    def test_panel_sin_configuracion_explicita_permiso(self,api):
        api.return_value=dict(PROFILE,permisos=['pedidos.gestionar'])
        s=self.client.session;s['midistri_operador_token']='x'*43;s.save()
        r=self.client.get('/portal/administrar/')
        self.assertContains(r,'No tenés habilitado el permiso para configurar')
        self.assertContains(r,'Pedidos')
        self.assertNotContains(r,'>Configurar MiDistri</a>')
    @patch('midistri_portal.operadores.api')
    def test_panel_separa_configuracion_y_pedidos(self,api):
        api.return_value=dict(PROFILE,permisos=['midistri.tienda_configurar','pedidos.gestionar'])
        s=self.client.session;s['midistri_operador_token']='x'*43;s.save()
        r=self.client.get('/portal/administrar/')
        self.assertContains(r,'>Configurar MiDistri</a>')
        self.assertContains(r,'/portal/administrar/pagina/?distribuidora=20')
        self.assertContains(r,'Ver mi sitio')
    @patch('midistri_portal.operadores.api')
    def test_sin_permiso_no_abre_editor(self,api):
        a=self.entrada()
        nonce=parse_qs(urlsplit(a['Location']).query)['desafio'][0]
        api.return_value={'perfil':dict(PROFILE,permisos=['pedidos.gestionar']),'session_token':'s'*43}
        r=self.client.post('/portal/administrar/entrar/',{'codigo':'c'*43,'desafio':nonce},HTTP_ORIGIN='https://sistema7000.belnu.com.ar')
        self.assertTrue(r['Location'].startswith('/portal/administrar/?'))
