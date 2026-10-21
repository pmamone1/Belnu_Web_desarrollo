import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'tools' / 'prepare_environment.py'


class PrepareEnvironmentTests(unittest.TestCase):
    def run_preparation(self, root):
        self.assertTrue(SCRIPT.exists(), 'Environment preparation script is missing')
        return subprocess.run([sys.executable, str(SCRIPT), '--root', str(root)],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def test_preserves_live_credentials_and_backs_up_existing_environment(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            config = root / 'belnuweb'
            config.mkdir()
            (root / 'accounts').mkdir()
            (config / 'settings.py').write_text(
                "SECRET_KEY = 'live-test-secret'\n"
                "DATABASES = {'default': {'ENGINE': 'django.db.backends.mysql',"
                "'NAME':'live_db','USER':'live_user','PASSWORD':'live-db-password',"
                "'HOST':'localhost','PORT':'3306'}}\n")
            (root / 'accounts' / 'views.py').write_text(
                "EMAIL_HOST_USER='test@example.invalid'\n"
                "EMAIL_HOST_PASSWORD='live-mail-password'\n")
            original = 'UNRELATED=keep\nSECRET_KEY="obsolete"\n'
            (config / '.env').write_text(original)
            result = self.run_preparation(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            text = (config / '.env').read_text()
            pairs = dict(line.split('=', 1) for line in text.splitlines() if '=' in line)
            self.assertEqual(json.loads(pairs['SECRET_KEY']), 'live-test-secret')
            self.assertEqual(json.loads(pairs['DATABASE_PASSWORD']), 'live-db-password')
            self.assertEqual(json.loads(pairs['EMAIL_HOST_PASSWORD']), 'live-mail-password')
            self.assertIn('UNRELATED=keep', text)
            backups = list(config.glob('.env.backup-*'))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(), original)
            self.assertEqual(os.stat(config / '.env').st_mode & 0o777, 0o600)
            self.assertNotIn('live-test-secret', result.stdout + result.stderr)
            self.assertNotIn('live-db-password', result.stdout + result.stderr)
            self.assertNotIn('live-mail-password', result.stdout + result.stderr)

    def test_missing_live_values_leaves_existing_environment_unchanged(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            config = root / 'belnuweb'
            config.mkdir()
            (config / 'settings.py').write_text('DEBUG = True\n')
            (config / '.env').write_text('ORIGINAL=keep\n')
            result = self.run_preparation(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual((config / '.env').read_text(), 'ORIGINAL=keep\n')


if __name__ == '__main__':
    unittest.main()
