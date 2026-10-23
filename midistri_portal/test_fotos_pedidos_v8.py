from uuid import uuid4
from unittest.mock import patch
from django.test import TestCase, override_settings
from .models import Distribuidora, Publicacion, PedidoLocal

PHOTO='https://sistema7000.belnu.com.ar/catalogo-imagenes/abbeddef-abcd-4444-aaaa-123456789012/'+'a'*64+'/'
OTHER=PHOTO.replace('a'*64,'b'*64)

@override_settings(MIDISTRI_ENABLED=True, MIDISTRI_MULTIMEDIA_ENABLED=True)
class FotosPedidoTests(TestCase):
    def setUp(self):
        self.d=Distribuidora.objects.create(id=20,nombre='Belgrano')
        self.other=Distribuidora.objects.create(id=65,nombre='Barracas')
        self.product=Publicacion.objects.create(producto_id=314,distribuidora=self.d,nombre='Producto actual',precio=999,pvp=1500,
            multimedia=[dict(tipo='foto',url=PHOTO)],imagenes=[])
        Publicacion.objects.create(producto_id=314,distribuidora=self.other,nombre='Otro',precio=111,pvp=222,imagenes=[OTHER])
        self.profile=dict(id=7,nombre='Vendedor',linea='12',distribuidora_id=20,distribuidora='Belgrano')
        session=self.client.session;session['midistri_token']='x'*43;session['midistri_cart']={'314':2};session.save()
        self.order=PedidoLocal.objects.create(vendedor_id=7,distribuidora=self.d,estado='pendiente',
            datos={'items':[dict(producto_id=314,nombre='Producto histórico',cantidad=2,precio='100.00',pvp='150.00')]})
        self.remote=patch('midistri_portal.views.api',return_value=self.profile)
        self.remote.start();self.addCleanup(self.remote.stop)

    def test_carrito_foto_propia_y_total_vendedor(self):
        response=self.client.get('/portal/carrito/')
        self.assertContains(response,'src="'+PHOTO+'"')
        self.assertNotContains(response,OTHER)
        self.assertEqual(response.context['total'],1998)

    def test_detalle_foto_actual_sin_reescribir_pedido_historico(self):
        self.product.activa=False;self.product.save()
        before=self.order.datos.copy()
        response=self.client.get('/portal/pedido/'+str(self.order.pk)+'/')
        self.assertContains(response,'src="'+PHOTO+'"')
        self.assertNotContains(response,OTHER)
        self.assertContains(response,'Producto histórico')
        self.assertEqual(response.context['total'],200)
        self.order.refresh_from_db();self.assertEqual(self.order.datos,before)
        self.assertEqual(response.context['items'][0]['precio'],'100.00')

    def test_sin_foto_propia_no_toma_foto_de_otra_distribuidora(self):
        self.product.delete()
        response=self.client.get('/portal/pedido/'+str(self.order.pk)+'/')
        self.assertContains(response,'Foto pendiente')
        self.assertNotContains(response,OTHER)
        self.assertEqual(response.context['total'],200)

    @override_settings(MIDISTRI_MULTIMEDIA_ENABLED=False)
    def test_compatibilidad_imagenes_anteriores(self):
        self.product.imagenes=[PHOTO];self.product.save()
        self.assertContains(self.client.get('/portal/carrito/'),'src="'+PHOTO+'"')
        self.assertContains(self.client.get('/portal/pedido/'+str(self.order.pk)+'/'),'src="'+PHOTO+'"')

    def test_otro_vendedor_no_puede_ver_foto_ni_detalle(self):
        self.order.vendedor_id=99;self.order.save()
        self.assertEqual(self.client.get('/portal/pedido/'+str(self.order.pk)+'/').status_code,404)
