from unittest.mock import patch

from django.test import TestCase, override_settings

from .models import Distribuidora


@override_settings(MIDISTRI_LOGIN_CODIGO_ENABLED=False)
class CuentaTests(TestCase):
    def setUp(self):
        Distribuidora.objects.create(pk=1, nombre='20 - Belgrano')
        sesion = self.client.session
        sesion['midistri_token'] = 'a' * 43
        sesion.save()
        self.perfil = dict(id=169, nombre='98', linea='1981', distribuidora_id=1,
                           distribuidora='20 - Belgrano', cuenta_disponible=True)

    def test_piloto_muestra_aviso_remito_y_protege_saldo(self):
        movimiento = dict(fecha='2026-11-14', concepto='Traslado a cuenta de la distribuidora',
                          referencia='PM-000286', consignado='0.00', vencido='-33000.00',
                          saldo_consignado='0.00', saldo_vencido='0.00',
                          remitos=[dict(id='pedido-9', tipo='pedido'), dict(id='https://ejemplo.test', tipo='pedido')])
        datos = dict(vendedor_id=169, distribuidora_id=1, consignado=0, vencido=0, total=0,
                     anterior_c=0, anterior_v=33000, pagina=1, anterior=None, siguiente=None,
                     aviso_traslado='El importe se cobra en tu cuenta con la distribuidora.',
                     requiere_revision=False, movimientos=[movimiento])
        with patch('midistri_portal.cuenta_views.identificar', return_value=self.perfil), \
             patch('midistri_portal.cuenta_views.api', return_value=datos) as api:
            r = self.client.get('/portal/estado-cuenta/', {'vendedor_id': 23})
            self.assertContains(r, 'se cobra en tu cuenta con la distribuidora')
            self.assertContains(r, '$ -33.000,00')
            self.assertContains(r, '/portal/remitos/pedido-9/')
            self.assertNotContains(r, 'https://ejemplo.test')
            self.assertNotContains(r, '20 - Belgrano')
            self.assertIn('no-store', r.headers['Cache-Control'])
            api.assert_called_once_with('seller-account', params={'pagina': '1'}, token='a' * 43)
            datos['vendedor_id'] = 23
            self.assertNotContains(self.client.get('/portal/estado-cuenta/'), 'PM-000286', status_code=503)

    def test_mismo_nombre_otros_perfiles_no_acceden_ni_ven_el_menu(self):
        with patch('midistri_portal.cuenta_views.identificar',
                   return_value=dict(self.perfil, id=170, cuenta_disponible=False)), \
             patch('midistri_portal.cuenta_views.api') as api:
            self.assertEqual(self.client.get('/portal/estado-cuenta/').status_code, 404)
            api.assert_not_called()
