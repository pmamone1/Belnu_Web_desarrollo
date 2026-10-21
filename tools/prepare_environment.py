"""Preserve private configuration BEFORE replacing the existing cPanel code.

Reads Python literals with ast.literal_eval; never imports application code.
Does not modify settings, database, migrations, uploads, or service state.
"""
import argparse
import ast
from datetime import datetime
import json
import os
from pathlib import Path
import tempfile


def literal_values(path, wanted):
    if not path.exists():
        return {}
    tree = ast.parse(path.read_text(encoding='utf-8-sig'))
    result = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in wanted:
                try:
                    value = ast.literal_eval(node.value)
                except (ValueError, TypeError):
                    continue
                if target.id in result and result[target.id] != value:
                    raise ValueError('Conflicting configuration assignments')
                result[target.id] = value
    return result


def write_private(path, content):
    descriptor, temporary = tempfile.mkstemp(prefix='.config-', dir=str(path.parent))
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as output:
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, str(path))
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def prepare(root):
    config = root / 'belnuweb'
    settings = literal_values(config / 'settings.py', {'SECRET_KEY', 'DATABASES', 'PASSWORD_GMAIL'})
    database = settings.get('DATABASES', {}).get('default', {})
    if not settings.get('SECRET_KEY') or any(key not in database for key in ('NAME', 'USER', 'PASSWORD', 'HOST', 'PORT')):
        raise ValueError('Missing live literal configuration; no files were changed')
    values = {'SECRET_KEY': settings['SECRET_KEY']}
    for key in ('NAME', 'USER', 'PASSWORD', 'HOST', 'PORT'):
        values['DATABASE_' + key] = str(database[key])
    for folder in ('accounts', 'orders'):
        mail = literal_values(root / folder / 'views.py', {'EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD'})
        for key, value in mail.items():
            if key in values and values[key] != value:
                raise ValueError('Conflicting live mail configuration; no files were changed')
            values[key] = value
    if not values.get('EMAIL_HOST_USER') or not values.get('EMAIL_HOST_PASSWORD'):
        raise ValueError('Missing live mail configuration; no files were changed')
    if 'PASSWORD_GMAIL' in settings:
        values['PASSWORD_GMAIL'] = settings['PASSWORD_GMAIL']
    target = config / '.env'
    original = target.read_text(encoding='utf-8') if target.exists() else ''
    lines = [line for line in original.splitlines()
             if line.split('=', 1)[0].strip() not in values]
    lines.extend(key + '=' + json.dumps(str(value), ensure_ascii=False)
                 for key, value in sorted(values.items()))
    content = '\n'.join(lines) + '\n'
    if original:
        backup = config / ('.env.backup-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
        write_private(backup, original)
    write_private(target, content)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    args = parser.parse_args()
    try:
        prepare(args.root.resolve())
    except (ValueError, OSError, SyntaxError):
        raise SystemExit('Preparation failed; inspect the existing configuration locally. No private values were printed.')
    print('Private configuration prepared. Keep .env and backups outside Git. Application code and database unchanged.')
