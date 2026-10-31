"""Simulate a MariaDB partial-DDL interruption only in a dedicated QA DB."""
import importlib.util,sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import django;django.setup()
from django.conf import settings
from django.db import connection
from django.core.management import call_command
cfg=settings.DATABASES['default']
assert cfg.get('HOST')=='127.0.0.1' and cfg['NAME']=='qa_midistri30_partial','Dedicated QA DB only'
call_command('migrate','midistri_portal','0013_intervalo_unico_portable',interactive=False,verbosity=0)
with connection.cursor() as cursor:cursor.execute('CREATE TABLE IF NOT EXISTS midistri_portal_dispositivorecordado (id char(32) PRIMARY KEY)')
path=Path(__file__).with_name('instalar_release_midistri_v30.py')
spec=importlib.util.spec_from_file_location('qa_release30',path);release=importlib.util.module_from_spec(spec);spec.loader.exec_module(release)
for fn in (release.comprobar_intervalos,release.comprobar_restauracion):
 with patch.object(release,'run') as run:fn(Path('.'))
 try:exec(run.call_args.args[-1])
 except AssertionError:pass
 else:raise AssertionError('Partial schema must block both install and restore')
print('MariaDB partial device table rejected before copy; code-only restore also blocked. No production data.')
