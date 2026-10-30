"""Forward-only migration QA on an explicitly isolated qa_ database."""
import os,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import django;django.setup()
from django.conf import settings
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.core.management import call_command
from uuid import UUID
cfg=settings.DATABASES['default']
assert cfg.get('HOST')=='127.0.0.1' and cfg['NAME'].startswith('qa_'),'Only isolated loopback QA databases'
base=('midistri_portal','0013_intervalo_unico_portable');target=('midistri_portal','0014_dispositivo_recordado')
executor=MigrationExecutor(connection)
assert base in executor.loader.applied_migrations,'Requires exact v29 migration base'
apps=executor.loader.project_state([base]).apps
Tab=apps.get_model('midistri_portal','SesionVendedorPortal')
ident=UUID('00000000-0000-0000-0000-000000000030')
Tab.objects.get_or_create(pk=ident,defaults={'prueba_hash':'a'*64,'navegador_hash':'b'*64,'token_urban':'synthetic-qa','vendedor_id':7,'distribuidora_id':1,'datos':{'midistri_cart':{'1':3}}})
def snapshot():
 return {name:list(apps.get_model('midistri_portal',name).objects.order_by('pk').values()) for name in ('ControlAnalitica','IntervaloAnalitico','EventoAnalitico','SesionVendedorPortal')}
before=snapshot()
call_command('migrate','midistri_portal',target[1],interactive=False,verbosity=0)
after=snapshot();assert before==after,'Existing rows changed'
from midistri_portal.models import SesionVendedorPortal,DispositivoRecordado
assert SesionVendedorPortal.objects.get(pk=ident).dispositivo_id is None
assert not DispositivoRecordado.objects.exists()
call_command('migrate','midistri_portal',target[1],interactive=False,verbosity=0)
assert snapshot()==before
print('Forward0013->0014 and repeat OK. Capture, intervals, events and old cart preserved; no device invented.')
