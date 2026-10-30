"""Browser ownership is persistent; carts and privileges remain isolated."""
from importlib import import_module,util
from unittest.mock import patch
from uuid import uuid4
from django.conf import settings
from django.test import TestCase,override_settings,Client
from . import test_acceso_email_v14 as fixtures
from .client import ApiError
from .models import SesionVendedorPortal

@override_settings(MIDISTRI_LOGIN_CODIGO_ENABLED=True,MIDISTRI_ADMIN_ENABLED=True,
 MIDISTRI_ACCESO_RECORDADO_ENABLED=True)
class DispositivoPortalTests(TestCase):
    iniciar=fixtures.AccesoEmailPortalTests.iniciar
    response=fixtures.AccesoEmailPortalTests.response
    def setUp(self):
        fixtures.AccesoEmailPortalTests.setUp(self)
        self.assertIsNotNone(util.find_spec('midistri_portal.dispositivos'),'Falta acceso recordado automatico')
        self.devices=import_module('midistri_portal.dispositivos')
        self.remote_profiles=[dict(x,vendedor_id=7) for x in self.options]
        self.remote_error=None;self.remote_revoked=[]
        p=patch('midistri_portal.dispositivos.api',side_effect=self.device_response)
        p.start();self.addCleanup(p.stop)
    def device_response(self,action,**kw):
        if self.remote_error:raise self.remote_error
        if action=='capabilities':return {'seller_device':1,'seller_device_habilitado':True}
        if action=='seller-device-remember':return {'version':1,'dispositivo':kw['data']['credencial'].split('.')[0]}
        if action=='seller-device-profiles':return {'version':1,'identidades':self.remote_profiles}
        if action=='seller-device-resume':
            selection=kw['data']['seleccion'];opt=next(i for i in self.remote_profiles if i['seleccion']==selection)
            profile=dict(self.profile)
            if opt['distribuidora_id']!=20:profile.update(id=8,nombre='Otro kiosco',distribuidora_id=61,distribuidora='61 - Recova')
            return {'version':1,'tipo':'vendedor','perfil':profile,'session_token':kw.get('token') or 'remembered-bearer-'+'z'*30}
        if action=='seller-device-revoke':self.remote_revoked.append(kw['data']['dispositivo']);return {'version':1,'ok':True}
        raise AssertionError(action)
    def login(self):
        self.iniciar()
        r=self.client.post('/portal/acceso/verificar/',{'codigo':'123456'},**self.headers)
        self.assertEqual(r.status_code,200)
        return r
    def resume(self,**kwargs):return self.client.post('/portal/acceso/recordado/',kwargs,**self.headers)
    def test_codigo_crea_cookie_persistente_automatica_sin_exponer_credencial(self):
        r=self.login();cookie=r.cookies[self.devices.COOKIE]
        self.assertTrue(cookie['secure']);self.assertTrue(cookie['httponly']);self.assertEqual(cookie['samesite'],'Lax')
        self.assertEqual(cookie['path'],'/portal/');self.assertEqual(int(cookie['max-age']),34560000)
        self.assertNotIn(cookie.value,r.content.decode());self.assertNotIn('private-bearer',r.content.decode())
        from .models import DispositivoRecordado
        device=DispositivoRecordado.objects.get();self.assertNotIn(cookie.value,device.hash_cookie)
        self.assertEqual(SesionVendedorPortal.objects.get().dispositivo_id,device.pk)
    def test_otro_browser_session_y_nueva_pestana_restauran_sin_codigo(self):
        self.login();self.client.cookies.pop(settings.SESSION_COOKIE_NAME,None)
        self.headers=dict(self.headers,HTTP_X_MIDISTRI_TAB=str(uuid4()),HTTP_X_MIDISTRI_TAB_PROOF='b'*64)
        r=self.resume();self.assertEqual(r.status_code,200);self.assertEqual(r.json()['fase'],'dentro')
        self.assertEqual(SesionVendedorPortal.objects.count(),2)
    def test_restaurar_misma_pestana_conserva_carrito(self):
        self.login();row=SesionVendedorPortal.objects.get();row.datos={'midistri_cart':{'1':3}};row.save()
        self.assertEqual(self.resume().status_code,200)
        row.refresh_from_db();self.assertEqual(row.datos['midistri_cart'],{'1':3})
        self.assertEqual(SesionVendedorPortal.objects.count(),1)
    def test_nueva_pestana_no_copia_carrito(self):
        self.login();row=SesionVendedorPortal.objects.get();row.datos={'midistri_cart':{'1':3}};row.save()
        self.headers['HTTP_X_MIDISTRI_TAB']=str(uuid4());self.headers['HTTP_X_MIDISTRI_TAB_PROOF']='b'*64
        self.resume();self.assertEqual(SesionVendedorPortal.objects.get(pk=self.headers['HTTP_X_MIDISTRI_TAB']).datos,{})
        row.refresh_from_db();self.assertEqual(row.datos['midistri_cart'],{'1':3})
    def test_varios_perfiles_en_nueva_pestana_ofrecen_selector_sin_email_ni_codigo(self):
        self.login();self.remote_profiles.append({'seleccion':'q'*32,'nombre':'Otro kiosco','distribuidora':'61 - Recova','tipo':'vendedor','distribuidora_id':61,'vendedor_id':8})
        self.headers['HTTP_X_MIDISTRI_TAB']=str(uuid4());self.headers['HTTP_X_MIDISTRI_TAB_PROOF']='b'*64
        r=self.resume();self.assertEqual(r.json()['fase'],'elegir');self.assertEqual(len(r.json()['identidades']),2)
        r=self.resume(seleccion='q'*32);self.assertEqual(r.json()['fase'],'dentro')
        self.assertEqual(SesionVendedorPortal.objects.get(pk=self.headers['HTTP_X_MIDISTRI_TAB']).distribuidora_id,61)
    def test_api_no_puede_restaurar_administracion(self):
        self.login();self.remote_profiles[0]['tipo']='administracion'
        self.assertEqual(self.resume().status_code,503)
    def test_sin_cookie_ni_prueba_no_hay_recuerdo_ni_nombres(self):
        r=self.resume();self.assertEqual(r.status_code,200);self.assertEqual(r.json()['fase'],'sin_recuerdo')
        self.assertNotIn('Kiosco',r.content.decode())
    def test_cookie_manipulada_no_muestra_perfiles(self):
        self.login();self.client.cookies[self.devices.COOKIE]=str(uuid4())+'.'+'x'*43
        r=self.resume();self.assertEqual(r.status_code,403);self.assertNotIn('Kiosco',r.content.decode())
    def test_bandera_apagada_no_emite_cookie_y_no_restaura(self):
        with override_settings(MIDISTRI_ACCESO_RECORDADO_ENABLED=False):
            r=self.login();self.assertNotIn(self.devices.COOKIE,r.cookies)
            self.assertEqual(self.resume().json()['fase'],'deshabilitado')
    def test_urban_caido_no_borra_cookie_al_intentar_restaurar(self):
        self.login();old=self.client.cookies[self.devices.COOKIE].value;self.remote_error=ApiError('No disponible',503)
        r=self.resume();self.assertEqual(r.status_code,503)
        self.assertEqual(self.client.cookies[self.devices.COOKIE].value,old)
    def test_logout_olvida_dispositivo_y_revoca_todas_sus_pestanas_aun_con_urban_caido(self):
        self.login();self.headers['HTTP_X_MIDISTRI_TAB']=str(uuid4());self.headers['HTTP_X_MIDISTRI_TAB_PROOF']='b'*64;self.resume()
        self.remote_error=ApiError('No disponible',503)
        r=self.client.post('/portal/salir/',HTTP_ACCEPT='application/json',**self.headers)
        self.assertEqual(r.status_code,200);self.assertEqual(int(r.cookies[self.devices.COOKIE]['max-age']),0)
        from .models import DispositivoRecordado
        self.assertTrue(DispositivoRecordado.objects.get().revocado);self.assertTrue(DispositivoRecordado.objects.get().remoto_pendiente)
        self.assertFalse(SesionVendedorPortal.objects.filter(revocado=False).exists())
        self.assertEqual(self.client.post('/portal/cantidad/',{'producto':1,'cantidad':1},**self.headers).status_code,403)
    def test_cierre_offline_persistente_bloquea_restauracion_hasta_olvidar(self):
        self.login();self.client.cookies[self.devices.OLVIDO]='1'
        self.assertEqual(self.resume().status_code,403)
        r=self.client.post('/portal/acceso/olvidar/')
        self.assertEqual(r.status_code,200)
        from .models import DispositivoRecordado
        self.assertTrue(DispositivoRecordado.objects.get().revocado)
        self.assertEqual(int(r.cookies[self.devices.COOKIE]['max-age']),0)
    def test_olvido_remoto_pendiente_se_concilia_sin_cron_y_sin_revive(self):
        self.login();self.remote_error=ApiError('No disponible',503)
        self.client.post('/portal/acceso/olvidar/')
        from .models import DispositivoRecordado
        self.assertTrue(DispositivoRecordado.objects.get().remoto_pendiente)
        self.remote_error=None;self.resume()
        self.assertFalse(DispositivoRecordado.objects.get().remoto_pendiente)
        self.assertTrue(DispositivoRecordado.objects.get().revocado)
    def test_csrf_es_obligatorio_para_restaurar_y_olvidar(self):
        c=Client(enforce_csrf_checks=True)
        for url in ('/portal/acceso/recordado/','/portal/acceso/olvidar/'):
            self.assertEqual(c.post(url).status_code,403)
    def test_cookie_no_se_crea_si_urban_no_soporta_la_capacidad(self):
        original=self.device_response
        with patch('midistri_portal.dispositivos.api',side_effect=lambda action,**kw: {} if action=='capabilities' else original(action,**kw)):
            r=self.login();self.assertNotIn(self.devices.COOKIE,r.cookies)
    def test_adopta_sesion_codigo_existente_sin_borrar_su_carrito(self):
        with override_settings(MIDISTRI_ACCESO_RECORDADO_ENABLED=False):self.login()
        row=SesionVendedorPortal.objects.get();row.datos={'midistri_cart':{'1':3}};row.save()
        r=self.resume();self.assertEqual(r.json()['fase'],'dentro');self.assertIn(self.devices.COOKIE,r.cookies)
        row.refresh_from_db();self.assertEqual(row.datos['midistri_cart'],{'1':3})

    def test_restauracion_no_borra_tombstone_creado_mientras_viaja_la_respuesta(self):
        self.login()
        r=self.resume()
        self.assertNotIn(self.devices.OLVIDO,r.cookies)

    def test_analitica_distingue_restauracion_y_no_repite_ingreso_al_refrescar(self):
        from .analitica_captura import cambiar_estado
        from .models import EventoAnalitico
        cambiar_estado(True);self.login()
        self.assertEqual(EventoAnalitico.objects.filter(tipo='ingreso').count(),1)
        self.headers['HTTP_X_MIDISTRI_TAB']=str(uuid4());self.headers['HTTP_X_MIDISTRI_TAB_PROOF']='b'*64
        self.resume();self.resume()
        self.assertEqual(EventoAnalitico.objects.filter(tipo='ingreso_recordado').count(),1)
        self.assertEqual(EventoAnalitico.objects.filter(tipo='ingreso').count(),1)

    def test_diagnostico_local_no_expone_cookie_ni_cambia_estado(self):
        from io import StringIO
        from django.core.management import call_command
        self.login();output=StringIO()
        call_command('midistri_acceso_recordado_estado',local=True,stdout=output)
        self.assertNotIn(self.client.cookies[self.devices.COOKIE].value,output.getvalue())
        self.assertIn('dispositivos',output.getvalue())
        from .models import DispositivoRecordado
        self.assertFalse(DispositivoRecordado.objects.get().revocado)

from . import test_analitica_informes_v28 as analytics_fixtures
class InformesRecordadosTests(TestCase):
    setUp=analytics_fixtures.InformesAnaliticaTests.setUp
    modulos=analytics_fixtures.InformesAnaliticaTests.modulos
    api=analytics_fixtures.InformesAnaliticaTests.api
    consulta=analytics_fixtures.InformesAnaliticaTests.consulta
    actividad=analytics_fixtures.InformesAnaliticaTests.actividad
    def test_informe_cuenta_y_filtra_acceso_recordado_como_ingreso(self):
        self.actividad()
        from .models import EventoAnalitico
        EventoAnalitico.objects.create(distribuidora_id=20,vendedor_id=7,vendedor='Visita sin pedido',visita=uuid4(),tipo='ingreso_recordado',huella='e'*64)
        q=self.consulta();_,reports=self.modulos()
        result=reports.resultado(q,{})
        self.assertEqual(result['resumen']['ingresos'],1)
        selected=reports.resultado(q,{'tipo':'ingreso_recordado'})
        self.assertEqual(selected['eventos'].count(),1)

