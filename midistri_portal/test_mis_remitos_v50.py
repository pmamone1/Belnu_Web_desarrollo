from unittest.mock import patch

from django.test import TestCase, override_settings

from .client import ApiError
from .models import Distribuidora


@override_settings(MIDISTRI_LOGIN_CODIGO_ENABLED=False)
class MisRemitosTests(TestCase):
    def setUp(self):
        Distribuidora.objects.create(pk=20, nombre='Prueba')
        session = self.client.session
        session['midistri_token'] = 'a' * 43
        session.save()
        self.perfil = {'id':7, 'nombre':'Kiosco', 'distribuidora_id':20, 'distribuidora':'Prueba', 'linea':'12'}

    def test_presenta_filtros_referencia_y_pdf_privado(self):
        with patch('midistri_portal.remitos_views.identificar', return_value=self.perfil), \
             patch('midistri_portal.remitos_views.api') as api:
            api.return_value = {'remitos':[{'id':'pedido-23','nombre':'Mercadería','tipo':'pedido',
                'fecha':'2026-11-13','referencia':'MP-000009','origen_pedido':'MiDistri'}],
                'pagina':1,'anterior':None,'siguiente':2}
            r = self.client.get('/portal/remitos/', {'tipo':'pedido','desde':'2026-11-01'})
            self.assertContains(r, 'Mis remitos')
            self.assertContains(r, 'MP-000009')
            self.assertContains(r, 'Ver / imprimir PDF')
            api.assert_called_once_with('seller-remittances', token='a'*43,
                params={'tipo':'pedido','desde':'2026-11-01','hasta':'','pagina':'1'})
            api.return_value = b'%PDF-1.4'
            r = self.client.get('/portal/remitos/pedido-23/')
            self.assertIn('inline', r.headers['Content-Disposition'])
            self.assertIn('no-store',r.headers['Cache-Control'])
            r = self.client.get('/portal/remitos/pedido-23/', {'descargar':'1'})
            self.assertIn('attachment', r.headers['Content-Disposition'])
            api.side_effect = ApiError('No disponible',404)
            self.assertEqual(self.client.get('/portal/remitos/pedido-24/').status_code,404)

    def test_sin_acceso_no_llama_api_para_obtener_pdf(self):
        self.client.session.flush()
        with patch('midistri_portal.remitos_views.api') as api:
            self.assertEqual(self.client.get('/portal/remitos/pedido-23/').status_code,403)
            api.assert_not_called()
