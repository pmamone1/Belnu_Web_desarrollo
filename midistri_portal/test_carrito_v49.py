from unittest.mock import patch

from django.test import TestCase, override_settings

from .models import Distribuidora, Publicacion, Tienda


@override_settings(MIDISTRI_ENABLED=True)
class CarritoAjaxTests(TestCase):
    def setUp(self):
        tienda = Distribuidora.objects.create(pk=20, nombre='20 - Belgrano')
        Tienda.objects.create(distribuidora=tienda)
        otra = Distribuidora.objects.create(pk=65, nombre='65 - Barracas')
        self.producto(tienda, 314)
        self.producto(otra, 215)
        session = self.client.session
        session['midistri_token'] = 'a' * 43
        session.save()
        self.perfil = dict(id=7, nombre='Cerrutti', linea='1126 - Saavedra',
                           distribuidora_id=20, distribuidora='20 - Belgrano')

    def producto(self, tienda, id):
        return Publicacion.objects.create(
            distribuidora=tienda, producto_id=id, nombre='Pilas', precio=10, pvp=15, display=2,
            imagenes=[{'url': 'https://sistema7000.belnu.com.ar/pila.jpg'}])

    def cantidad(self, id, cantidad, origen='catalogo'):
        return self.client.post('/portal/cantidad/', dict(producto=id, cantidad=cantidad, origen=origen),
                                HTTP_ACCEPT='application/json')

    @patch('midistri_portal.views.api')
    def test_actualiza_sin_redirect_y_refresca_el_carrito_y_la_revision(self, api):
        api.return_value = self.perfil
        response = self.cantidad(314, 4)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['unidades'], 4)
        self.assertNotIn('carrito_html', response.json())
        carrito = self.client.get('/portal/carrito/')
        revision = carrito.context['revision']
        update = self.cantidad(314, 2, 'carrito').json()
        self.assertIn('Total a precio vendedor:', update['carrito_html'])
        self.assertNotEqual(self.client.session['midistri_revision'], revision)
        self.assertIn(self.client.session['midistri_revision'], update['carrito_html'])
        remove = self.cantidad(314, 0, 'carrito').json()
        self.assertEqual(remove['unidades'], 0)
        self.assertIn('Tu pedido está vacío.', remove['carrito_html'])
        self.assertNotIn('Enviar pedido', remove['carrito_html'])
        self.assertEqual(self.client.session['midistri_cart'], {})

    @patch('midistri_portal.views.api')
    def test_no_guarda_cantidad_invalida_ni_producto_ajeno(self, api):
        api.return_value = self.perfil
        self.cantidad(314, 4)
        for pid, qty in ((314, 3), (215, 2)):
            with self.subTest(pid=pid):
                response = self.cantidad(pid, qty)
                self.assertEqual(response.status_code, 400)
                self.assertEqual(self.client.session['midistri_cart'], {'314': 4})

    @patch('midistri_portal.views.api')
    def test_datos_visibles_y_carrito_en_el_menu(self, api):
        api.return_value = self.perfil
        for path in ('/portal/', '/portal/carrito/'):
            response = self.client.get(path)
            self.assertContains(response, 'class="portal-nav"')
            self.assertContains(response, 'class="button carrito-boton"')
            self.assertNotContains(response, '20 - Belgrano')
        self.assertContains(response, 'Cerrutti · Línea 1126 - Saavedra')
        from . import pagina
        original = pagina.pagina_publica
        for encabezado in ('MiDistri - 20–Belgrano', 'MiDistri - Pedidos Web - Dist. 20'):
            def pagina_guardada(tienda):
                data = original(tienda)
                data['mensajes']['encabezado'] = encabezado
                return data
            with patch.object(pagina, 'pagina_publica', side_effect=pagina_guardada):
                response = self.client.get('/portal/')
                self.assertNotContains(response, 'Belgrano')
                self.assertNotContains(response, 'Dist. 20')
                self.assertContains(response, 'MiDistri')

    @override_settings(MIDISTRI_LOGIN_CODIGO_ENABLED=True)
    @patch('midistri_portal.views.api')
    def test_ajax_con_prueba_de_pestana_aisla_carritos(self, api):
        from uuid import uuid4
        from .models import SesionVendedorPortal
        from .sesion_pestana import hash_texto
        api.return_value = self.perfil
        browser = 'cookie-privada-de-prueba'
        session = self.client.session
        session['midistri_browser'] = browser
        session.save()
        tabs = [SesionVendedorPortal.objects.create(pk=uuid4(), prueba_hash=hash_texto('a' * 64),
                navegador_hash=hash_texto(browser), token_urban='t' * 43, vendedor_id=7, distribuidora_id=20)
                for _ in range(2)]
        response = self.client.post('/portal/cantidad/', {'producto': 314, 'cantidad': 2},
                                    HTTP_ACCEPT='application/json', HTTP_X_MIDISTRI_TAB=str(tabs[0].pk),
                                    HTTP_X_MIDISTRI_TAB_PROOF='a' * 64)
        self.assertEqual(response.json()['unidades'], 2)
        for tab in tabs:
            tab.refresh_from_db()
        self.assertEqual(tabs[0].datos['midistri_cart'], {'314': 2})
        self.assertNotIn('midistri_cart', tabs[1].datos)

    def test_ajax_sin_sesion_no_edita_el_carrito(self):
        self.client.session.flush()
        response = self.cantidad(314, 2)
        self.assertEqual(response.status_code, 401)
        self.assertNotIn('midistri_cart', self.client.session)
