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
                           distribuidora='20 - Belgrano', cuenta_disponible=True, nombre_persona='Julia Prueba')

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
            self.assertContains(r, 'Hola, <strong>Julia Prueba</strong>')
            self.assertContains(r, 'Vendedor <strong>98</strong>')
            self.assertContains(r, 'se cobra en tu res. de cuenta con la distribuidora.')
            self.assertNotContains(r, 'Un saldo de $0')
            self.assertContains(r, '<caption>Evolución de saldos</caption>', html=True)
            self.assertContains(r, 'Saldo anterior a estos movimientos')
            self.assertContains(r, 'Saldo total acumulado')
            self.assertContains(r, '<td class="cuenta-total">$ 33.000,00</td>', html=True)
            self.assertContains(r, '$ -33.000,00')
            self.assertContains(r, '/portal/remitos/pedido-9/')
            self.assertContains(r, 'data-remito-pdf="ver"')
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

    def test_filtra_el_periodo_y_conserva_las_fechas_al_paginar_y_exportar(self):
        datos = dict(vendedor_id=169, distribuidora_id=1, consignado=300, vencido=0, total=300,
                     anterior_c=150, anterior_v=0, pagina=2, anterior=1, siguiente=3,
                     requiere_revision=False, movimientos=[])
        with patch('midistri_portal.cuenta_views.identificar', return_value=self.perfil), \
             patch('midistri_portal.cuenta_views.api', return_value=datos) as api:
            r = self.client.get('/portal/estado-cuenta/', {'desde': '2026-11-01', 'hasta': '2026-11-14', 'pagina': '2'})
        api.assert_called_once_with('seller-account', params={'desde': '2026-11-01', 'hasta': '2026-11-14',
                                                             'pagina': '2'}, token='a' * 43)
        self.assertContains(r, 'name="desde" value="2026-11-01"')
        self.assertContains(r, 'name="hasta" value="2026-11-14"')
        self.assertContains(r, '?desde=2026-11-01&amp;hasta=2026-11-14&amp;pagina=1')
        self.assertContains(r, '?desde=2026-11-01&amp;hasta=2026-11-14&amp;pagina=3')
        for formato in ('excel', 'pdf'):
            self.assertContains(r, f'?desde=2026-11-01&amp;hasta=2026-11-14&amp;formato={formato}')

    def test_descarga_privada_del_rango_completo_sin_pagina_ni_perfil_ajeno(self):
        excel_mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        formatos = (('excel', excel_mime, 'xlsx', b'PK\x03\x04test', {'binary_mime': excel_mime}),
                    ('pdf', 'application/pdf', 'pdf', b'%PDF-test', {'binary': True}))
        for formato, mime, extension, contenido, opciones in formatos:
            with self.subTest(formato=formato), \
                 patch('midistri_portal.cuenta_views.identificar', return_value=self.perfil), \
                 patch('midistri_portal.cuenta_views.api', return_value=contenido) as api:
                r = self.client.get('/portal/estado-cuenta/', {'hasta': '2026-11-14', 'formato': formato,
                                                              'pagina': '9', 'vendedor_id': '23'})
                self.assertEqual(r.status_code, 200)
                self.assertEqual(r.content, contenido)
                self.assertEqual(r.headers['Content-Type'], mime)
                self.assertEqual(r.headers['Content-Disposition'], f'attachment; filename="estado-cuenta.{extension}"')
                self.assertEqual(r.headers['Cache-Control'], 'private, no-store')
                self.assertEqual(r.headers['X-Content-Type-Options'], 'nosniff')
                api.assert_called_once_with('seller-account', params={'hasta': '2026-11-14', 'formato': formato},
                                            token='a' * 43, **opciones)
        with patch('midistri_portal.cuenta_views.identificar',
                   return_value=dict(self.perfil, cuenta_disponible=False)), \
             patch('midistri_portal.cuenta_views.api') as api:
            self.assertEqual(self.client.get('/portal/estado-cuenta/', {'formato': 'pdf'}).status_code, 404)
            api.assert_not_called()

    def test_rechaza_fechas_invalidas_antes_de_consultar_o_exportar(self):
        for filtros in ({'desde': '2026-11-31'}, {'desde': '2026-11-15', 'hasta': '2026-11-14'},
                        {'hasta': '20261114', 'formato': 'excel'}):
            with self.subTest(filtros=filtros), \
                 patch('midistri_portal.cuenta_views.identificar', return_value=self.perfil), \
                 patch('midistri_portal.cuenta_views.api') as api:
                r = self.client.get('/portal/estado-cuenta/', filtros)
                self.assertContains(r, 'role="alert"', status_code=400)
                self.assertIn('no-store', r.headers['Cache-Control'])
                api.assert_not_called()


    @override_settings(MIDISTRI_LOGIN_CODIGO_ENABLED=True)
    def test_inicio_de_sesion_desde_enlaces_directos(self):
        for url in ('/portal/remitos/', '/portal/estado-cuenta/'):
            r = self.client.get(url)
            self.assertContains(r, 'Comprobando tu acceso en esta pestaña')
            self.assertNotContains(r, 'Julia Prueba')
