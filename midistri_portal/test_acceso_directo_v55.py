from runpy import run_module
from types import ModuleType, SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock, patch


class ContadorCarritoTests(TestCase):
    def setUp(self):
        modelos = ModuleType('carts.models')
        modelos.Cart = Mock(DoesNotExist=LookupError)
        modelos.CartItem = Mock()
        vistas = ModuleType('carts.views')
        self.cart_id = vistas._cart_id = Mock(return_value='legacy')
        self.items = modelos.CartItem
        with patch.dict('sys.modules', {'carts.models': modelos, 'carts.views': vistas}):
            self.counter = run_module('carts.context_processors')['counter']

    def test_el_acceso_directo_al_portal_prescinde_del_usuario_y_carrito_legacy(self):
        for ruta in ('/portal/remitos/', '/portal/estado-cuenta/'):
            self.assertEqual(self.counter(SimpleNamespace(path=ruta)), {'cart_count': 0})
        self.cart_id.assert_not_called()

    def test_el_carrito_legacy_conserva_su_contador_original(self):
        self.items.objects.all.return_value.filter.return_value = [SimpleNamespace(quantity=3)]
        usuario = SimpleNamespace(is_authenticated=True)
        self.assertEqual(self.counter(SimpleNamespace(path='/cart/', user=usuario)), {'cart_count': 3})
        self.items.objects.all.return_value.filter.assert_called_once_with(user=usuario)
