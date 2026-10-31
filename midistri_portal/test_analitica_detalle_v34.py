from copy import deepcopy
from datetime import timedelta
from unittest.mock import patch
from uuid import uuid4
from django.test import TestCase
from django.utils import timezone
from . import test_analitica_informes_v28 as fixture
from .models import EventoAnalitico,ConsultaAnalitica
from .client import ApiError

class DetalleAnaliticoTests(TestCase):
    setUp=fixture.InformesAnaliticaTests.setUp
    modulos=fixture.InformesAnaliticaTests.modulos
    api=fixture.InformesAnaliticaTests.api
    consulta=fixture.InformesAnaliticaTests.consulta
    def dataset(self):
        visits=[uuid4(),uuid4(),uuid4()]
        for seller,visit,kind in [(7,visits[0],k) for k in ('catalogo','ingreso','producto_consulta','foto_ampliada','video_enlace')]+[(8,visits[1],k) for k in ('ingreso_recordado','producto_consulta','foto_ampliada','video_mp4')]+[(8,visits[2],'catalogo')]:
            EventoAnalitico.objects.create(fecha=self.cut-timedelta(seconds=2),distribuidora_id=20,vendedor_id=seller,vendedor='Visita sin pedido' if seller==7 else 'Pidió sin visita',visita=visit,tipo=kind,producto_id=101 if kind in ('producto_consulta','foto_ampliada','video_enlace','video_mp4') else None,producto='Termo <QA>',sku='T-101',huella='a'*64)
        EventoAnalitico.objects.create(fecha=self.cut-timedelta(seconds=2),distribuidora_id=61,vendedor_id=999,vendedor='AJENO',visita=uuid4(),tipo='ingreso',huella='a'*64)
        EventoAnalitico.objects.create(fecha=self.cut+timedelta(days=1),distribuidora_id=20,vendedor_id=999,vendedor='POSTERIOR',visita=uuid4(),tipo='ingreso',huella='a'*64)
        return self.consulta()
    def detalle(self,data,key,page=1):
        from .analitica_detalle import detalle
        return detalle(data,key,page)
    def test_nueve_totales_concilian_y_excluyen_datos_ajenos_y_posteriores(self):
        from .analitica_informes import resultado
        q=self.dataset();data=resultado(q,{})
        for key,value in {'consultas_productos':2,'productos_consultados':1,'vendedores_activos':2,'visitas':3,'ingresos':2,'fotos':2,'videos':2,'pedidos':1,'conversion':2}.items():
            with self.subTest(key=key):self.assertEqual(self.detalle(data,key)['total'],value)
        self.assertEqual(data['resumen']['conversion'],50)
        conversion=self.detalle(data,'conversion')
        self.assertIn('1 de 2',conversion['nota'])
        for key in ('ingresos','fotos','videos'):
            text=str(self.detalle(data,key)['filas']);self.assertNotIn('AJENO',text);self.assertNotIn('POSTERIOR',text)
    def test_filtros_y_ficha_no_cambian_totales_del_detalle(self):
        from .analitica_informes import resultado
        q=self.dataset();data=resultado(q,{'tipo':'foto_ampliada','vendedor':'7','tienda':'20'})
        self.assertEqual(data['eventos'].count(),1)
        self.assertEqual(self.detalle(data,'fotos')['total'],2)
        self.assertEqual(self.detalle(data,'pedidos')['total'],1)
    def test_inactivos_con_actividad_se_incluyen_en_detalle(self):
        from .analitica_informes import resultado
        self.vs[0].update(actual=False,activo=False)
        q=self.dataset();data=resultado(q,{})
        self.assertNotIn(7,[v['id'] for v in data['vendedores']])
        self.assertEqual(self.detalle(data,'vendedores_activos')['total'],2)
    def test_producto_unico_y_visita_unica_aunque_haya_dos_tiendas(self):
        from .analitica_informes import resultado
        q=self.dataset();q.distribuidoras=[20,65];q.meta['distribuidoras'].append({'id':65,'nombre':'65 - Barracas'})
        visit=EventoAnalitico.objects.filter(tipo='producto_consulta').first().visita
        EventoAnalitico.objects.create(fecha=self.cut-timedelta(seconds=2),distribuidora_id=65,vendedor_id=77,vendedor='Otro perfil',visita=visit,tipo='producto_consulta',producto_id=101,producto='Termo <QA>',sku='T-101',huella='a'*64)
        data=resultado(q,{})
        self.assertEqual(self.detalle(data,'productos_consultados')['total'],1)
        self.assertEqual(self.detalle(data,'visitas')['total'],3)
        self.assertIn('Otro perfil',str(self.detalle(data,'visitas')['filas']))
    def test_paginacion_determinista_y_cero_registros(self):
        from .analitica_informes import resultado
        q=self.consulta();data=resultado(q,{})
        self.assertEqual(self.detalle(data,'fotos')['total'],0)
        for i in range(51):EventoAnalitico.objects.create(fecha=self.cut-timedelta(seconds=2),distribuidora_id=20,vendedor_id=7,vendedor='QA',visita=uuid4(),tipo='foto_ampliada',huella='a'*64)
        data=resultado(q,{})
        self.assertEqual(len(self.detalle(data,'fotos',1)['filas']),50)
        self.assertEqual(len(self.detalle(data,'fotos',2)['filas']),1)
        with self.assertRaises(ApiError):self.detalle(data,'desconocida')
        q.vence=timezone.now()-timedelta(seconds=1)
        with self.assertRaises(ApiError):self.detalle(data,'fotos')
    def test_html_ajax_caducidad_y_permiso_por_peticion(self):
        q=self.dataset();url='/portal/administrar/estadisticas/'+str(q.pk)+'/'
        with patch('midistri_portal.operadores.perfil_operador',return_value=fixture.PROFILE):
            r=self.client.get(url,{'distribuidora':20,'detalle':'fotos','parcial':'metrica'})
            self.assertEqual(r.status_code,200);self.assertIn('html',r.json());self.assertIn('Termo &lt;QA&gt;',r.json()['html']);self.assertNotIn('AJENO',r.json()['html'])
            self.assertEqual(r['Cache-Control'],'private, no-store')
            self.assertContains(self.client.get(url,{'distribuidora':20,'detalle':'fotos'}),'data-detalle-cerrar')
            self.assertEqual(self.client.get(url,{'distribuidora':20,'detalle':'invalid','parcial':'metrica'}).status_code,400)
        for changed in (dict(fixture.PROFILE,operador_id=999),dict(fixture.PROFILE,permisos=[])):
            with patch('midistri_portal.operadores.perfil_operador',return_value=changed):
                self.assertEqual(self.client.get(url,{'distribuidora':20,'detalle':'fotos','parcial':'metrica'}).status_code,403)
        ConsultaAnalitica.objects.filter(pk=q.pk).update(vence=timezone.now()-timedelta(seconds=1))
        with patch('midistri_portal.operadores.perfil_operador',return_value=fixture.PROFILE):
            r=self.client.get(url,{'distribuidora':20,'detalle':'fotos','parcial':'metrica'})
            self.assertEqual(r.status_code,403);self.assertIn('venc',r.json()['error'])

    def test_acceso_a_estadisticas_destacado_y_permisos_conservados(self):
        with patch('midistri_portal.operadores.perfil_operador',return_value=fixture.PROFILE):
            r=self.client.get('/portal/administrar/estadisticas/?distribuidora=20')
            self.assertContains(r,'class="button estadisticas-acceso"')

    def test_tabla_muestra_nombre_sin_lin_ni_vv(self):
        q=self.dataset()
        with patch('midistri_portal.operadores.perfil_operador',return_value=fixture.PROFILE):
            r=self.client.get('/portal/administrar/estadisticas/'+str(q.pk)+'/',{'distribuidora':20})
        self.assertContains(r,'>Visita sin pedido</a>')
