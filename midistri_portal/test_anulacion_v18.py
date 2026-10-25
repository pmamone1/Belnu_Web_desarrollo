from copy import deepcopy
from django.test import SimpleTestCase
from .test_parciales_v6 import pedido,PERFIL
from .contract import pedido_valido
from .client import ApiError

class AnulacionContratoTests(SimpleTestCase):
    def test_anulacion_parcial_se_conserva_y_rechaza_metadatos_incoherentes(self):
        data=pedido();data['anulacion']={'completa':False,'motivo':'No se entregará esta parte','fecha':'2026-10-24T21:00:00+00:00'}
        self.assertEqual(pedido_valido(data,PERFIL)['anulacion'],data['anulacion'])
        long=deepcopy(data);long['anulacion']['motivo']='M'*1500
        self.assertEqual(len(pedido_valido(long,PERFIL)['anulacion']['motivo']),1500)
        for key,value in [('completa',True),('completa','no'),('motivo',None),('fecha','ayer')]:
            bad=deepcopy(data);bad['anulacion'][key]=value
            with self.assertRaises(ApiError):pedido_valido(bad,PERFIL)
