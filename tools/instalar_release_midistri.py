#!/usr/bin/env python3
"""Install one project's verified update; never touch the other installation."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime

PROJECT = 'midistri-pedidos'
MARKERS = {'urban-soft': 'sistema7000.settings', 'midistri-pedidos': 'belnuweb.settings'}

def sha(data):return hashlib.sha256(data).hexdigest()
def normalized(data):return sha(data.replace(b'\r\n', b'\n').rstrip(b'\n'))
def relative(name):
    p=PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts or '\\' in name or name!=str(p) or name.startswith('.'):
        raise ValueError('Ruta de paquete no permitida.')
    return Path(*p.parts)
def no_links(path):
    if any(p.is_symlink() for p in [path]+list(path.parents)):
        raise ValueError('No se reemplazan rutas con enlaces simbólicos: '+str(path))
def run(root,*args):
    subprocess.run([sys.executable,'manage.py']+list(args),cwd=str(root),check=True)

def restore(backup,root):
    meta=json.loads((backup/'restauracion.json').read_text(encoding='utf-8'))
    if meta['project']!=PROJECT or Path(meta['root'])!=root:raise ValueError('Respaldo de otro proyecto o carpeta.')
    for item in meta['files']:
        dst=root/relative(item['path']);no_links(dst)
        if dst.exists() and sha(dst.read_bytes())!=item['installed_sha256']:
            raise ValueError('El archivo cambió después de instalar. Revisar antes de restaurar: '+item['path'])
    for item in reversed(meta['files']):
        dst=root/relative(item['path']);src=backup/'files'/relative(item['path'])
        if src.exists():shutil.copy2(str(src),str(dst))
        elif dst.exists():dst.unlink()
    print('Código restaurado. Las migraciones/datos no se revierten. Respaldo: '+str(backup))

def main():
    os.umask(0o077)
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',required=True,help='Carpeta de ESTE proyecto; nunca la de la otra aplicación.')
    parser.add_argument('--apply',action='store_true',help='Aplicar después de verificar y respaldar la base.')
    parser.add_argument('--restore',help='Restaurar únicamente archivos desde un respaldo de este instalador.')
    opts=parser.parse_args();root=Path(opts.root).absolute();no_links(root)
    if not root.is_dir() or not (root/'manage.py').is_file() or MARKERS[PROJECT] not in (root/'manage.py').read_text(encoding='utf-8'):
        raise ValueError('Destino incorrecto. Este paquete es únicamente para '+PROJECT+'.')
    if opts.restore:
        restore(Path(opts.restore).absolute(),root);return
    bundle=Path(__file__).resolve().parent
    manifest=json.loads((bundle/'release_manifest.json').read_text(encoding='utf-8'))
    if manifest['project']!=PROJECT or manifest['schema']!=1:raise ValueError('Manifiesto de otro proyecto.')
    pending=[]
    for item in manifest['files']:
        rel=relative(item['path']);src=bundle/'payload'/rel;dst=root/rel
        no_links(src);no_links(dst)
        if not src.is_file() or sha(src.read_bytes())!=item['sha256']:raise ValueError('Paquete incompleto o alterado: '+item['path'])
        if dst.exists() and sha(dst.read_bytes())==item['sha256']:continue
        if item.get('base_normalized_sha256') and (not dst.is_file() or normalized(dst.read_bytes())!=item['base_normalized_sha256']):
            raise ValueError('La versión instalada difiere de la revisada: '+item['path']+'. Detenido sin modificar archivos. Compartir este mensaje para preparar la adaptación.')
        if item.get('new_code') and dst.exists():raise ValueError('Ya existe código diferente en '+item['path']+'. Detenido sin reemplazarlo.')
        pending.append(item)
    required=manifest['required_migration']
    code="from django.db import connection; from django.db.migrations.recorder import MigrationRecorder; assert "+repr(tuple(required))+" in MigrationRecorder(connection).applied_migrations(), 'Falta la migración base requerida: "+'/'.join(required)+"'"
    run(root,'shell','-c',code)
    print('DESTINO VERIFICADO: '+PROJECT+' — '+str(root))
    print('Versión base y paquete correctos. Archivos por actualizar: '+str(len(pending)))
    if not opts.apply:
        print('Solo comprobación. No se modificaron archivos ni base.');return
    backup=Path(tempfile.mkdtemp(prefix='respaldo_'+PROJECT.replace('-','_')+'_',dir=str(root.parent)))
    meta={'project':PROJECT,'root':str(root),'files':[]}
    for item in pending:
        rel=relative(item['path']);dst=root/rel;no_links(dst)
        if dst.exists():
            saved=backup/'files'/rel;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(str(dst),str(saved))
        meta['files'].append({'path':item['path'],'installed_sha256':item['sha256']})
    (backup/'restauracion.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
    print('Respaldo privado del código: '+str(backup))
    try:
        for item in pending:
            rel=relative(item['path']);dst=root/rel;dst.parent.mkdir(parents=True,exist_ok=True);no_links(dst)
            fd,temp=tempfile.mkstemp(prefix='.midistri_install_',dir=str(dst.parent))
            try:
                with os.fdopen(fd,'wb') as f:f.write((bundle/'payload'/rel).read_bytes())
                os.chmod(temp,0o644);os.replace(temp,str(dst))
            finally:
                if os.path.exists(temp):os.unlink(temp)
        run(root,'check')
        run(root,'makemigrations','--check','--dry-run')
        run(root,'migrate',manifest['app'],'--noinput')
        run(root,'collectstatic','--noinput')
    except Exception:
        print('La instalación no terminó. No se revierten datos automáticamente. Conservar salida y respaldo: '+str(backup),file=sys.stderr)
        raise
    (root/'tmp').mkdir(exist_ok=True);no_links(root/'tmp'/'restart.txt');(root/'tmp'/'restart.txt').touch()
    print('CÓDIGO INSTALADO: '+PROJECT+'. Falta configurar conexión y realizar prueba funcional antes de habilitar a vendedores.')
    print('Respaldo: '+str(backup))

if __name__=='__main__':
    try:main()
    except (ValueError,OSError,subprocess.CalledProcessError) as e:
        print('DETENIDO: '+str(e),file=sys.stderr);sys.exit(1)
