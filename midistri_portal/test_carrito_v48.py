from copy import deepcopy
from unittest.mock import patch
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from . import pagina
from .models import Distribuidora, Publicacion, Tienda
from .test_operadores import PROFILE


@override_settings(MIDISTRI_ENABLED=True, MIDISTRI_ADMIN_ENABLED=True)
class CarritoPresentacionTests(TestCase):
    def setUp(self):
        self.tienda = Distribuidora.objects.create(pk=20, nombre='Belgrano')
        Tienda.objects.create(distribuidora=self.tienda)
        Publicacion.objects.create(distribuidora=self.tienda, producto_id=314,
                                   nombre='Pilas', precio=10, pvp=15,
                                   imagenes=[{'url': 'https://sistema7000.belnu.com.ar/pila.jpg'}])
        self.perfil = {'id': 7, 'nombre': 'Pablo', 'distribuidora_id': 20,
                       'distribuidora': 'Belgrano', 'linea': '12'}
        s = self.client.session
        s['midistri_token'] = 'a' * 43
        s.save()

    @patch('midistri_portal.views.api')
    def test_indicador_se_actualiza_y_carrito_explica_la_consignacion(self, api):
        api.return_value = self.perfil
        carrito = self.client.get('/portal/carrito/')
        self.assertContains(carrito, '0 unidades en el carrito')
        self.assertContains(carrito, 'La mercadería es consignada')
        self.assertContains(carrito, 'derecho a devolución, salvo casos especiales')
        self.assertNotContains(carrito, 'class="sticky"')
        self.client.post('/portal/cantidad/', {'producto': 314, 'cantidad': 3})
        self.assertContains(self.client.get('/portal/'), '3 unidades en el carrito')
        self.assertContains(self.client.get('/portal/carrito/'), '3 unidades en el carrito')
        self.client.post('/portal/cantidad/', {'producto': 314, 'cantidad': 0})
        self.assertContains(self.client.get('/portal/carrito/'), '0 unidades en el carrito')

    @patch('midistri_portal.views.api')
    def test_presentacion_privada_hasta_publicar_y_configurable_por_tienda(self, api):
        api.return_value = self.perfil
        operador = dict(PROFILE, permisos=['midistri.tienda_configurar'])
        otra = Distribuidora.objects.create(pk=65, nombre='Barracas')
        with patch.object(pagina, 'api', side_effect=lambda action, **kw:
                         operador if action == 'operator-profile' else {'ok': True, 'huella': kw['data']['huella']}):
            b = pagina.borrador_tienda(operador, 20, 'token')
            self.assertNotIn('presentacion_carrito', b.datos)
            self.assertEqual(pagina.validar_pagina(b.datos, 20), b.datos)
            data = deepcopy(b.datos)
            data['presentacion_carrito'] = {'activo': True, 'titulo': 'Comprá <local>',
                                             'texto': 'Texto de prueba'}
            with self.assertRaises(ValidationError):
                pagina.validar_pagina(dict(data, presentacion_carrito={'activo': 'false'}), 20)
            for activo in (True, False):
                data['presentacion_carrito']['activo'] = activo
                b = pagina.guardar_borrador(operador, 20, data, b.revision, str(uuid4()), 'token')
                if activo:
                    self.assertNotContains(self.client.get('/portal/carrito/'), 'Texto de prueba')
                firma = pagina.revisar_borrador(operador, 20, 'token')
                pagina.publicar_revision(operador, 20, firma, 'token')
                carrito = self.client.get('/portal/carrito/')
                if activo:
                    self.assertContains(carrito, 'Comprá &lt;local&gt;')
                    self.assertContains(carrito, 'Texto de prueba')
                else:
                    self.assertNotContains(carrito, 'Texto de prueba')
        self.assertNotIn('presentacion_carrito', pagina.pagina_publica(otra))
