from copy import deepcopy
from uuid import uuid4
from unittest.mock import patch
from django.utils import timezone
from datetime import timedelta
from django.test import TestCase
from . import test_analitica_informes_v28 as fixture
from .models import ConsultaAnalitica
from .client import ApiError

class EstadosDesplegablesTests(TestCase):
    setUp=fixture.InformesAnaliticaTests.setUp
    modulos=fixture.InformesAnaliticaTests.modulos
    api=fixture.InformesAnaliticaTests.api
    consulta=fixture.InformesAnaliticaTests.consulta
    def dataset(self,n=6):
        q=self.consulta();orders=[]
        for i in range(n+2):
            o=deepcopy(self.orders[0]);o.update(id=str(uuid4()),referencia='MP-'+str(i),estado='cancelado' if i<n else 'emitido' if i==n else 'ok',atencion='cancelada' if i<n else 'total' if i==n else 'pendiente')
            if i==n:o.update(total_confirmado='100.00',unidades_confirmadas=1)
            orders.append(o)
        q.datos['pedidos']=orders;q.save(update_fields=['datos']);return q
    def data(self,q,params=None):
        from .analitica_informes import resultado
        from .analitica_estados import preparar
        data=resultado(q,params or {});preparar(data,params or {});return data
    def test_detalle_concilia_cada_grupo_sin_cambiar_resumen(self):
        d=self.data(self.dataset())
        self.assertEqual([r['pedidos'] for r in d['estados']],[6,1,1])
        for r in d['estados']:
            self.assertEqual(r['ordenes'].paginator.count,r['pedidos'])
            self.assertTrue(all(o['estado']==r['codigo_estado'] and o['atencion']==r['codigo_atencion'] for o in r['ordenes']))
        self.assertEqual(d['resumen']['pedidos'],8)
    def test_paginacion_50_preserva_filtros_y_abre_solo_grupo_elegido(self):
        d=self.data(self.dataset(51),{'distribuidora':'20','grupo_pedidos':'cancelado/cancelada','pagina_estado':'2','vendedor':'8','tienda':'20'})
        first=d['estados'][0];self.assertEqual(len(first['ordenes']),1);self.assertTrue(first['abierto']);self.assertFalse(d['estados'][1]['abierto'])
        self.assertIn('vendedor=8',first['anterior']);self.assertIn('grupo_pedidos=cancelado%2Fcancelada',first['anterior'])
        self.assertEqual(first['ordenes'].paginator.count,51)
    def test_ficha_vendedor_no_muestra_pedidos_de_otro(self):
        q=self.dataset();q.datos['pedidos'][0].update(vendedor_id=7,vendedor='Otro vendedor')
        q.save(update_fields=['datos']);d=self.data(q,{'vendedor':'8','tienda':'20'})
        self.assertEqual(d['estados'][0]['pedidos'],5)
        self.assertNotIn('Otro vendedor',str([list(e['ordenes']) for e in d['estados']]))
    def test_vista_permiso_caducidad_y_escape_se_conservan(self):
        q=self.dataset();q.datos['pedidos'][0]['vendedor']='<script>nombre</script>';q.save(update_fields=['datos'])
        url='/portal/administrar/estadisticas/'+str(q.pk)+'/'
        with patch('midistri_portal.operadores.perfil_operador',return_value=fixture.PROFILE):
            r=self.client.get(url,{'distribuidora':20});self.assertContains(r,'class="estado-pedidos"');self.assertContains(r,'&lt;script&gt;nombre&lt;/script&gt;');self.assertNotContains(r,'<script>nombre</script>');self.assertEqual(r['Cache-Control'],'private, no-store')
            self.assertEqual(self.client.get(url,{'distribuidora':20,'grupo_pedidos':'invalido'}).status_code,400)
        with patch('midistri_portal.operadores.perfil_operador',return_value=dict(fixture.PROFILE,operador_id=999)):
            self.assertEqual(self.client.get(url,{'distribuidora':20}).status_code,403)
        ConsultaAnalitica.objects.filter(pk=q.pk).update(vence=timezone.now()-timedelta(seconds=1))
        with patch('midistri_portal.operadores.perfil_operador',return_value=fixture.PROFILE):self.assertEqual(self.client.get(url,{'distribuidora':20}).status_code,403)
    def test_cero_pedidos_y_conciliacion_no_inventan_importes(self):
        q=self.dataset();q.datos['pedidos'][0].update(conciliacion=True,total_solicitado=None,total_confirmado=None);q.save(update_fields=['datos'])
        d=self.data(q);self.assertIsNone(d['estados'][0]['total_solicitado']);self.assertEqual(d['estados'][0]['ordenes'].paginator.count,6)
        q.datos['pedidos']=[];q.save(update_fields=['datos']);self.assertEqual(self.data(q)['estados'],[])
