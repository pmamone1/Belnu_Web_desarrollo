"""Presentation compatibility: private origin and operator access stay intact."""
from unittest.mock import patch
from django.test import TestCase, override_settings
from .client import ApiError, api
from .test_operadores import PROFILE

@override_settings(MIDISTRI_ENABLED=True, MIDISTRI_ADMIN_ENABLED=True, MIDISTRI_LOGIN_CODIGO_ENABLED=True)
class MarcaPortalTests(TestCase):
    def test_acceso_email_neutro_y_perfiles_conservados(self):
        response=self.client.get('/portal/acceso/')
        self.assertContains(response,'cuenta de la distribuidora')
        self.assertNotContains(response,'Urban Soft')

    def test_error_de_acceso_conserva_estado_y_reintento(self):
        response=self.client.post('/portal/administrar/entrar/',{})
        self.assertEqual(response.status_code,403)
        self.assertContains(response,'Iniciar de nuevo desde la administración de la distribuidora',status_code=403)
        self.assertNotContains(response,'Urban Soft',status_code=403)

    def test_panel_conserva_permiso_y_distribuidora(self):
        session=self.client.session;session['midistri_operador_token']='x'*43;session.save()
        with patch('midistri_portal.operadores.api',return_value=PROFILE):
            response=self.client.get('/portal/administrar/')
        self.assertContains(response,'20 - Belgrano')
        self.assertNotContains(response,'Urban Soft')
        self.assertContains(response,'No tenés habilitado el permiso')

    def test_errores_conocidos_se_adaptan_sin_tocar_datos_ajenos(self):
        error=ApiError('Falta configurar la conexión HTTPS con Urban Soft.',503)
        self.assertEqual(str(error),'Falta configurar la conexión HTTPS con la distribuidora.')
        self.assertEqual(error.status,503)
        self.assertEqual(str(ApiError('Producto Urban Soft edición especial no disponible.',400)),
                         'Producto Urban Soft edición especial no disponible.')

    @override_settings(URBAN_API_BASE='https://sistema7000.belnu.com.ar/midistri/api/',URBAN_API_TOKEN='private')
    def test_error_api_no_cambia_destino_credenciales_ni_estado(self):
        class Response:
            status_code=503
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def iter_content(self,size):
                yield br'{"error":"Falta configurar la conexi\u00f3n HTTPS con Urban Soft."}'
        with patch('midistri_portal.client.requests.request',return_value=Response()) as call:
            with self.assertRaises(ApiError) as caught:api('operator-profile',operator_token='operator')
        self.assertEqual(str(caught.exception),'Falta configurar la conexión HTTPS con la distribuidora.')
        self.assertEqual(caught.exception.status,503)
        self.assertEqual(call.call_args.args[1],'https://sistema7000.belnu.com.ar/midistri/api/operator-profile/')
        self.assertEqual(call.call_args.kwargs['headers']['X-Midistri-Operator'],'operator')


    def test_error_historico_se_presenta_neutro_sin_reescribirlo(self):
        from django.template.loader import render_to_string
        from .models import Sincronizacion
        state=Sincronizacion.objects.create(pk=1,error='Falta configurar la conexión HTTPS con Urban Soft.')
        html=render_to_string('midistri_portal/gestion.html',{'sync':state})
        self.assertNotIn('Urban Soft',html)
        state.refresh_from_db()
        self.assertEqual(state.error,'Falta configurar la conexión HTTPS con Urban Soft.')

    def test_plantillas_y_recursos_sin_marca_abreviada(self):
        import re
        from pathlib import Path
        root=Path(__file__).resolve().parents[1]
        for folder in ['midistri_portal/templates','midistri_portal/static','templates','static']:
            for path in (root/folder).rglob('*'):
                if path.is_file() and path.suffix in ('.html','.js','.css','.svg'):
                    self.assertIsNone(re.search(r'\burban\b',path.read_text(encoding='utf-8-sig'),re.I),str(path))

    def test_mensajes_y_errores_ui_sin_marca_abreviada(self):
        import ast,re
        from pathlib import Path
        for path in Path(__file__).resolve().parent.rglob('*.py'):
            if path.name.startswith('test'):continue
            tree=ast.parse(path.read_text(encoding='utf-8-sig'))
            for call in ast.walk(tree):
                if not isinstance(call,ast.Call):continue
                name=getattr(call.func,'id',None) or getattr(call.func,'attr',None)
                if name not in ('ApiError','HttpResponse','CommandError','warning','success','error','info'):continue
                for arg in call.args:
                    if isinstance(arg,ast.Constant) and isinstance(arg.value,str):
                        self.assertIsNone(re.search(r'\burban\b',arg.value,re.I),str(path)+':'+str(call.lineno))
