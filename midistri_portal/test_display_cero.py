"""A zero optional display in Urban must not block a complete store catalogue."""
from copy import deepcopy
from decimal import Decimal
from django.test import TestCase, override_settings
from .models import Distribuidora, Publicacion
from .services import aplicar_snapshot, validar_snapshot

@override_settings(URBAN_API_BASE='https://sistema7000.belnu.com.ar/midistri/api/')
class DisplayCeroTests(TestCase):
    def datos(self,display=0):
        return {'version':1,'completo':True,
            'distribuidoras':[{'id':20,'nombre':'20 - Belgrano'},{'id':65,'nombre':'65 - Barracas'}],
            'publicaciones':[{'producto_id':314,'distribuidora_id':did,
                'nombre':'Producto con presentación opcional','codigo':'SKU-314',
                'categoria':'Bazar','precio':'25000.00','pvp':'30000.00',
                'imagenes':[],'display':display} for did in (20,65)]}

    def test_cero_sin_presentacion_no_bloquea_20_y_65(self):
        try:count=aplicar_snapshot(self.datos())
        except ValueError as exc:self.fail('Display cero válido en Urban bloquea catálogo: '+str(exc))
        self.assertEqual(count,2)
        self.assertEqual(set(Publicacion.objects.values_list('distribuidora_id',flat=True)),{20,65})
        for p in Publicacion.objects.all():
            self.assertIsNone(p.display)
            self.assertEqual((p.precio,p.pvp),(Decimal('25000'),Decimal('30000')))

    def test_normalizar_no_modifica_snapshot_original(self):
        data=self.datos();original=deepcopy(data)
        try:ds,rows=validar_snapshot(data)
        except ValueError as exc:self.fail('El cero informativo debe poder leerse: '+str(exc))
        self.assertEqual(data,original)
        self.assertIsNone(rows[0][2]['display'])

    def test_presentaciones_positivas_y_nulas_se_conservan(self):
        for value in (None,1,3,6,12,24):
            with self.subTest(display=value):
                ds,rows=validar_snapshot(self.datos(value))
                self.assertEqual(rows[0][2]['display'],value)

    def test_booleanos_texto_negativos_y_fracciones_siguen_rechazados(self):
        d=Distribuidora.objects.create(pk=61,nombre='Catálogo anterior')
        anterior=Publicacion.objects.create(distribuidora=d,producto_id=1,nombre='Anterior',precio=10,pvp=20,imagenes=['https://sistema7000.belnu.com.ar/catalogo-imagenes/fixture.jpg'])
        for value in (False,True,'0',-1,0.5,[],{}):
            with self.subTest(display=value):
                with self.assertRaises(ValueError):aplicar_snapshot(self.datos(value))
                anterior.refresh_from_db();d.refresh_from_db()
                self.assertTrue(anterior.activa);self.assertTrue(d.activa)
                self.assertEqual(Publicacion.objects.count(),1)
