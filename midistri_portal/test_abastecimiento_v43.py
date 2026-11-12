from copy import deepcopy
from unittest.mock import patch
from uuid import uuid4

from django.test import TestCase, override_settings

from .models import PedidoLocal, Publicacion, Sincronizacion, Tienda
from .services import aplicar_snapshot
from . import test_display_cero as fixture


@override_settings(MIDISTRI_ENABLED=True, URBAN_API_BASE='https://sistema7000.belnu.com.ar/midistri/api/')
class AbastecimientoTests(TestCase):
    proveedor = {
        'origen': 'proveedor', 'disponible': False,
        'actualizado': '2026-11-01T17:30:00Z', 'stock_local_disponible': 0,
    }
    perfil = {'id': 7, 'nombre': 'Pablo', 'distribuidora_id': 20,
              'distribuidora': '20 - Belgrano', 'linea': '12'}

    def datos(self, **cambios):
        data = fixture.DisplayCeroTests.datos(self)
        for p in data['publicaciones']:
            p['imagenes'] = [{'url': 'https://sistema7000.belnu.com.ar/catalogo-imagenes/fixture.jpg'}]
        data['publicaciones'][0]['abastecimiento'] = dict(self.proveedor, **cambios)
        data['publicaciones'][0]['indicadores'] = {
            'ranking': 1, 'entrega': '96', 'ultimas_unidades': False,
        }
        return data

    def iniciar_sesion(self, **datos):
        session = self.client.session
        session.update(dict(datos, midistri_token='a' * 43))
        session.save()

    def test_snapshot_persiste_el_dto_y_su_omision_lo_limpia(self):
        data = self.datos(actualizado=None)
        aplicar_snapshot(data)
        p = Publicacion.objects.get(distribuidora_id=20)
        self.assertEqual(getattr(p, 'abastecimiento', None), dict(self.proveedor, actualizado=None))
        del data['publicaciones'][0]['abastecimiento']
        aplicar_snapshot(data)
        p.refresh_from_db()
        self.assertEqual(p.abastecimiento, {})
        self.assertEqual(Publicacion.objects.get(distribuidora_id=65).abastecimiento, {})

    def test_enlace_y_categoria_kanji_del_catalogo_de_la_tienda(self):
        from urllib.parse import parse_qs, urlsplit

        data = self.datos()
        base = data['publicaciones'][0]
        base['nombre'] = 'Televisor del proveedor'
        base['categoria'] = 'Electrónica'
        base['clasificacion'] = {'categorias': ['Electrónica'], 'subcategoria': 'Televisores'}
        data['publicaciones'].append({**base, 'producto_id': 55, 'nombre': 'Electrónica local',
            'abastecimiento': {}, 'indicadores': {'ranking': 2, 'entrega': '96', 'ultimas_unidades': False}})
        data['publicaciones'][1]['nombre'] = 'Producto de otra tienda'
        aplicar_snapshot(data)

        catalogo = self.client.get('/portal/', {'distribuidora': 20, 'q': 'local', 'orden': 'ventas'})
        self.assertIn('Kanji', catalogo.context['categorias'])
        self.assertContains(catalogo, '<option value="Kanji">Kanji</option>', html=True)
        self.assertIn('Electrónica', catalogo.context['categorias'])
        self.assertContains(catalogo, 'catalogo-kanji.jpg')
        acceso = catalogo.context['catalogo_kanji_url']
        filtros = parse_qs(urlsplit(acceso).query, keep_blank_values=True)
        self.assertEqual(filtros['distribuidora'], ['20'])
        self.assertEqual(filtros['categoria'], ['Kanji'])
        self.assertEqual(filtros['q'], [''])
        self.assertEqual(filtros['orden'], ['recomendados'])
        filtrado = self.client.get(acceso)
        self.assertEqual([p.nombre for p in filtrado.context['productos']], ['Televisor del proveedor'])
        self.assertEqual(filtrado.context['subcategorias'], ['Televisores'])
        self.assertEqual(filtrado.context['productos'][0].categorias_catalogo, ['Electrónica', 'Kanji'])
        self.assertNotContains(filtrado, 'Electrónica local')
        self.assertNotContains(filtrado, 'Producto de otra tienda')
        otra = self.client.get('/portal/', {'distribuidora': 65})
        self.assertNotIn('Kanji', otra.context['categorias'])
        self.assertNotContains(otra, 'catalogo-kanji.jpg')

    def test_snapshot_rechaza_dtos_invalidos_sin_cambiar_copia(self):
        aplicar_snapshot(self.datos())
        before = list(Publicacion.objects.values())
        completada = Sincronizacion.objects.get(pk=1).completada
        for invalido in (
            None, [], '', {'origen': 'proveedor'}, dict(self.proveedor, origen='GFS'),
            dict(self.proveedor, costo=99), dict(self.proveedor, disponible=1),
            dict(self.proveedor, disponible='sí'), dict(self.proveedor, actualizado=1),
            dict(self.proveedor, actualizado='2026-11-01T17:30:00'),
            dict(self.proveedor, actualizado='2026-11-31T17:30:00Z'),
            dict(self.proveedor, stock_local_disponible=True),
            dict(self.proveedor, stock_local_disponible=-1),
            dict(self.proveedor, stock_local_disponible=2.5),
            dict(self.proveedor, stock_local_disponible=10**9 + 1),
        ):
            with self.subTest(invalido=invalido):
                data = deepcopy(self.datos())
                data['publicaciones'][0]['nombre'] = 'No debe guardarse'
                data['publicaciones'][1]['abastecimiento'] = invalido
                with self.assertRaisesRegex(ValueError, 'última copia válida'):
                    aplicar_snapshot(data)
                self.assertEqual(list(Publicacion.objects.values()), before)
                self.assertEqual(Sincronizacion.objects.get(pk=1).completada, completada)

    def test_catalogo_visible_sin_promesa_de_entrega_96hs(self):
        aplicar_snapshot(self.datos())
        r = self.client.get('/portal/?distribuidora=20')
        self.assertContains(r, 'Producto con presentación opcional')
        self.assertContains(r, 'Sin disponibilidad en proveedor')
        self.assertContains(r, '01/11/2026')
        self.assertNotContains(r, 'Entrega en 96 hs')

    def test_catalogo_separa_disponibilidad_del_proveedor_y_del_deposito(self):
        aplicar_snapshot(self.datos(disponible=True, stock_local_disponible=6))
        r = self.client.get('/portal/?distribuidora=20')
        self.assertContains(r, 'Disponible en proveedor')
        self.assertContains(r, 'Disponible en depósito')
        self.assertNotContains(r, 'Entrega en 96 hs')

    def test_vista_previa_usa_los_mismos_indicadores(self):
        from .editor_views import html_pagina
        from .pagina import inicial
        aplicar_snapshot(self.datos())
        tienda = Tienda.objects.create(distribuidora_id=20)
        html = html_pagina(inicial(tienda), tienda.distribuidora)
        self.assertIn('Sin disponibilidad en proveedor', html)
        self.assertNotIn('Entrega en 96 hs', html)

    @patch('midistri_portal.views.api')
    def test_no_puede_agregar_sin_stock_local_ni_en_proveedor(self, api):
        api.return_value = self.perfil
        aplicar_snapshot(self.datos())
        self.iniciar_sesion()
        r = self.client.get('/portal/')
        self.assertContains(r, 'Agregar / actualizar')
        self.assertRegex(r.content.decode(), r'<input name="cantidad"[^>]* disabled')
        self.assertRegex(r.content.decode(), r'<button[^>]* disabled[^>]*>Agregar / actualizar')
        r = self.client.post('/portal/cantidad/', {'producto': '314', 'cantidad': '2'}, follow=True)
        self.assertContains(r, 'no tiene disponibilidad para pedidos nuevos')
        self.assertEqual(self.client.session.get('midistri_cart', {}), {})

    @patch('midistri_portal.views.api')
    def test_puede_agregar_si_hay_stock_local_aunque_el_proveedor_no_tenga(self, api):
        api.return_value = self.perfil
        aplicar_snapshot(self.datos(stock_local_disponible=6))
        self.iniciar_sesion()
        self.client.post('/portal/cantidad/', {'producto': '314', 'cantidad': '2'})
        self.assertEqual(self.client.session['midistri_cart'], {'314': 2})

    @patch('midistri_portal.views.api')
    def test_no_agrega_mas_del_stock_local_sin_proveedor(self, api):
        api.return_value = self.perfil
        aplicar_snapshot(self.datos(stock_local_disponible=1))
        self.iniciar_sesion(midistri_cart={'314': 1})
        r = self.client.post('/portal/cantidad/', {'producto': '314', 'cantidad': '2'}, follow=True)
        self.assertContains(r, 'No hay suficientes unidades en depósito')
        self.assertEqual(self.client.session['midistri_cart'], {'314': 1})

    @patch('midistri_portal.views.api')
    def test_conserva_carrito_si_el_stock_local_bajo_tras_revisar(self, api):
        api.return_value = self.perfil
        aplicar_snapshot(self.datos(stock_local_disponible=2))
        self.iniciar_sesion(midistri_cart={'314': 2}, midistri_cart_id=str(uuid4()))
        self.client.get('/portal/carrito/')
        revision = self.client.session['midistri_revision']
        aplicar_snapshot(self.datos(stock_local_disponible=1))
        r = self.client.post('/portal/enviar/', {'revision': revision}, follow=True)
        self.assertContains(r, 'No hay suficientes unidades en depósito')
        self.assertFalse(PedidoLocal.objects.exists())
        self.assertEqual(self.client.session['midistri_cart'], {'314': 2})
        self.client.post('/portal/cantidad/', {'producto': '314', 'cantidad': '1', 'origen': 'carrito'})
        self.assertEqual(self.client.session['midistri_cart'], {'314': 1})

    @patch('midistri_portal.views.api')
    def test_rechaza_enviar_carrito_si_cambio_disponibilidad_tras_revisar(self, api):
        api.return_value = self.perfil
        aplicar_snapshot(self.datos(disponible=True))
        self.iniciar_sesion(midistri_cart={'314': 2}, midistri_cart_id=str(uuid4()))
        self.client.get('/portal/carrito/')
        revision = self.client.session['midistri_revision']
        aplicar_snapshot(self.datos())
        r = self.client.post('/portal/enviar/', {'revision': revision}, follow=True)
        self.assertContains(r, 'no tiene disponibilidad para pedidos nuevos')
        self.assertFalse(PedidoLocal.objects.exists())
        self.assertEqual(self.client.session['midistri_cart'], {'314': 2})
        self.assertContains(r, 'Quitar producto')
        self.client.post('/portal/cantidad/', {'producto': '314', 'cantidad': '0', 'origen': 'carrito'})
        self.assertEqual(self.client.session['midistri_cart'], {})

    @patch('midistri_portal.views.api')
    def test_repetir_post_de_pedido_existente_conserva_la_misma_referencia(self, api):
        api.return_value = self.perfil
        aplicar_snapshot(self.datos())
        pedido = PedidoLocal.objects.create(vendedor_id=7, distribuidora_id=20, estado='recibido')
        self.iniciar_sesion(midistri_cart_id=str(pedido.pk))
        r = self.client.post('/portal/enviar/', {})
        self.assertRedirects(r, '/portal/pedido/' + str(pedido.pk) + '/', fetch_redirect_response=False)
        pedido.refresh_from_db()
        self.assertEqual(pedido.estado, 'recibido')
        self.assertEqual(PedidoLocal.objects.count(), 1)
