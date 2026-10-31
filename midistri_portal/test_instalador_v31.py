"""Real schema guard and static collection when restoring a code-only release."""
import importlib.util,json,sys,tempfile
from pathlib import Path
from unittest.mock import patch
from django.db import connection
from django.core.management import call_command
from django.test import TestCase,override_settings

class Restauracion31Tests(TestCase):
    def release(self):
        path=Path(__file__).resolve().parents[1]/'tools/instalar_release_midistri_v31.py'
        spec=importlib.util.spec_from_file_location('real_restore31',path)
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
    def test_guardia_real_acepta_base30_sin_modificar_esquema(self):
        from django.db.migrations.recorder import MigrationRecorder
        m=self.release();before=set(connection.introspection.table_names())
        applied=set(MigrationRecorder(connection).applied_migrations())
        self.assertIn(('midistri_portal','0014_dispositivo_recordado'),applied)
        def run(root,*args):exec(args[-1],{})
        with patch.object(m,'run',side_effect=run):m.comprobar_restauracion(Path('.'))
        self.assertEqual(set(connection.introspection.table_names()),before)
        self.assertEqual(set(MigrationRecorder(connection).applied_migrations()),applied)
    def test_guardia_real_rechaza_esquema_parcial(self):
        m=self.release();tables=connection.introspection.table_names()
        def run(root,*args):exec(args[-1],{})
        with patch.object(m,'run',side_effect=run),patch.object(connection.introspection,'table_names',return_value=[n for n in tables if n!='midistri_portal_dispositivorecordado']):
            with self.assertRaises(AssertionError):m.comprobar_restauracion(Path('.'))
    def test_restore_regenera_bytes_estaticos_antes_de_iniciar(self):
        m=self.release()
        with tempfile.TemporaryDirectory(prefix='qa-restore31-') as directory:
            folder=Path(directory);root=folder/'belnuweb';root.mkdir()
            (root/'manage.py').write_text('belnuweb.settings',encoding='ascii')
            rel='midistri_portal/static/midistri_portal/recordado.js'
            current=root/rel;current.parent.mkdir(parents=True);current.write_bytes(b'new31')
            backup=folder/'backup';old=backup/'files'/rel;old.parent.mkdir(parents=True);old.write_bytes(b'old30')
            (backup/'restauracion.json').write_text(json.dumps({'project':'midistri-pedidos','release_version':'31','root':str(root),
                'files':[{'path':rel,'installed_sha256':m.sha(b'new31'),'original_sha256':m.sha(b'old30')}]}),encoding='utf-8')
            served=folder/'served';served.mkdir();(served/'midistri_portal').mkdir();(served/'midistri_portal/recordado.js').write_bytes(b'new31')
            events=[]
            def run(root,*args):
                events.append(args[0])
                if args[0]=='collectstatic':call_command('collectstatic',*args[1:],verbosity=0)
            def control(root,action):events.append(action)
            with override_settings(STATICFILES_DIRS=[str(root/'midistri_portal/static')],STATIC_ROOT=str(served),STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage',STATICFILES_FINDERS=['django.contrib.staticfiles.finders.FileSystemFinder']),patch.object(m,'validar_entorno'),patch.object(m,'comprobar_restauracion'),patch.object(m,'run',side_effect=run),patch.object(m,'control',side_effect=control),patch('sys.argv',['instalar.py','--root',str(root),'--restore',str(backup)]):
                m.main()
            self.assertEqual(current.read_bytes(),b'old30')
            self.assertEqual((served/'midistri_portal/recordado.js').read_bytes(),b'old30')
            self.assertLess(events.index('collectstatic'),events.index('start'))
