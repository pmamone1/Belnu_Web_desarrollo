from copy import deepcopy
from unittest.mock import patch

from django.test import SimpleTestCase, TestCase, override_settings

from .client import ApiError
from .contract import pedido_valido
from .models import Distribuidora, PedidoLocal
from .test_parciales_v6 import PERFIL, pedido


def modalidades():
    return [
        {'pedido_id': 101, 'modalidad': 'consignado', 'plazo_dias': 30,
         'fecha_confirmacion': '2026-11-01T10:00:00-03:00',
         'vencimientos': [{'salida_id': 201, 'fecha_devolucion': '2026-12-01'},
                          {'salida_id': 202, 'fecha_devolucion': '2026-12-03'}],
         'devoluciones_permitidas': True},
        {'pedido_id': 102, 'modalidad': 'firme', 'plazo_dias': 0,
         'fecha_confirmacion': '2026-11-01T10:00:00-03:00',
         'vencimientos': [], 'devoluciones_permitidas': False},
    ]


class ContratoModalidadesTests(SimpleTestCase):
    def test_modalidades_se_preservan_sin_referencias_mutables_al_dto(self):
        data = pedido(); data['pedidos'] = [101, 102]; data['modalidades_pedidos'] = modalidades()
        result = pedido_valido(data, PERFIL)
        self.assertEqual(result.get('modalidades_pedidos'), modalidades())
        data['modalidades_pedidos'][0]['vencimientos'][0]['fecha_devolucion'] = '2099-01-01'
        self.assertEqual(result['modalidades_pedidos'][0]['vencimientos'][0]['fecha_devolucion'], '2026-12-01')

    def test_historicos_sin_modalidad_y_lista_vacia_siguen_validos(self):
        self.assertNotIn('modalidades_pedidos', pedido_valido(pedido(), PERFIL))
        data = pedido(); data['pedidos'] = [101, 102]; data['modalidades_pedidos'] = []
        self.assertEqual(pedido_valido(data, PERFIL).get('modalidades_pedidos'), [])

    def test_dto_malformado_o_con_datos_internos_se_rechaza(self):
        invalid = [None, {}, 'consignado', [None]]
        mutations = [
            ('pedido_id', True), ('pedido_id', 0), ('pedido_id', '101'),
            ('modalidad', 'otro'), ('modalidad', '<script>'),
            ('plazo_dias', True), ('plazo_dias', -1), ('plazo_dias', '30'), ('plazo_dias', 3650), ('plazo_dias', 0),
            ('devoluciones_permitidas', False),
            ('fecha_confirmacion', '2026-11-01'), ('fecha_confirmacion', 'fecha'),
            ('devoluciones_permitidas', 'true'), ('vencimientos', None),
            ('proveedor', 'PRIVADO'), ('costo', '999.00'),
        ]
        for key, value in mutations:
            rows = modalidades(); rows[0][key] = value; invalid.append(rows)
        for mutation in ({'salida_id': True}, {'fecha_devolucion': '2026-02-30'},
                         {'fecha_devolucion': '2026-12-01T10:00:00'}, {'precio': '999'}):
            rows = modalidades(); rows[0]['vencimientos'][0].update(mutation); invalid.append(rows)
        rows = modalidades(); rows.append(deepcopy(rows[0])); invalid.append(rows)
        rows = modalidades(); rows[0]['vencimientos'].append(deepcopy(rows[0]['vencimientos'][0])); invalid.append(rows)
        rows = modalidades(); del rows[0]['plazo_dias']; invalid.append(rows)
        for value in invalid:
            with self.subTest(value=value):
                data = pedido(); data['pedidos'] = [101, 102]; data['modalidades_pedidos'] = value
                with self.assertRaises(ApiError): pedido_valido(data, PERFIL)

    def test_modalidades_requieren_pedidos_alcanzados_y_rechazan_firme_con_devolucion(self):
        for linked in (None, [], [101], [101, True], ['101', 102]):
            with self.subTest(linked=linked):
                data = pedido(); data['modalidades_pedidos'] = modalidades()
                if linked is not None: data['pedidos'] = linked
                with self.assertRaises(ApiError): pedido_valido(data, PERFIL)
        for mutation in ({'plazo_dias': 30}, {'devoluciones_permitidas': True},
                         {'vencimientos': [{'salida_id': 203, 'fecha_devolucion': '2026-12-01'}]}):
            data = pedido(); data['pedidos'] = [101, 102]; data['modalidades_pedidos'] = modalidades()
            data['modalidades_pedidos'][1].update(mutation)
            with self.subTest(mutation=mutation), self.assertRaises(ApiError): pedido_valido(data, PERFIL)

    def test_consignado_acepta_plazos_y_vencimiento_heredado_previo_a_confirmacion(self):
        for days in (7, 14, 21, 30):
            data = pedido(); data['pedidos'] = [101, 102, 103]; data['modalidades_pedidos'] = modalidades()
            data['modalidades_pedidos'][0]['plazo_dias'] = days
            data['modalidades_pedidos'][0]['vencimientos'][0]['fecha_devolucion'] = '2026-10-01'
            result = pedido_valido(data, PERFIL)
            self.assertEqual(result['modalidades_pedidos'][0]['vencimientos'][0]['fecha_devolucion'], '2026-10-01')


@override_settings(MIDISTRI_ENABLED=True)
class PantallaModalidadesTests(TestCase):
    def setUp(self):
        dist = Distribuidora.objects.create(id=20, nombre='Belgrano')
        self.data = pedido(); self.data['pedidos'] = [101, 102]; self.data['modalidades_pedidos'] = modalidades()
        self.local = PedidoLocal.objects.create(pk=self.data['id'], vendedor_id=7,
            distribuidora=dist, estado='ok', datos={'items': self.data['items']})
        session = self.client.session; session['midistri_token'] = 'a'*43; session.save()

    def response(self, path, failed=False):
        def remote(action, **kwargs):
            if action == 'profile': return PERFIL
            if failed: raise ApiError('Sin conexión')
            if action == 'orders': return {'pedidos': [deepcopy(self.data)]}
            return deepcopy(self.data)
        with patch('midistri_portal.views.api', side_effect=remote): return self.client.get(path)

    def test_historial_y_detalle_muestran_modalidad_y_cada_vencimiento(self):
        for path in ('/portal/pedidos/', '/portal/pedido/'+self.data['id']+'/'):
            with self.subTest(path=path):
                response = self.response(path)
                self.assertContains(response, 'Consignado')
                self.assertContains(response, '30 días')
                self.assertContains(response, '01/12/2026')
                self.assertContains(response, '03/12/2026')
                self.assertContains(response, 'En firme · no admite devolución de consignación')
                self.assertContains(response, 'La emisión del remito no confirma una deuda aplicada.')
                self.assertNotContains(response, 'salida_id')
                self.assertNotContains(response, 'pedido_id')
        self.local.refresh_from_db()
        self.assertEqual(self.local.respuesta.get('modalidades_pedidos'), modalidades())

    def test_sin_modalidad_conserva_presentacion_historica(self):
        for empty in (False, True):
            if empty: self.data['modalidades_pedidos'] = []
            else: self.data.pop('modalidades_pedidos', None)
            response = self.response('/portal/pedidos/')
            self.assertContains(response, 'Entregado')
            self.assertNotContains(response, 'Consignado')
            self.assertNotContains(response, 'La emisión del remito no confirma')

    def test_respuesta_invalida_no_reemplaza_snapshot_valido_y_se_ve_offline(self):
        self.response('/portal/pedidos/')
        self.data['modalidades_pedidos'][0]['proveedor'] = 'PRIVADO'
        response = self.response('/portal/pedido/'+self.data['id']+'/')
        self.assertContains(response, 'Última información guardada')
        self.assertContains(response, '01/12/2026')
        self.assertNotContains(response, 'PRIVADO')
        self.local.refresh_from_db()
        self.assertEqual(self.local.respuesta['modalidades_pedidos'], modalidades())
        response = self.response('/portal/pedidos/', failed=True)
        self.assertContains(response, '01/12/2026')
