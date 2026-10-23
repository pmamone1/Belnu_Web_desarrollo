"""Compatibility of scheduled complete snapshots; never changes order history."""
from decimal import Decimal
from django.test import TestCase, override_settings
from .models import Distribuidora, Publicacion, PedidoLocal, Sincronizacion
from .services import aplicar_snapshot

@override_settings(URBAN_API_BASE='https://sistema7000.belnu.com.ar/midistri/api/')
class CatalogoAutomaticoCompatibilidadTests(TestCase):
    def datos(self):
        return {'version':1,'completo':True,'distribuidoras':[{'id':1,'nombre':'20 Belgrano'}],
            'publicaciones':[{'producto_id':141,'distribuidora_id':1,'nombre':'Alfajor','codigo':'ALM',
                'categoria':'Alimentos','precio':'100.00','pvp':'150.00','display':None,'imagenes':[],'multimedia':[]}]}
    def test_actualiza_fotos_categoria_y_precios_sin_cambiar_pedido_anterior(self):
        data=self.datos();aplicar_snapshot(data)
        order=PedidoLocal.objects.create(vendedor_id=98,distribuidora_id=1,
            datos={'items':[{'producto_id':141,'cantidad':2,'precio':'100.00'}]},respuesta={'total':'200.00'},estado='recibido')
        row=data['publicaciones'][0]
        row.update(nombre='Alfajor actualizado',categoria='Golosinas',precio='120.00',pvp='180.00',
            imagenes=[{'url':'https://sistema7000.belnu.com.ar/catalogo-imagenes/imagen1.webp'}])
        aplicar_snapshot(data)
        pub=Publicacion.objects.get()
        self.assertEqual((pub.nombre,pub.categoria,pub.precio,pub.pvp),('Alfajor actualizado','Golosinas',Decimal('120'),Decimal('180')))
        self.assertEqual(pub.imagenes,['https://sistema7000.belnu.com.ar/catalogo-imagenes/imagen1.webp'])
        order.refresh_from_db()
        self.assertEqual(order.datos,{'items':[{'producto_id':141,'cantidad':2,'precio':'100.00'}]})
        self.assertEqual(order.respuesta,{'total':'200.00'})
    def test_alta_repetida_y_futura_distribuidora_no_duplica(self):
        data=self.datos();aplicar_snapshot(data)
        data['distribuidoras'].append({'id':2,'nombre':'65 Barracas'})
        data['publicaciones'].append({**data['publicaciones'][0],'distribuidora_id':2})
        aplicar_snapshot(data);aplicar_snapshot(data)
        self.assertEqual(Publicacion.objects.filter(activa=True).count(),2)
        self.assertEqual(Distribuidora.objects.filter(activa=True).count(),2)
    def test_baja_conserva_fila_y_pedido(self):
        data=self.datos();aplicar_snapshot(data)
        order=PedidoLocal.objects.create(vendedor_id=98,distribuidora_id=1,datos={'total':'100.00'})
        data['publicaciones']=[]
        aplicar_snapshot(data)
        self.assertFalse(Publicacion.objects.get().activa)
        self.assertTrue(PedidoLocal.objects.filter(pk=order.pk).exists())
    def test_error_de_snapshot_no_desactiva_ultima_copia_valida(self):
        data=self.datos();aplicar_snapshot(data)
        previous=Sincronizacion.objects.get(pk=1).completada
        data['publicaciones'][0]['imagenes']=[{'url':'https://otro.example.test/privada.jpg'}]
        with self.assertRaises(ValueError):aplicar_snapshot(data)
        self.assertTrue(Publicacion.objects.get().activa)
        self.assertEqual(Sincronizacion.objects.get(pk=1).completada,previous)
