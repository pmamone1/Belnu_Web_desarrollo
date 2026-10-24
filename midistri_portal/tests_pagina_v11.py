from copy import deepcopy
from uuid import uuid4
from unittest.mock import patch
from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError
from .models import Distribuidora,Tienda,Publicacion
from .test_operadores import PROFILE
from .client import ApiError

@override_settings(MIDISTRI_ADMIN_ENABLED=True,MIDISTRI_MULTIMEDIA_ENABLED=True)
class PaginaTests(TestCase):
    def setUp(self):
        self.d=Distribuidora.objects.create(pk=20,nombre='Belgrano')
        self.t=Tienda.objects.create(distribuidora=self.d,bienvenida='Original')
        self.perfil=dict(PROFILE,permisos=['midistri.tienda_configurar'])
    def remoto(self,action,**kw):
        return self.perfil if action=='operator-profile' else {'ok':True,'huella':kw['data']['huella']}
    def test_borrador_no_publico_y_publicacion_repetible(self):
        from . import pagina as p
        with patch.object(p,'api',side_effect=self.remoto):
            draft=p.borrador_tienda(self.perfil,20,'token')
            data=deepcopy(draft.datos);data['mensajes']['titulo']='Novedades'
            draft=p.guardar_borrador(self.perfil,20,data,draft.revision,str(uuid4()),'token')
            self.assertNotEqual(p.pagina_publica(self.d)['mensajes']['titulo'],'Novedades')
            review=p.revisar_borrador(self.perfil,20,'token')
            v=p.publicar_revision(self.perfil,20,review,'token')
            self.assertEqual(p.publicar_revision(self.perfil,20,review,'token').pk,v.pk)
            self.assertEqual(p.pagina_publica(self.d)['mensajes']['titulo'],'Novedades')
    def test_revision_obsoleta_y_fallo_remoto_conservan_publico(self):
        from . import pagina as p
        with patch.object(p,'api',side_effect=self.remoto):
            b=p.borrador_tienda(self.perfil,20,'token'); review=p.revisar_borrador(self.perfil,20,'token')
            data=deepcopy(b.datos);data['mensajes']['titulo']='Otro'
            p.guardar_borrador(self.perfil,20,data,b.revision,str(uuid4()),'token')
            with self.assertRaises(ValidationError):p.publicar_revision(self.perfil,20,review,'token')
            review=p.revisar_borrador(self.perfil,20,'token')
        with patch.object(p,'api',side_effect=ApiError('Sin red')):
            with self.assertRaises(ApiError):p.publicar_revision(self.perfil,20,review,'token')
        self.assertNotEqual(p.pagina_publica(self.d)['mensajes']['titulo'],'Otro')
    def test_limites_fuentes_y_temas(self):
        from . import pagina as p
        data=p.inicial(self.t)
        data['bloques']=[dict(id=str(uuid4()),tipo='banner',titulo='Hola',texto='',activo=True,diapositivas=[],segundos=2)]
        with self.assertRaises(ValidationError):p.validar_pagina(data,20)
        data['bloques'][0]['segundos']=5
        data['bloques']=data['bloques']*11
        with self.assertRaises(ValidationError):p.validar_pagina(data,20)
    def test_producto_retirado_no_revive_al_restaurar(self):
        from . import pagina as p
        pub=Publicacion.objects.create(producto_id=1,distribuidora=self.d,nombre='Pilas',precio=10,pvp=15,
            imagenes=[{'url':'https://sistema7000.belnu.com.ar/foto.jpg'}])
        data=p.inicial(self.t);data['bloques']+=[dict(id=str(uuid4()),tipo='banner',titulo='Pilas',texto='',activo=True,
            segundos=5,diapositivas=[{'publicacion':pub.pk,'tipo':'foto','url':pub.imagenes[0]['url'],'titulo':'','texto':'','enlace':'','boton':''}])]
        p.validar_pagina(data,20)
        pub.activa=False;pub.save()
        self.assertFalse(any(b['tipo']=='banner' for b in p.bloques_vigentes(data,20)))
        with self.assertRaises(ValidationError):p.validar_pagina(data,20)

    def test_editor_y_pantallas_antiguas_comparten_borrador(self):
        session=self.client.session;session['midistri_operador_token']='x'*43;session.save()
        with patch('midistri_portal.operadores.api',return_value=self.perfil),patch('midistri_portal.pagina.api',side_effect=self.remoto):
            r=self.client.get('/portal/administrar/pagina/?distribuidora=20')
            self.assertContains(r,'Banners de productos')
            self.assertContains(r,'Lista rápida')
            old=self.client.get('/portal/administrar/promociones/?distribuidora=20')
            self.assertEqual(old.status_code,302)
            self.assertIn('/administrar/pagina/',old['Location'])

    def test_revision_firmada_alterada_y_permiso_revocado(self):
        from . import pagina as p
        with patch.object(p,'api',side_effect=self.remoto):
            p.borrador_tienda(self.perfil,20,'token')
            review=p.revisar_borrador(self.perfil,20,'token')
            with self.assertRaises(ValidationError):p.publicar_revision(self.perfil,20,review+'x','token')
        with patch.object(p,'api',return_value=dict(self.perfil,permisos=[])):
            with self.assertRaises(ApiError):p.publicar_revision(self.perfil,20,review,'token')

    def test_backfill_publico_equivalente_y_borrador_no_lo_muta(self):
        from django.apps import apps
        from django.db import connection
        from importlib import import_module
        from .models import BloquePromocional
        from . import pagina as p
        BloquePromocional.objects.create(tienda=self.t,titulo='Vigente',texto='<script>texto</script>',tipo='texto',activo=True)
        import_module('midistri_portal.migrations.0009_pagina_tienda').conservar_vigente(apps,type('Editor',(),{'connection':connection})())
        snapshot=p.pagina_publica(self.d)
        self.assertEqual(snapshot['mensajes']['bienvenida'],'Original')
        self.assertEqual(snapshot['bloques'][0]['titulo'],'Vigente')
        with patch.object(p,'api',side_effect=self.remoto):
            draft=p.borrador_tienda(self.perfil,20,'token')
            data=deepcopy(draft.datos);data['bloques'][0]['titulo']='Privado'
            p.guardar_borrador(self.perfil,20,data,draft.revision,str(uuid4()),'token')
        response=self.client.get('/portal/?distribuidora=20')
        self.assertContains(response,'Vigente')
        self.assertContains(response,'&lt;script&gt;texto&lt;/script&gt;')
        self.assertNotContains(response,'Privado')

    def test_limite_20_fotos_y_rotacion_una_sola(self):
        from . import pagina as p
        pub=Publicacion.objects.create(producto_id=1,distribuidora=self.d,nombre='Pilas',precio=10,pvp=15,
            multimedia=[{'tipo':'foto','url':'https://example.test/pilas.png'}])
        data=p.inicial(self.t)
        slide={'publicacion':pub.pk,'tipo':'foto','url':pub.multimedia[0]['url']}
        b=dict(id=str(uuid4()),tipo='banner',titulo='Pilas',texto='',activo=True,segundos=5,diapositivas=[slide]*21)
        data['bloques'].append(b)
        with self.assertRaises(ValidationError):p.validar_pagina(data,20)
        b['diapositivas']=[slide]
        data=p.validar_pagina(data,20)
        from django.template.loader import render_to_string
        html=render_to_string('midistri_portal/pagina_bloques.html',{'bloques':p.bloques_vigentes(data,20),'pagina':data,'pagina_mensajes':data['mensajes'],'distribuidora':self.d})
        self.assertNotIn('data-banner-next',html)

    def test_editor_guardar_revisar_publicar_desde_http(self):
        session=self.client.session;session['midistri_operador_token']='x'*43;session.save()
        with patch('midistri_portal.operadores.api',return_value=self.perfil),patch('midistri_portal.pagina.api',side_effect=self.remoto):
            self.client.get('/portal/administrar/pagina/?distribuidora=20')
            response=self.client.post('/portal/administrar/pagina/',dict(distribuidora=20,accion='general',revision=0,
                operacion=str(uuid4()),diseno='lista',tema='azul',titulo='Mi catálogo',subtitulo='',email='',telefono='',
                bienvenida='Hola',instrucciones='',carrito='',recibido='',contacto='',boton_pedido=''))
            self.assertEqual(response.status_code,302)
            public=self.client.get('/portal/?distribuidora=20')
            self.assertNotContains(public,'Mi catálogo')
            preview=self.client.get('/portal/administrar/pagina/previa/?distribuidora=20&pantalla=movil')
            self.assertContains(preview,'Mi catálogo')
            self.assertIn('no-store',preview['Cache-Control'])
            response=self.client.post('/portal/administrar/pagina/',dict(distribuidora=20,accion='publicar',firma=preview.context['firma']))
            self.assertEqual(response.status_code,302)
            public=self.client.get('/portal/?distribuidora=20')
            self.assertContains(public,'Mi catálogo');self.assertContains(public,'diseno-lista')

    def test_rechazo_definitivo_libera_borrador(self):
        from . import pagina as p
        def remote(action,**kw):
            if action=='operator-page-publish':raise ApiError('Fuente retirada',409)
            return self.remoto(action,**kw)
        with patch.object(p,'api',side_effect=remote):
            p.borrador_tienda(self.perfil,20,'token')
            firma=p.revisar_borrador(self.perfil,20,'token')
            with self.assertRaises(ApiError):p.publicar_revision(self.perfil,20,firma,'token')
            draft=p.borrador_tienda(self.perfil,20,'token')
            self.assertIsNone(draft.pendiente_id)
            data=deepcopy(draft.datos);data['mensajes']['titulo']='Corregido'
            p.guardar_borrador(self.perfil,20,data,draft.revision,str(uuid4()),'token')

    def test_otro_operador_puede_descartar_intento_incierto_con_auditoria(self):
        from . import pagina as p
        def remote(action,**kw):
            if action=='operator-page-publish':raise ApiError('Sin respuesta')
            return self.remoto(action,**kw)
        with patch.object(p,'api',side_effect=remote):
            p.borrador_tienda(self.perfil,20,'token');firma=p.revisar_borrador(self.perfil,20,'token')
            with self.assertRaises(ApiError):p.publicar_revision(self.perfil,20,firma,'token')
            draft=p.borrador_tienda(self.perfil,20,'token')
        other=dict(self.perfil,operador_id=8)
        with patch.object(p,'api',return_value=other):
            p.descartar_pendiente(other,20,str(draft.pendiente_id),draft.revision,'Corregir contenido','token')
        draft.refresh_from_db();self.assertIsNone(draft.pendiente_id)
        self.assertGreater(draft.revision,0)
        self.assertTrue(draft.edicionpagina_set.filter(operador_id=8).exists())

    @override_settings(MIDISTRI_MULTIMEDIA_ENABLED=False)
    def test_bandera_multimedia_oculta_promociones_anteriores(self):
        from .models import BloquePromocional
        BloquePromocional.objects.create(tienda=self.t,titulo='Promoción apagada',tipo='texto',activo=True)
        r=self.client.get('/portal/?distribuidora=20')
        self.assertContains(r,'Original')
        self.assertNotContains(r,'Promoción apagada')

    def test_conserva_email_visible_y_normaliza_tema_anterior(self):
        from . import pagina as p
        self.d.email_respuesta='respuesta@example.test';self.d.save()
        self.t.tema='violeta_pastel';self.t.save()
        data=p.inicial(self.t)
        self.assertEqual(data['presentacion']['email'],'respuesta@example.test')
        self.assertEqual(data['tema'],'claro')

    def test_tienda_autorizada_no_sincronizada_da_error_claro(self):
        from . import pagina as p
        profile=dict(self.perfil,distribuidoras=[{'id':65,'nombre':'Barracas'}])
        with patch.object(p,'api',return_value=profile):
            with self.assertRaises(ApiError):p.borrador_tienda(profile,65,'token')

    def test_pagina_inicial_conserva_disposicion_anterior_hasta_publicar(self):
        from .models import BloquePromocional
        BloquePromocional.objects.create(tienda=self.t,titulo='Oferta anterior',texto='Texto vigente',tipo='texto',activo=True)
        response=self.client.get('/portal/?distribuidora=20')
        self.assertContains(response,'promociones-rail')
        self.assertContains(response,'Oferta anterior')

from django.test import TransactionTestCase

class MigracionPaginaTests(TransactionTestCase):
    def test_dos_operadores_no_sobrescriben_misma_revision(self):
        from django.db import connection,close_old_connections
        if connection.vendor!='postgresql':self.skipTest('Bloqueo real verificado en PostgreSQL QA.')
        from concurrent.futures import ThreadPoolExecutor
        from . import pagina as p
        d=Distribuidora.objects.create(pk=20,nombre='Belgrano');Tienda.objects.create(distribuidora=d)
        profile=dict(PROFILE,permisos=['midistri.tienda_configurar'])
        with patch.object(p,'api',return_value=profile):
            draft=p.borrador_tienda(profile,20,'token')
            def edit(title):
                close_old_connections()
                try:
                    data=deepcopy(draft.datos);data['mensajes']['titulo']=title
                    try:p.guardar_borrador(profile,20,data,draft.revision,str(uuid4()),'token');return 'guardado'
                    except ValidationError:return 'revision_obsoleta'
                finally:close_old_connections()
            with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(edit,['Primero','Segundo']))
        self.assertCountEqual(results,['guardado','revision_obsoleta'])

    def test_migracion_real_conserva_tienda_y_promociones(self):
        from django.db import connection
        from django.db.migrations.executor import MigrationExecutor
        old=('midistri_portal','0008_recuperacion_promociones')
        new=('midistri_portal','0009_pagina_tienda')
        executor=MigrationExecutor(connection)
        try:
            executor.migrate([old])
            apps=executor.loader.project_state([old]).apps
            D=apps.get_model('midistri_portal','Distribuidora');T=apps.get_model('midistri_portal','Tienda');B=apps.get_model('midistri_portal','BloquePromocional')
            d=D.objects.create(pk=65,nombre='Barracas',email_respuesta='tienda@example.test')
            t=T.objects.create(distribuidora=d,bienvenida='Hola',tema='verde')
            block=B.objects.create(tienda=t,titulo='Anterior',tipo='texto',activo=True)
            executor=MigrationExecutor(connection);executor.migrate([new])
            apps=executor.loader.project_state([new]).apps
            page=apps.get_model('midistri_portal','PaginaTienda').objects.get(tienda_id=t.pk)
            self.assertEqual(page.publicada.datos['mensajes']['bienvenida'],'Hola')
            self.assertEqual(page.publicada.datos['presentacion']['email'],'tienda@example.test')
            self.assertEqual(page.publicada.datos['bloques'][0]['titulo'],'Anterior')
            self.assertTrue(apps.get_model('midistri_portal','BloquePromocional').objects.get(pk=block.pk).activo)
        finally:MigrationExecutor(connection).migrate([new])
