import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

class InstallerTests(unittest.TestCase):
    def setUp(self):
        spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('instalar_release_midistri_v5.py'))
        self.module=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.module)
        guard=patch.object(self.module,'comprobar_restauracion',create=True);guard.start();self.addCleanup(guard.stop)
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/'belnuweb';self.root.mkdir()
        (self.root/'manage.py').write_text('belnuweb.settings')
        self.bundle=Path(self.temp.name)/'bundle';self.bundle.mkdir();(self.bundle/'payload').mkdir()
        (self.bundle/'instalar.py').write_text('')
        self.module.__file__=str(self.bundle/'instalar.py')
        self.path='belnuweb/settings.py';(self.root/'belnuweb').mkdir();(self.root/self.path).write_text('original\n')
        (self.bundle/'payload/belnuweb').mkdir();(self.bundle/'payload'/self.path).write_bytes(b'valor=1\n')
        self.manifest={'project':'midistri-pedidos','schema':1,'app':'midistri_portal','required_migration':['store','0017'], 'migration_targets':[],
            'files':[{'path':self.path,'sha256':self.module.sha(b'valor=1\n'),'base_normalized_sha256':self.module.normalized(b'original\n')}]}
        (self.bundle/'release_manifest.json').write_text(json.dumps(self.manifest))
    def invoke(self,*args):
        with patch('sys.argv',['instalar.py','--root',str(self.root)]+list(args)),patch.object(self.module,'run') as run,patch.object(self.module,'control',create=True),patch.object(self.module,'validar_entorno',create=True):
            self.module.main()
            return run.call_count
    def test_check_no_modifica_archivos(self):
        self.invoke();self.assertEqual((self.root/self.path).read_text(),'original\n')
        self.assertFalse(list(Path(self.temp.name).glob('respaldo*')))
    def test_version_distinta_no_copia_ni_respalda(self):
        (self.root/self.path).write_text('personalizado\n')
        with self.assertRaises(ValueError):self.invoke('--apply')
        self.assertEqual((self.root/self.path).read_text(),'personalizado\n')
        self.assertFalse(list(Path(self.temp.name).glob('respaldo*')))
    def test_otro_proyecto_se_rechaza(self):
        (self.root/'manage.py').write_text('sistema7000.settings')
        with self.assertRaises(ValueError):self.invoke('--apply')
    def test_aplicar_respalda_y_restaurar_recupera(self):
        self.assertEqual(self.invoke('--apply'),6)
        self.assertEqual((self.root/self.path).read_text(),'valor=1\n')
        backup=next(Path(self.temp.name).glob('respaldo*'))
        self.module.restore(backup,self.root)
        self.assertEqual((self.root/self.path).read_text(),'original\n')
    def test_paquete_alterado_no_se_aplica(self):
        (self.bundle/'payload'/self.path).write_text('corrupto')
        with self.assertRaises(ValueError):self.invoke('--apply')

    def test_entorno_equivocado_rechaza_antes_de_escribir(self):
        with patch('sys.argv',['instalar.py','--root',str(self.root),'--apply']),patch.object(self.module,'run'),patch.object(self.module,'control',create=True),patch('sys.prefix','/otro/entorno'),patch('sys.version_info',(3,12,0)):
            with self.assertRaises(ValueError):self.module.main()
        self.assertEqual((self.root/self.path).read_text(),'original\n')
        self.assertFalse(list(Path(self.temp.name).glob('respaldo*')))

    def test_app_de_migracion_equivocada_rechaza(self):
        self.manifest['app']='otra_aplicacion'
        (self.bundle/'release_manifest.json').write_text(json.dumps(self.manifest))
        with self.assertRaises(ValueError):self.invoke('--apply')
        self.assertEqual((self.root/self.path).read_text(),'original\n')

    def test_restaurar_copia_parcial_conserva_originales_y_borra_nuevos(self):
        self.invoke('--apply')
        backup=next(Path(self.temp.name).glob('respaldo*'))
        meta=json.loads((backup/'restauracion.json').read_text())
        (self.root/self.path).write_bytes((backup/'files'/self.path).read_bytes())
        meta['files'].append({'path':'nuevo.py','installed_sha256':self.module.sha(b'nuevo'),'original_sha256':None})
        (backup/'restauracion.json').write_text(json.dumps(meta))
        self.module.restore(backup,self.root)
        self.assertEqual((self.root/self.path).read_text(),'original\n')
        self.assertFalse((self.root/'nuevo.py').exists())

    def test_restaurar_rechaza_respaldo_alterado_antes_de_escribir(self):
        self.invoke('--apply')
        backup=next(Path(self.temp.name).glob('respaldo*'))
        (backup/'files'/self.path).write_text('alterado')
        with self.assertRaises(ValueError):self.module.restore(backup,self.root)
        self.assertEqual((self.root/self.path).read_text(),'valor=1\n')


    def test_restauracion_migrada_rechaza_sin_cambiar_archivos(self):
        self.invoke('--apply')
        backup=next(Path(self.temp.name).glob('respaldo*'))
        with patch.object(self.module,'comprobar_restauracion',side_effect=ValueError('corrección hacia adelante')):
            with self.assertRaises(ValueError):self.module.restore(backup,self.root)
        self.assertEqual((self.root/self.path).read_text(),'valor=1\n')

    def test_codigo_solo_rechaza_cualquier_migracion_pendiente(self):
        self.module.validar_plan([])
        with self.assertRaises(ValueError):self.module.validar_plan([('midistri_portal','0004_ajena',False)])
        with self.assertRaises(ValueError):self.module.validar_plan([('midistri_portal','0003_tienda_presentacion',True)])

    def test_instalacion_no_ejecuta_migrate(self):
        with patch('sys.argv',['instalar.py','--root',str(self.root),'--apply']),patch.object(self.module,'run') as run,patch.object(self.module,'control'),patch.object(self.module,'validar_entorno'):
            self.module.main()
        self.assertFalse(any('migrate' in call.args for call in run.call_args_list))

    def test_recuperacion_parcial_conserva_archivos_de_migraciones(self):
        self.invoke('--apply')
        backup=next(Path(self.temp.name).glob('respaldo*'))
        meta=json.loads((backup/'restauracion.json').read_text())
        rel=self.module.APPS[self.module.PROJECT]+'/migrations/0005_demo.py'
        dst=self.root/rel;dst.parent.mkdir(parents=True);dst.write_bytes(b'# migration')
        meta['files'].append({'path':rel,'installed_sha256':self.module.sha(b'# migration'),'original_sha256':None})
        (backup/'restauracion.json').write_text(json.dumps(meta))
        self.module.restore(backup,self.root)
        self.assertTrue(dst.is_file())


    def test_preflight_real_sin_targets_detecta_migracion_ajena_pendiente(self):
        from types import SimpleNamespace, MethodType
        from django.db.migrations.graph import MigrationGraph
        from django.db.migrations.migration import Migration
        from django.db.migrations.executor import MigrationExecutor
        graph=MigrationGraph()
        base=('midistri_portal','0003_tienda_presentacion')
        pending=('midistri_portal','0004_ajena')
        graph.add_node(base,Migration(base[1],base[0]))
        graph.add_node(pending,Migration(pending[1],pending[0]))
        graph.add_dependency(None,pending,base)
        loader=SimpleNamespace(graph=graph,applied_migrations={base:object()},
            load_disk=lambda:None,build_graph=lambda:None,check_consistent_history=lambda connection:None)
        executor=SimpleNamespace(loader=loader)
        executor.migration_plan=MethodType(MigrationExecutor.migration_plan,executor)
        (self.bundle/'instalar.py').write_bytes(Path(__file__).with_name('instalar_release_midistri_v5.py').read_bytes())
        def ejecutar(root,*args):exec(args[2],{})
        with patch.object(self.module,'run',side_effect=ejecutar),patch('django.db.migrations.loader.MigrationLoader',return_value=loader),patch('django.db.migrations.executor.MigrationExecutor',return_value=executor):
            with self.assertRaises(ValueError):self.module.comprobar_plan(self.root,self.bundle,{'migration_targets':[]})

if __name__=='__main__':unittest.main()
