from unittest.mock import patch
from django.test import TestCase
from django.db import connection,transaction,IntegrityError
from django.utils import timezone
from .models import Distribuidora,IntervaloAnalitico,ControlAnalitica
from .analitica_captura import cambiar_estado

class IntervalosPortablesTests(TestCase):
    def setUp(self):self.d=Distribuidora.objects.create(pk=20,nombre='20 - Belgrano')
    def test_no_requiere_indice_parcial_ignorado_por_mariadb(self):
        with patch.object(connection.features,'supports_partial_indexes',False):
            warnings=IntervaloAnalitico._check_constraints(databases=['default'])
        self.assertNotIn('models.W036',[w.id for w in warnings])
    def test_bloquea_dos_abiertos_y_conserva_varios_cerrados(self):
        self.assertIn('abierto_unico',{f.name for f in IntervaloAnalitico._meta.fields})
        a=IntervaloAnalitico.objects.create(distribuidora=self.d)
        with self.assertRaises(IntegrityError),transaction.atomic():IntervaloAnalitico.objects.create(distribuidora=self.d)
        a.hasta=timezone.now();a.save(update_fields=['hasta']);a.refresh_from_db();self.assertIsNone(a.abierto_unico)
        IntervaloAnalitico.objects.create(distribuidora=self.d,hasta=timezone.now())
        b=IntervaloAnalitico.objects.create(distribuidora=self.d);self.assertEqual(b.abierto_unico,1)
        with self.assertRaises(IntegrityError),transaction.atomic():IntervaloAnalitico.objects.filter(pk=b.pk).update(abierto_unico=None)
    def test_pausa_reactivacion_idempotente_y_otra_tienda(self):
        self.assertIn('abierto_unico',{f.name for f in IntervaloAnalitico._meta.fields})
        Distribuidora.objects.create(pk=61,nombre='61 - Recova')
        cambiar_estado(True);cambiar_estado(True)
        self.assertEqual(IntervaloAnalitico.objects.filter(abierto_unico=1).count(),2)
        cambiar_estado(False)
        self.assertEqual(IntervaloAnalitico.objects.filter(abierto_unico__isnull=True).count(),2)
        cambiar_estado(True);self.assertEqual(IntervaloAnalitico.objects.count(),4)
        self.assertTrue(ControlAnalitica.objects.get(pk=1).activa)

from unittest import skipUnless
from django.test import TransactionTestCase

@skipUnless(connection.vendor=='mysql','Concurrencia específica de MariaDB/MySQL')
class ConcurrenciaMariaTests(TransactionTestCase):
    def test_dos_sesiones_crean_un_solo_intervalo(self):
        from concurrent.futures import ThreadPoolExecutor
        from threading import Barrier
        from django.db import connections,close_old_connections
        Distribuidora.objects.create(pk=81,nombre='QA concurrencia')
        barrier=Barrier(2)
        def worker():
            close_old_connections()
            try:
                barrier.wait(timeout=10)
                row,created=IntervaloAnalitico.objects.get_or_create(distribuidora_id=81,hasta__isnull=True)
                return row.pk
            finally:connections['default'].close()
        with ThreadPoolExecutor(max_workers=2) as pool:ids=list(pool.map(lambda n:worker(),[1,2]))
        self.assertEqual(ids[0],ids[1]);self.assertEqual(IntervaloAnalitico.objects.filter(distribuidora_id=81).count(),1)
