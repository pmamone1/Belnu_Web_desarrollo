from pathlib import Path
import posixpath
import re
import subprocess
import sys
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / 'belnuweb' / 'static'


class StaticAssetTests(unittest.TestCase):
    def test_django_manifest_resolves_literal_template_static_tags(self):
        program = textwrap.dedent('''
            from pathlib import Path
            import re
            import sys
            import tempfile
            from django.conf import settings
            root = Path(sys.argv[1])
            with tempfile.TemporaryDirectory() as target:
                settings.configure(
                    SECRET_KEY='static-manifest-test-only', DEBUG=False,
                    INSTALLED_APPS=['django.contrib.staticfiles'],
                    STATIC_URL='/static/', STATIC_ROOT=target,
                    STATICFILES_DIRS=[str(root / 'belnuweb' / 'static')],
                    STATICFILES_STORAGE='django.contrib.staticfiles.storage.ManifestStaticFilesStorage')
                import django
                django.setup()
                from django.core.management import call_command
                from django.contrib.staticfiles.storage import staticfiles_storage
                call_command('collectstatic', interactive=False, verbosity=0)
                pattern = r"{%\\s*static\\s+['\\\"]([^'\\\"]+)['\\\"]\\s*%}"
                for template in (root / 'templates').rglob('*.html'):
                    for asset in re.findall(pattern, template.read_text(encoding='utf-8', errors='replace')):
                        staticfiles_storage.url(asset)
        ''')
        result = subprocess.run([sys.executable, '-c', program, str(ROOT)],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_local_css_urls_resolve_to_existing_source_files(self):
        missing = []
        for css in STATIC.rglob('*.css'):
            text = css.read_text(encoding='utf-8', errors='replace')
            for url in re.findall(r'url\(\s*[\'\"]?([^\)\'\"\s]+)', text):
                if url.startswith(('data:', 'http:', 'https:', '/', '#')):
                    continue
                path = url.split('?', 1)[0].split('#', 1)[0]
                if path and not (css.parent / path).is_file():
                    missing.append((str(css.relative_to(ROOT)), url))
        self.assertEqual(missing, [], 'CSS references missing static source files')

    def test_template_static_tags_resolve_to_existing_source_files(self):
        missing = []
        for template in (ROOT / 'templates').rglob('*.html'):
            text = template.read_text(encoding='utf-8', errors='replace')
            for asset in re.findall(r'{%\s*static\s+[\'\"]([^\'\"]+)[\'\"]\s*%}', text):
                path = posixpath.normpath(asset)
                if not (STATIC / path).is_file():
                    missing.append((str(template.relative_to(ROOT)), asset))
        self.assertEqual(missing, [], 'Templates reference missing static source files')


if __name__ == '__main__':
    unittest.main()
