import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

class InstallerTests(unittest.TestCase):
    def setUp(self):
        spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('instalar_release_midistri.py'))
        self.module=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.module)
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/'belnuweb';self.root.mkdir()
        (self.root/'manage.py').write_text('belnuweb.settings')
        self.bundle=Path(self.temp.name)/'bundle';self.bundle.mkdir();(self.bundle/'payload').mkdir()
        (self.bundle/'instalar.py').write_text('')
        self.module.__file__=str(self.bundle/'instalar.py')
        self.path='belnuweb/settings.py';(self.root/'belnuweb').mkdir();(self.root/self.path).write_text('original\n')
        (self.bundle/'payload/belnuweb').mkdir();(self.bundle/'payload'/self.path).write_bytes(b'valor=1\n')
        self.manifest={'project':'midistri-pedidos','schema':1,'app':'midistri_portal','required_migration':['store','0017'],
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
if __name__=='__main__':unittest.main()
