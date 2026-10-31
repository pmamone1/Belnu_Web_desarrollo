from datetime import datetime,timedelta,timezone as tz
from uuid import uuid4
from unittest.mock import patch
from django.test import TestCase
from .models import Distribuidora,IntervaloAnalitico,EventoAnalitico,IncidenciaAnalitica
from .client import ApiError

class ProductorTests(TestCase):
    def setUp(self):
        self.d=Distribuidora.objects.create(pk=20,nombre='Control')
        self.cut=datetime(2026,11,2,10,tzinfo=tz(timedelta(hours=-3)));self.start=self.cut-timedelta(days=7)
        IntervaloAnalitico.objects.create(distribuidora=self.d,desde=self.start-timedelta(days=1))
        self.config={'id':1,'revision':2,'distribuidoras':[20],'desde':self.start.isoformat(),'hasta':self.cut.isoformat()}
    def test_actividad_distinta_y_aislamiento(self):
        from .incentivos_preparacion import preparar_periodo
        visit=uuid4()
        for tipo in ('producto_consulta','foto_ampliada'):
            EventoAnalitico.objects.create(fecha=self.start+timedelta(hours=1),distribuidora_id=20,vendedor_id=98,vendedor='Control',visita=visit,tipo=tipo,producto_id=1,huella='x'*64)
        EventoAnalitico.objects.create(fecha=self.start+timedelta(hours=1),distribuidora_id=61,vendedor_id=8,vendedor='Ajeno',visita=uuid4(),tipo='producto_consulta',producto_id=9,huella='x'*64)
        result=preparar_periodo(self.config)
        self.assertEqual(result['cobertura'],'completa')
        self.assertEqual(len(result['actividad']),1)
        self.assertEqual(result['actividad'][0]['visitas'],1)
        self.assertEqual(result['actividad'][0]['productos'],[1])
    def test_cobertura_incompleta_no_se_envia_a_urban(self):
        from .incentivos_preparacion import preparar_periodo
        IncidenciaAnalitica.objects.create(distribuidora_id=20,desde=self.start,hasta=self.start+timedelta(minutes=1))
        with self.assertRaises(ApiError):preparar_periodo(self.config)
    def test_no_smtp_solo_preparacion_con_contrato(self):
        from .incentivos_preparacion import procesar
        def fake(action,**kw):
            if action=='weekly-incentives-due':return {'version':1,'configuraciones':[self.config]}
            self.assertEqual(action,'weekly-incentives-prepare')
            self.assertEqual(kw['data']['actividad']['cobertura'],'completa')
            return {'ejecucion':1,'destinatarios':2,'estado':'preparada'}
        with patch('midistri_portal.incentivos_preparacion.api',side_effect=fake) as api:
            result=procesar();self.assertEqual(result['preparadas'],1);self.assertEqual(api.call_count,2)

    def test_previa_se_transmite_sin_convertirse_en_campana(self):
        from .incentivos_preparacion import procesar
        config=dict(self.config,vista_previa=True)
        def fake(action,**kw):
            if action=='weekly-incentives-due':return {'version':1,'configuraciones':[config]}
            self.assertTrue(kw['data'].get('vista_previa'))
            return {'vista_previa':True,'estado':'previa_sin_envios'}
        with patch('midistri_portal.incentivos_preparacion.api',side_effect=fake):self.assertEqual(procesar()['preparadas'],1)
