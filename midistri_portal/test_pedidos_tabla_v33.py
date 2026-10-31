from copy import deepcopy
from types import SimpleNamespace as NS
from decimal import Decimal
from django.test import SimpleTestCase
from .test_parciales_v6 import pedido

class ResumenPedidoTests(SimpleTestCase):
    def resumen(self,data,estado=None):
        from .historial_presentacion import resumen_pedido
        return resumen_pedido(NS(respuesta=data,datos={},estado=estado or data['estado']))
    def test_parcial_usa_snapshot_no_catalogo(self):
        r=self.resumen(pedido())
        self.assertEqual(r['total_solicitado'],Decimal('250000'))
        self.assertEqual(r['total_vigente'],Decimal('150000'))
        row=r['filas'][0];self.assertEqual((row['solicitada'],row['aceptada'],row['faltante']),(10,6,4))
        self.assertTrue(r['finalizado']);self.assertEqual(row['codigo'],'T1')
    def test_revision_y_pendiente_no_inventan_entrega(self):
        data=pedido();data.pop('atencion');data['estado']='recibido'
        r=self.resumen(data);self.assertFalse(r['finalizado']);self.assertIsNone(r['filas'][0]['aceptada']);self.assertIsNone(r['filas'][0]['faltante'])
        data['revision_comercial']={'motivo':'Sin stock','cantidades':[{'producto_id':1,'cantidad_preparada':3}]}
        r=self.resumen(data);self.assertEqual(r['filas'][0]['aceptada'],3);self.assertEqual(r['filas'][0]['faltante'],7);self.assertFalse(r['finalizado'])
    def test_cancelacion_total_sin_atencion(self):
        data=pedido();data.pop('atencion');data['estado']='cancelado'
        r=self.resumen(data);self.assertEqual(r['total_vigente'],0);self.assertEqual(r['filas'][0]['faltante'],10)

    def test_remito_historico_sin_desglose_no_se_describe_como_pendiente(self):
        data=pedido();data.pop('atencion');data.pop('contrato_pedido')
        r=self.resumen(data)
        self.assertTrue(r['finalizado'])
        self.assertTrue(r['sin_desglose'])
        self.assertIsNone(r['filas'][0]['aceptada'])
        self.assertIsNone(r['total_vigente'])
        from django.template.loader import render_to_string
        from uuid import UUID
        from datetime import datetime
        order=NS(pk=UUID(int=1),respuesta=data,datos={},estado='emitido',resumen=r,creado=datetime(2026,10,1),referencia_publica='MP-HISTORICO')
        html=render_to_string('midistri_portal/pedidos.html',{'pedidos':[order]})
        self.assertIn('No informado',html)
        self.assertNotIn('La preparación todavía no está finalizada',html)
        self.assertIn('Ver / imprimir remito',html)
