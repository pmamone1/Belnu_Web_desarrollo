"""Exercise the actual cumulative ZIP against tracked bytes of each admitted base."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
BUILDER=ROOT/'tools/paquete_integracion_v20.py'
APP_ROOT='belnuweb'
CRITICAL='midistri_portal/static/midistri_portal/pagina.css'

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj

class BasesRealesTests(unittest.TestCase):
    def test_zip_sobre_ambas_bases_reales_y_rechazo_de_diferencias(self):
        builder=module('package_real',BUILDER)
        with tempfile.TemporaryDirectory() as directory:
            temp=Path(directory);archive=temp/'actual.zip'
            with contextlib.redirect_stdout(io.StringIO()):builder.build(archive)
            bundle=temp/'bundle'
            with ZipFile(archive) as z:z.extractall(bundle)
            manifest=json.loads((bundle/'release_manifest.json').read_text(encoding='utf-8'))
            for index,base in enumerate(builder.BASES):
                with self.subTest(base=base):
                    root=temp/str(index)/APP_ROOT;root.mkdir(parents=True)
                    for name in ['manage.py']+[item['path'] for item in manifest['files']]:
                        previous=subprocess.run(['git','-c','core.fsmonitor=false','show',base+':'+name],cwd=str(ROOT),capture_output=True)
                        if previous.returncode==0:
                            dst=root/name;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(previous.stdout)
                    installer=module('installer_real_'+str(index),bundle/'instalar.py')
                    def invoke(apply=False):
                        args=['instalar.py','--root',str(root)]+(['--apply'] if apply else [])
                        with patch('sys.argv',args),patch.object(installer,'validar_entorno'),patch.object(installer,'run'),patch.object(installer,'control'),contextlib.redirect_stdout(io.StringIO()):
                            installer.main()
                    invoke()
                    self.assertFalse(list(root.parent.glob('respaldo*')))
                    before=(root/CRITICAL).read_bytes()
                    (root/CRITICAL).unlink()
                    with self.assertRaises(ValueError):invoke()
                    (root/CRITICAL).write_bytes(b'changed without review')
                    with self.assertRaises(ValueError):invoke()
                    (root/CRITICAL).write_bytes(before)
                    invoke(apply=True)
                    for item in manifest['files']:
                        self.assertEqual(hashlib.sha256((root/item['path']).read_bytes()).hexdigest(),item['sha256'])
                    print('BASE_REAL_OK',base,'preflight/apply, missing/changed core rejected')

if __name__=='__main__':unittest.main()
