import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

class InstallerTests(unittest.TestCase):
    def setUp(self):
        spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('instalar_release_midistri_v29.py'))
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
        self.manifest={'project':'midistri-pedidos','schema':1,'app':'midistri_portal','required_migration':['consignaciones','0121'], 'migration_targets':self.module.TARGETS,
            'files':[{'path':self.path,'sha256':self.module.sha(b'valor=1\n'),'base_normalized_sha256':self.module.normalized(b'original\n')}]}
        (self.bundle/'release_manifest.json').write_text(json.dumps(self.manifest))
    def invoke(self,*args):
        with patch('sys.argv',['instalar.py','--root',str(self.root)]+list(args)),patch.object(self.module,'run') as run,patch.object(self.module,'control',create=True),patch.object(self.module,'validar_entorno',create=True):
            self.module.main()
            return run.call_count
    def test_respaldo_invalido_no_detiene_aplicacion(self):
        backup=Path(self.temp.name)/'inexistente'
        with patch('sys.argv',['instalar.py','--root',str(self.root),'--restore',str(backup)]),patch.object(self.module,'validar_entorno'),patch.object(self.module,'control') as control:
            with self.assertRaises((ValueError,OSError)):self.module.main()
            control.assert_not_called()
    def test_check_no_modifica_archivos(self):
        self.invoke();self.assertEqual((self.root/self.path).read_text(),'original\n')
        self.assertFalse(list(Path(self.temp.name).glob('respaldo*')))
    def test_repetir_paquete_identico_conserva_archivos(self):
        self.invoke('--apply');first=(self.root/self.path).read_bytes()
        self.invoke('--apply');self.assertEqual((self.root/self.path).read_bytes(),first)

    def test_base_alternativa_revisada_se_admite_sin_aceptar_personalizaciones(self):
        self.manifest['files'][0]['accepted_base_normalized_sha256']=[self.module.normalized(b'alternativa')]
        (self.root/self.path).write_bytes(b'alternativa')
        (self.bundle/'release_manifest.json').write_text(json.dumps(self.manifest))
        self.invoke()
        self.assertEqual((self.root/self.path).read_bytes(),b'alternativa')

    def test_ausencia_revisada_de_base_antigua_es_admitida(self):
        self.manifest['files'][0]['accepted_base_normalized_sha256']=[self.module.normalized(b'original')]
        self.manifest['files'][0]['base_missing_allowed']=True
        (self.root/self.path).unlink()
        (self.bundle/'release_manifest.json').write_text(json.dumps(self.manifest))
        self.invoke()
        self.assertFalse((self.root/self.path).exists())

    def test_directorio_no_se_admite_como_archivo_ausente(self):
        self.manifest['files'][0]['base_missing_allowed']=True
        (self.root/self.path).unlink();(self.root/self.path).mkdir()
        (self.bundle/'release_manifest.json').write_text(json.dumps(self.manifest))
        with self.assertRaises(ValueError):self.invoke()

    def test_version_distinta_no_copia_ni_respalda(self):
        (self.root/self.path).write_text('personalizado\n')
        with self.assertRaises(ValueError):self.invoke('--apply')
        self.assertEqual((self.root/self.path).read_text(),'personalizado\n')
        self.assertFalse(list(Path(self.temp.name).glob('respaldo*')))
    def test_otro_proyecto_se_rechaza(self):
        (self.root/'manage.py').write_text('sistema7000.settings')
        with self.assertRaises(ValueError):self.invoke('--apply')
    def test_aplicar_respalda_y_restaurar_recupera(self):
        self.invoke('--apply') # The backup/content assertions below define the behaviour, not the number of read-only checks.
        self.assertEqual((self.root/self.path).read_text(),'valor=1\n')
        backup=next(Path(self.temp.name).glob('respaldo*'))
        self.module.restore(backup,self.root)
        self.assertEqual((self.root/self.path).read_text(),'original\n')
    def test_restore_conserva_migracion_anterior_ajena_a_entrega(self):
        self.invoke('--apply')
        backup=next(Path(self.temp.name).glob('respaldo*'))
        meta=json.loads((backup/'restauracion.json').read_text())
        app,name='midistri_portal','0009_pagina_tienda'
        rel=app+'/migrations/'+name+'.py'
        dst=self.root/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(b'# verified migration')
        meta['files'].append({'path':rel,'installed_sha256':self.module.sha(dst.read_bytes()),'original_sha256':None})
        (backup/'restauracion.json').write_text(json.dumps(meta))
        self.module.restore(backup,self.root)
        self.assertTrue(dst.exists())

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

    def test_plan_rechaza_otras_migraciones_y_reversiones(self):
        with self.assertRaises(ValueError):self.module.validar_plan([('auth','0001_initial',False)])
        with self.assertRaises(ValueError):self.module.validar_plan([('midistri_bridge','0005_operadores',True)])
        self.module.validar_plan([(app,name,False) for app,name in self.module.TARGETS])

    def test_preflight_fallido_no_reemplaza_codigo(self):
        def fail(root,*args):
            if 'PLAN_DE_MIGRACIONES' in ' '.join(args):raise ValueError('Plan extra')
        with patch('sys.argv',['instalar.py','--root',str(self.root),'--apply']),patch.object(self.module,'run',side_effect=fail),patch.object(self.module,'control'),patch.object(self.module,'validar_entorno'):
            with self.assertRaises(ValueError):self.module.main()
        self.assertEqual((self.root/self.path).read_text(),'original\n')
        self.assertFalse(list(Path(self.temp.name).glob('respaldo*')))


    def test_esquema_aditivo_identificado_antes_de_restaurar(self):
        self.assertEqual(self.module.TARGETS,[['midistri_portal','0013_intervalo_unico_portable']])
        self.assertEqual(self.module.DESTINATIONS,[['midistri_portal','0013_intervalo_unico_portable']])
        self.module.validar_restauracion({('consignaciones','0124_midistri_presentacion_campanas')})

    def test_cualquier_migracion_de_entrega_bloquea_restauracion(self):
        self.module.validar_restauracion(set())
        for target in self.module.TARGETS:
            with self.assertRaises(ValueError):self.module.validar_restauracion({tuple(target)})

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


    def test_guardia_restauracion_consulta_migraciones_aplicadas(self):
        spec=importlib.util.spec_from_file_location('guard19',Path(__file__).with_name('instalar_release_midistri_v29.py'))
        fresh=importlib.util.module_from_spec(spec);spec.loader.exec_module(fresh)
        with patch.object(fresh,'run') as run:
            fresh.comprobar_restauracion(self.root)
        self.assertEqual(run.call_count,1)
        self.assertEqual(run.call_args.args[1:3],('shell','-c'))
        self.assertIn('MigrationRecorder',run.call_args.args[-1])
        self.assertNotIn('0011_publicacion_ranking_analitica',run.call_args.args[-1])

    def test_apply_ejecuta_solo_hoja_revisada(self):
        with patch('sys.argv',['instalar.py','--root',str(self.root),'--apply']),patch.object(self.module,'run') as run,patch.object(self.module,'control'),patch.object(self.module,'validar_entorno'):
            self.module.main()
        destinations=[call.args[2:4] for call in run.call_args_list if len(call.args)>1 and call.args[1]=='migrate']
        self.assertEqual(destinations,[('midistri_portal','0013_intervalo_unico_portable')])

class IntervalGuardRecoveryTests(unittest.TestCase):
    setUp=InstallerTests.setUp
    invoke=InstallerTests.invoke
    def test_guardia_cambio_tras_stop_reinicia_sin_copiar(self):
        with patch('sys.argv',['instalar.py','--root',str(self.root),'--apply']),patch.object(self.module,'run'),patch.object(self.module,'validar_entorno'),patch.object(self.module,'comprobar_intervalos',side_effect=[None,ValueError('Duplicados nuevos')]),patch.object(self.module,'control') as control:
            with self.assertRaises(ValueError):self.module.main()
        self.assertEqual((self.root/self.path).read_text(),'original\n')
        self.assertEqual([c.args[1] for c in control.call_args_list],['stop','start'])

class IntervalPreflightTests(unittest.TestCase):
    def test_guardia_intervalos_solo_consulta(self):
        spec=importlib.util.spec_from_file_location('release29',Path(__file__).with_name('instalar_release_midistri_v29.py'))
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        with patch.object(m,'run') as run:m.comprobar_intervalos(Path('.'))
        command=run.call_args.args[-1];self.assertIn('n__gt=1',command)
        self.assertNotIn('.update(',command);self.assertNotIn('.delete(',command)
        self.assertIn('MigrationRecorder',command);self.assertIn('abierto_unico',command)

class PartialDDLRestoreTests(unittest.TestCase):
    def test_guardia_consulta_columna_aunque_migracion_no_figure_aplicada(self):
        spec=importlib.util.spec_from_file_location('release29_partial',Path(__file__).with_name('instalar_release_midistri_v29.py'))
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        with patch.object(m,'run') as run:m.comprobar_restauracion(Path('.'))
        code=run.call_args.args[-1]
        self.assertIn('get_table_description',code);self.assertIn('abierto_unico',code)

class MigrationRecoveryTests(unittest.TestCase):
    def test_planes_reales_en_cada_etapa_sin_reversion(self):
        from types import SimpleNamespace
        from django.db.migrations.graph import MigrationGraph
        from django.db.migrations import Migration
        from django.db.migrations.executor import MigrationExecutor
        spec=importlib.util.spec_from_file_location('release',Path(__file__).with_name('instalar_release_midistri_v29.py'))
        release=importlib.util.module_from_spec(spec);spec.loader.exec_module(release)
        graph=MigrationGraph()
        branches={}
        for app,name in release.TARGETS:branches.setdefault(app,[]).append((app,name))
        bases={'midistri_bridge':('midistri_bridge','0007_contactos_acceso'),'consignaciones':('consignaciones','0123_midistri_acceso_destinos'),'midistri_portal':('midistri_portal','0003_tienda_presentacion')}
        for app,chain in branches.items():
            keys=[bases[app]]+chain
            for key in keys:graph.add_node(key,Migration(key[1],key[0]))
            for parent,child in zip(keys,keys[1:]):graph.add_dependency(None,child,parent)
        with patch.object(release,'run') as run:release.comprobar_plan(Path('.'),Path('.'),{'migration_targets':release.TARGETS},overlay=False)
        statement=next(l for l in run.call_args.args[-1].splitlines() if l.startswith('plan=executor.migration_plan('))
        allkeys=set(graph.nodes);basekeys=set(bases[a] for a in branches)
        stages=[basekeys,allkeys]+[basekeys|set(chain[:i]) for chain in branches.values() for i in range(len(chain)+1)]
        for applied in stages:
            executor=MigrationExecutor.__new__(MigrationExecutor)
            executor.loader=SimpleNamespace(graph=graph,applied_migrations={key:graph.nodes[key] for key in applied},replace_migrations=False)
            scope={'executor':executor};exec(statement,scope);plan=scope['plan']
            self.assertFalse(any(back for m,back in plan))
            release.validar_plan([(m.app_label,m.name,back) for m,back in plan])
            self.assertEqual({(m.app_label,m.name) for m,back in plan},allkeys-applied)
class NoPendingMigrationsTests(unittest.TestCase):
    def test_preflight_rechaza_hoja_ajena_pendiente_antes_de_copiar(self):
        from types import SimpleNamespace
        from django.db.migrations.graph import MigrationGraph
        from django.db.migrations import Migration
        from django.db.migrations.executor import MigrationExecutor
        spec=importlib.util.spec_from_file_location('no_op_release',Path(__file__).with_name('instalar_release_midistri_v29.py'))
        release=importlib.util.module_from_spec(spec);spec.loader.exec_module(release)
        with patch.object(release,'run') as run:
            release.comprobar_plan(Path('.'),Path('.'),{'migration_targets':release.TARGETS},overlay=False)
        statement=next(line for line in run.call_args.args[-1].splitlines() if line.startswith('plan=executor.migration_plan('))
        graph=MigrationGraph()
        graph.add_node(('auth','0001_initial'),Migration('0001_initial','auth'))
        for app,name in release.TARGETS:graph.add_node((app,name),Migration(name,app))
        executor=MigrationExecutor.__new__(MigrationExecutor)
        executor.loader=SimpleNamespace(graph=graph,applied_migrations={},replace_migrations=False)
        scope={'executor':executor};exec(statement,scope)
        with self.assertRaises(ValueError):
            release.validar_plan([(m.app_label,m.name,back) for m,back in scope['plan']])
        executor.loader.applied_migrations={('auth','0001_initial'):graph.nodes[('auth','0001_initial')]}
        scope={'executor':executor};exec(statement,scope)
        release.validar_plan([(m.app_label,m.name,back) for m,back in scope['plan']])




if __name__=='__main__':unittest.main()
