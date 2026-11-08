"""Exercise the cumulative ZIP against tracked bytes of every supported base."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / 'tools/paquete_integracion_v43.py'
INSTALLER = ROOT / 'tools/instalar_release_midistri_v43.py'
INVENTORY = ROOT / 'tools/release_files_v43.json'
BASES = [
    'bacd089cfe2d5d14e971af7bdc439d92ba0764f5',
    '824f5da3b7f8fdb11a9b567e5ffa0c21f031ffe9',
    'f362520c247b23796d5b0846f1170b13ab1b5587',
    '14f14b6f89ad9eee099c0cde5cc297f698d491bc',
]
BASE = ('midistri_portal', '0014_dispositivo_recordado')
DESCRIPCION = ('midistri_portal', '0015_publicacion_descripcion')
ABASTECIMIENTO = ('midistri_portal', '0016_publicacion_abastecimiento')
MIGRACION_15 = 'midistri_portal/migrations/0015_publicacion_descripcion.py'
MIGRACION_16 = 'midistri_portal/migrations/0016_publicacion_abastecimiento.py'


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def copiar_base(base, root, names):
    for name in names:
        previous = subprocess.run(
            ['git', '-c', 'core.fsmonitor=false', 'show', base + ':' + name],
            cwd=str(ROOT), capture_output=True,
        )
        if previous.returncode == 0:
            dst = root / name
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(previous.stdout)


class PaqueteV43Tests(unittest.TestCase):
    def test_zip_y_aplicacion_simulada_sobre_bases_39_a_42(self):
        builder = module('package_real', BUILDER)
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            archive = temp / 'actual.zip'
            with patch.object(builder, 'MANIFEST_OUTPUT', temp / 'manifest.json'), contextlib.redirect_stdout(io.StringIO()):
                builder.build(archive, verificar_commit=False)
            bundle = temp / 'bundle'
            with ZipFile(archive) as z:
                self.assertIsNone(z.testzip())
                z.extractall(bundle)
            manifest = json.loads((bundle / 'release_manifest.json').read_text(encoding='utf-8'))
            self.assertEqual(manifest['required_migration'], list(BASE))
            self.assertEqual(manifest['migration_targets'], [list(DESCRIPCION), list(ABASTECIMIENTO)])
            self.assertEqual(manifest['production_installation'], 'pending')
            self.assertEqual(manifest['accepted_base_commits'], BASES)
            for index, base in enumerate(BASES):
                with self.subTest(base=base):
                    root = temp / str(index) / 'belnuweb'
                    root.mkdir(parents=True)
                    copiar_base(base, root, ['manage.py'] + [item['path'] for item in manifest['files']])
                    installer = module('installer_real_' + str(index), bundle / 'instalar.py')
                    commands = []
                    applied = {BASE}
                    original_migration = None
                    if base == BASES[-1]:
                        applied.add(DESCRIPCION)
                        original_migration = (root / MIGRACION_15).read_bytes().replace(b'\n', b'\r\n')
                        (root / MIGRACION_15).write_bytes(original_migration)

                    def simulated_run(_root, *args, capturar=False):
                        commands.append(args)
                        if capturar:
                            columns = []
                            if DESCRIPCION in applied:
                                columns.append('descripcion')
                            if ABASTECIMIENTO in applied:
                                columns.append('abastecimiento')
                            return 'ESTADO_PUBLICACION=' + json.dumps([sorted(applied), columns])
                        if args[0] == 'migrate':
                            applied.update({DESCRIPCION, ABASTECIMIENTO})

                    def invoke(apply=False):
                        args = ['instalar.py', '--root', str(root)] + (['--apply'] if apply else [])
                        with patch('sys.argv', args), patch.object(installer, 'validar_entorno'), \
                                patch.object(installer, 'run', side_effect=simulated_run), \
                                patch.object(installer, 'control') as control, contextlib.redirect_stdout(io.StringIO()):
                            installer.main()
                            if apply:
                                self.assertEqual([call[0][1] for call in control.call_args_list], ['stop', 'start'])
                            else:
                                control.assert_not_called()

                    invoke()
                    self.assertFalse(list(root.parent.glob('respaldo*')))
                    self.assertFalse(any(args[0] == 'migrate' for args in commands))
                    core = root / 'README.md'
                    before = core.read_bytes()
                    core.write_bytes(before.replace(b'\n', b'\r\n'))
                    invoke()
                    core.unlink()
                    with self.assertRaisesRegex(ValueError, 'versión instalada difiere'):
                        invoke()
                    core.write_bytes(b'changed without review')
                    with self.assertRaisesRegex(ValueError, 'versión instalada difiere'):
                        invoke()
                    core.write_bytes(before)
                    if original_migration is not None:
                        (root / MIGRACION_15).write_bytes(b'different applied migration')
                        with self.assertRaisesRegex(ValueError, 'migración aplicada difiere'):
                            invoke()
                        (root / MIGRACION_15).write_bytes(original_migration)
                    invoke(apply=True)
                    self.assertEqual([cmd for cmd in commands if cmd[0] == 'migrate'],
                                     [('migrate', *ABASTECIMIENTO, '--noinput')])
                    for item in manifest['files']:
                        data = (root / item['path']).read_bytes()
                        if item['path'] == MIGRACION_15 and original_migration is not None:
                            self.assertEqual(data, original_migration)
                        else:
                            self.assertEqual(hashlib.sha256(data).hexdigest(), item['sha256'])
                    backup, = root.parent.glob('respaldo*')
                    meta = json.loads((backup / 'restauracion.json').read_text(encoding='utf-8'))
                    self.assertEqual({tuple(m) for m in meta['migraciones_antes']},
                                     {BASE, DESCRIPCION} if original_migration is not None else {BASE})
                    print('BASE_REAL_OK', base, 'preflight y copia simulados')

    def test_inventario_acumulativo_excluye_datos_y_personalizacion(self):
        names = json.loads(INVENTORY.read_text(encoding='utf-8'))
        v42 = json.loads((ROOT / 'tools/release_files_v42.json').read_text(encoding='utf-8'))
        self.assertTrue(set(v42).issubset(names))
        self.assertEqual(len(names), len(set(names)))
        self.assertNotIn('templates/accounts/forgotPassword.html', names)
        self.assertEqual({name for name in names if '/migrations/' in name}, {MIGRACION_15, MIGRACION_16})
        for name in names:
            self.assertFalse(set(Path(name).parts) & {'tmp', 'output', 'media', 'venv', '__pycache__', '.git'})
            self.assertNotIn('settings.py', name)
            self.assertFalse(name.startswith('MANIFEST_'))

    def test_plan_solo_admite_0015_y_0016_hacia_adelante(self):
        installer = module('installer_plan', INSTALLER)
        installer.validar_plan([(*DESCRIPCION, False), (*ABASTECIMIENTO, False)])
        installer.validar_plan([(*ABASTECIMIENTO, False)])
        installer.validar_plan([])
        for unexpected in [(*DESCRIPCION, True), (*ABASTECIMIENTO, True), ('store', 'otra', False)]:
            with self.subTest(unexpected=unexpected), self.assertRaises(ValueError):
                installer.validar_plan([unexpected])

    def test_columnas_y_registro_de_migracion_deben_coincidir(self):
        installer = module('installer_schema', INSTALLER)
        installer.validar_esquema_publicacion({BASE}, set())
        installer.validar_esquema_publicacion({BASE, DESCRIPCION}, {'descripcion'})
        installer.validar_esquema_publicacion({BASE, DESCRIPCION, ABASTECIMIENTO}, {'descripcion', 'abastecimiento'})
        for applied, columns in [({BASE}, {'descripcion'}), ({BASE, DESCRIPCION}, set()),
                                 ({BASE, DESCRIPCION}, {'descripcion', 'abastecimiento'}),
                                 ({BASE, DESCRIPCION, ABASTECIMIENTO}, {'descripcion'}), (set(), set())]:
            with self.subTest(applied=applied, columns=columns), self.assertRaises(ValueError):
                installer.validar_esquema_publicacion(applied, columns)

    def test_restaurar_base42_conserva_0015_aplicada_y_quita_0016_pendiente(self):
        installer = module('installer_restore', INSTALLER)
        installer.validar_restauracion({BASE}, {BASE})
        with self.assertRaises(ValueError):
            installer.validar_restauracion({BASE, DESCRIPCION}, {BASE})
        with self.assertRaises(ValueError):
            installer.validar_restauracion({BASE, DESCRIPCION, ABASTECIMIENTO}, {BASE, DESCRIPCION})
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            root = temp / 'app'
            backup = temp / 'backup'
            (root / MIGRACION_15).parent.mkdir(parents=True)
            (root / MIGRACION_15).write_bytes(b'original migration')
            (root / MIGRACION_16).write_bytes(b'unapplied migration')
            (backup / 'files').mkdir(parents=True)
            meta = {
                'project': 'midistri-pedidos', 'release_version': '43', 'root': str(root),
                'migraciones_antes': [BASE, DESCRIPCION],
                'files': [{'path': MIGRACION_16, 'installed_sha256': installer.sha(b'unapplied migration'),
                           'original_sha256': None}],
            }
            (backup / 'restauracion.json').write_text(json.dumps(meta), encoding='utf-8')
            with patch.object(installer, 'estado_publicacion', return_value={BASE, DESCRIPCION}), \
                    patch.object(installer, 'comprobar_intervalos'), contextlib.redirect_stdout(io.StringIO()):
                installer.restore(backup, root)
            self.assertEqual((root / MIGRACION_15).read_bytes(), b'original migration')
            self.assertFalse((root / MIGRACION_16).exists())


if __name__ == '__main__':
    unittest.main()
