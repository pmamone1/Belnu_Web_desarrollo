"""Import the real deployment settings with synthetic secrets and no database access."""
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
class ProductionSettingsTests(unittest.TestCase):
    def test_multimedia_flag_defaults_false_and_can_be_enabled(self):
        for enabled in (False,True):
            class Env:
                def __call__(self,key,default=None):
                    return default if default is not None else 'synthetic-test-only'
                def bool(self,key,default=False):
                    return enabled if key=='MIDISTRI_MULTIMEDIA_ENABLED' else default
                @staticmethod
                def read_env(*args,**kwargs):pass
            source=ROOT/'belnuweb/settings.py'
            namespace={'__file__':str(source),'__name__':'synthetic_deployment_settings'}
            with patch.dict('sys.modules',{'environ':SimpleNamespace(Env=Env)}):
                exec(compile(source.read_bytes(),str(source),'exec'),namespace)
            self.assertIs(namespace['MIDISTRI_MULTIMEDIA_ENABLED'],enabled)
            self.assertEqual(namespace['DATABASES']['default']['NAME'],'synthetic-test-only')
if __name__=='__main__':unittest.main()
