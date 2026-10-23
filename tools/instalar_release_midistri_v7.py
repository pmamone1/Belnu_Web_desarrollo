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

APPS = {'urban-soft':'midistri_bridge','midistri-pedidos':'midistri_portal'}
VERSIONS = {'urban-soft':(3,10),'midistri-pedidos':(3,7)}
ROOTS = {'urban-soft':'sistema7000','midistri-pedidos':'belnuweb'}

def validar_entorno(root):
    version=VERSIONS[PROJECT]; app=ROOTS[PROJECT]
    expected=Path('/home/mcollini/virtualenv')/app/(str(version[0])+'.'+str(version[1]))
    if tuple(sys.version_info[:2])!=version or Path(sys.prefix).resolve()!=expected.resolve():
        raise ValueError('Entorno incorrecto. Usar '+str(expected/'bin/python')+'. No se modificó el proyecto.')
    if root.resolve()!=Path('/home/mcollini')/app:
        raise ValueError('Destino incorrecto para este proyecto.')

def control(root,accion):
    command=shutil.which('cloudlinux-selector')
    if not command:raise ValueError('No se encontró cloudlinux-selector; no se confirmó '+accion+'.')
    result=subprocess.run([command,accion,'--json','--interpreter','python','--user','mcollini',
        '--app-root',ROOTS[PROJECT]],capture_output=True,text=True,timeout=60)
    try:status=json.loads(result.stdout)
    except ValueError:raise ValueError('cPanel no confirmó '+accion+'.') from None
    if result.returncode or status.get('result')!='success':
        raise ValueError('cPanel no confirmó '+accion+'. Revisar Python App sin forzar la instalación.')

def sha(data):return hashlib.sha256(data).hexdigest()
def normalized(data):return sha(data.replace(b'\r\n', b'\n').rstrip(b'\n'))
def relative(name):
    p=PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts or '\\' in name or name!=str(p) or any(part.startswith('.') for part in p.parts):
        raise ValueError('Ruta de paquete no permitida.')
    return Path(*p.parts)
def no_links(path):
    if any(p.is_symlink() for p in [path]+list(path.parents)):
        raise ValueError('No se reemplazan rutas con enlaces simbólicos: '+str(path))

# Only the exact settings distributed in v7 may use this in-memory repair.
# It lets the read-only preflight inspect the interrupted install without changing files.
BROKEN_SETTINGS_HASH='b04855e7ee872edf34d91c8144f78dd0a185b8b7e7aa9305d0c8df8044763598'
BROKEN_SETTINGS_LINE="MIDISTRI_MULTIMEDIA_ENABLED = os.environ.get('MIDISTRI_MULTIMEDIA_ENABLED', 'False') == 'True'"
FIXED_SETTINGS_LINE="MIDISTRI_MULTIMEDIA_ENABLED = env.bool('MIDISTRI_MULTIMEDIA_ENABLED', default=False)"
PREFLIGHT_SETTINGS=None

def preparar_preflight(root):
    global PREFLIGHT_SETTINGS
    path=root/'belnuweb/settings.py'
    PREFLIGHT_SETTINGS=path if path.is_file() and normalized(path.read_bytes())==BROKEN_SETTINGS_HASH else None
    if PREFLIGHT_SETTINGS:
        print('Configuración v7 interrumpida reconocida; comprobación con corrección sólo en memoria.')

def comando_django(root,args):
    if PREFLIGHT_SETTINGS is None:return [sys.executable,'manage.py']+list(args)
    code="""import os,sys,types,hashlib
from pathlib import Path
path=Path(%r)
raw=path.read_bytes()
assert hashlib.sha256(raw.replace(b'\\r\\n',b'\\n').rstrip(b'\\n')).hexdigest()==%r, 'La configuración cambió; detenido'
source=raw.decode('utf-8')
assert source.count(%r)==1, 'Configuración no reconocida'
source=source.replace(%r,%r)
import belnuweb
module=types.ModuleType('belnuweb.settings');module.__file__=str(path)
exec(compile(source,str(path),'exec'),module.__dict__)
sys.modules['belnuweb.settings']=module;belnuweb.settings=module
os.environ['DJANGO_SETTINGS_MODULE']='belnuweb.settings'
from django.core.management import execute_from_command_line
execute_from_command_line(['manage.py']+%r)
""" % (str(PREFLIGHT_SETTINGS),BROKEN_SETTINGS_HASH,BROKEN_SETTINGS_LINE,BROKEN_SETTINGS_LINE,FIXED_SETTINGS_LINE,list(args))
    return [sys.executable,'-c',code]

def run(root,*args):
    subprocess.run(comando_django(root,args),cwd=str(root),check=True)

def restore(backup,root):
    comprobar_restauracion(root)
    no_links(backup)
    meta=json.loads((backup/'restauracion.json').read_text(encoding='utf-8'))
    if meta['project']!=PROJECT or Path(meta['root'])!=root:raise ValueError('Respaldo de otro proyecto o carpeta.')
    # Verify every original and both legal copy states before changing any file.
    for item in meta['files']:
        dst=root/relative(item['path']);src=backup/'files'/relative(item['path'])
        no_links(dst);no_links(src)
        original=item.get('original_sha256')
        if original is not None and (not src.is_file() or sha(src.read_bytes())!=original):
            raise ValueError('Respaldo incompleto o alterado: '+item['path'])
        if original is None and src.exists():
            raise ValueError('Respaldo inesperado: '+item['path'])
        current=sha(dst.read_bytes()) if dst.is_file() else None
        if current not in {item['installed_sha256'],original}:
            raise ValueError('El archivo cambió después de instalar. Revisar antes de restaurar: '+item['path'])
    for item in reversed(meta['files']):
        dst=root/relative(item['path']);src=backup/'files'/relative(item['path'])
        if item.get('original_sha256') is not None:
            dst.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(str(src),str(dst))
        elif dst.exists() and 'migrations' not in relative(item['path']).parts:dst.unlink()
    print('Código restaurado. Las migraciones/datos no se revierten. Respaldo: '+str(backup))


TARGETS=[['midistri_portal', '0004_sesion_pestana'], ['midistri_portal', '0005_configuracion_comercial'], ['midistri_portal', '0006_multimedia_publicacion'], ['midistri_portal', '0007_temas_promociones'], ['midistri_portal', '0008_recuperacion_promociones']]
DESTINATIONS=[['midistri_portal', '0008_recuperacion_promociones']]


def validar_restauracion(applied):
    if {tuple(t) for t in TARGETS}.intersection(applied):
        raise ValueError('Restauración bloqueada: hay migraciones de esta entrega aplicadas. Deshabilitar MIDISTRI_ADMIN_ENABLED en ambas aplicaciones y preparar una corrección hacia adelante; no revertir esquema ni históricos.')

def comprobar_restauracion(root):
    code="from django.db import connection; from django.db.migrations.recorder import MigrationRecorder; applied=MigrationRecorder(connection).applied_migrations(); assert not set("+repr([tuple(t) for t in TARGETS])+").intersection(applied), 'Restauración bloqueada: migraciones de esta entrega aplicadas. Requiere corrección hacia adelante, sin revertir esquema ni históricos.'"
    run(root,'shell','-c',code)

def validar_plan(plan):
    allowed={tuple(t) for t in TARGETS}
    if any((app,name) not in allowed or backward for app,name,backward in plan):
        raise ValueError('El plan incluye migraciones ajenas o reversiones; no se reemplazó código.')

def comprobar_plan(root,bundle,manifest,overlay=True):
    if manifest.get('migration_targets')!=TARGETS:raise ValueError('Objetivos de migración distintos de esta actualización.')
    additions=[(app,name,str(bundle/'payload'/app/'migrations'/(name+'.py'))) for app,name in TARGETS] if overlay else []
    code="""# PLAN_DE_MIGRACIONES: sólo lectura, antes de reemplazar archivos.
import importlib.util
from pathlib import Path
from django.db import connection
from django.db.migrations.loader import MigrationLoader
from django.db.migrations.executor import MigrationExecutor
spec=importlib.util.spec_from_file_location('release_plan_validation',%r)
release=importlib.util.module_from_spec(spec);spec.loader.exec_module(release)
loader=MigrationLoader(connection,load=False)
original=loader.load_disk
def load_disk():
    original()
    for app,name,path in %r:
        ms=importlib.util.spec_from_file_location('release_migration_'+app+'_'+name,path)
        module=importlib.util.module_from_spec(ms);ms.loader.exec_module(module)
        loader.disk_migrations[(app,name)]=module.Migration(name,app)
loader.load_disk=load_disk
loader.build_graph()
loader.check_consistent_history(connection)
unknown={(app,name) for app,name in loader.applied_migrations if app in ('consignaciones','midistri_bridge','midistri_portal','store') and (app,name) not in loader.graph.nodes}
allowed={('consignaciones','0015_alter_salidaproducto_options_proveedor_matricula_and_more')}
assert not unknown-allowed, 'La base registra migraciones desconocidas; no se reemplazó código'
executor=MigrationExecutor(connection);executor.loader=loader
# Only the final leaf is a destination. Ancestors remain the allowed whitelist;
# asking Django to target an applied ancestor would schedule a rollback.
plan=executor.migration_plan([tuple(t) for t in %r])
release.validar_plan([(m.app_label,m.name,backward) for m,backward in plan])
print('Plan exacto de migraciones verificado, sin modificar datos.')
""" % (str(Path(__file__).resolve()),additions,DESTINATIONS)
    run(root,'shell','-c',code)

def main():
    global PREFLIGHT_SETTINGS
    PREFLIGHT_SETTINGS=None
    os.umask(0o077)
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',required=True,help='Carpeta de ESTE proyecto; nunca la de la otra aplicación.')
    parser.add_argument('--apply',action='store_true',help='Aplicar después de verificar el paquete y el plan de migraciones.')
    parser.add_argument('--restore',help='Restaurar únicamente archivos desde un respaldo de este instalador.')
    opts=parser.parse_args();root=Path(opts.root).absolute();no_links(root)
    if not root.is_dir() or not (root/'manage.py').is_file() or MARKERS[PROJECT] not in (root/'manage.py').read_text(encoding='utf-8'):
        raise ValueError('Destino incorrecto. Este paquete es únicamente para '+PROJECT+'.')
    validar_entorno(root)
    if opts.restore:
        comprobar_restauracion(root)
        control(root,'stop')
        restore(Path(opts.restore).absolute(),root)
        control(root,'start')
        return
    bundle=Path(__file__).resolve().parent
    manifest=json.loads((bundle/'release_manifest.json').read_text(encoding='utf-8'))
    if manifest['project']!=PROJECT or manifest['schema']!=1 or manifest.get('app')!=APPS[PROJECT]:raise ValueError('Manifiesto de otro proyecto.')
    entries=manifest.get('files')
    if not isinstance(entries,list) or not 1<=len(entries)<=500:
        raise ValueError('Inventario de paquete inválido.')
    names=[item['path'] for item in entries]
    if len(names)!=len(set(names)):raise ValueError('Entradas repetidas en paquete.')
    pending=[]
    for item in manifest['files']:
        rel=relative(item['path']);src=bundle/'payload'/rel;dst=root/rel
        no_links(src);no_links(dst)
        if src.is_file() and src.stat().st_size>100*1024*1024:raise ValueError('Archivo demasiado grande.')
        if src.suffix=='.py' and src.is_file():compile(src.read_bytes(),str(src),'exec')
        if not src.is_file() or sha(src.read_bytes())!=item['sha256']:raise ValueError('Paquete incompleto o alterado: '+item['path'])
        if dst.exists() and sha(dst.read_bytes())==item['sha256']:continue
        additional=item.get('accepted_normalized_sha256',[])
        if not isinstance(additional,list) or len(additional)>2 or any(not isinstance(v,str) or len(v)!=64 for v in additional):
            raise ValueError('Huellas de recuperación inválidas.')
        accepted=set(additional)|{item.get('base_normalized_sha256')}
        current=normalized(dst.read_bytes()) if dst.is_file() else None
        if item.get('base_normalized_sha256') and current not in accepted:
            raise ValueError('La versión instalada difiere de la revisada: '+item['path']+'. Detenido sin modificar archivos. Compartir este mensaje para preparar la adaptación.')
        if item.get('new_code') and dst.exists() and current not in additional:raise ValueError('Ya existe código diferente en '+item['path']+'. Detenido sin reemplazarlo.')
        pending.append(item)
    preparar_preflight(root)
    required=manifest['required_migration']
    code="from django.db import connection; from django.db.migrations.recorder import MigrationRecorder; assert "+repr(tuple(required))+" in MigrationRecorder(connection).applied_migrations(), 'Falta la migración base requerida: "+'/'.join(required)+"'"
    if PROJECT=='urban-soft':
        code += "; import rest_framework, urllib3, hachoir, mutagen, pypdf"
        code += "; from django.db.migrations.loader import MigrationLoader; loader=MigrationLoader(connection)"
        code += "; unknown={name for app,name in MigrationRecorder(connection).applied_migrations() if app=='consignaciones' and (app,name) not in loader.graph.nodes}"
        code += "; assert not (unknown-{'0015_alter_salidaproducto_options_proveedor_matricula_and_more','0124_midistri_presentacion_campanas'}), 'Migraciones desconocidas: detener sin copiar'"
    else:
        code += "; import requests"
    run(root,'shell','-c',code)
    comprobar_plan(root,bundle,manifest,overlay=True)
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
        meta['files'].append({'path':item['path'],'installed_sha256':item['sha256'],
            'original_sha256':sha(dst.read_bytes()) if dst.is_file() else None})
    (backup/'restauracion.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
    print('Respaldo privado del código: '+str(backup))
    control(root,'stop')
    try:
        for item in pending:
            rel=relative(item['path']);dst=root/rel;dst.parent.mkdir(parents=True,exist_ok=True);no_links(dst)
            fd,temp=tempfile.mkstemp(prefix='.midistri_install_',dir=str(dst.parent))
            try:
                with os.fdopen(fd,'wb') as f:f.write((bundle/'payload'/rel).read_bytes())
                os.chmod(temp,0o644);os.replace(temp,str(dst))
            finally:
                if os.path.exists(temp):os.unlink(temp)
        PREFLIGHT_SETTINGS=None
        run(root,'check')
        run(root,'makemigrations','--check','--dry-run')
        comprobar_plan(root,bundle,manifest,overlay=False)
        for app,name in DESTINATIONS:run(root,'migrate',app,name,'--noinput')
        run(root,'collectstatic','--noinput')
    except Exception:
        print('La instalación no terminó. No se revierten datos automáticamente. Conservar salida y respaldo: '+str(backup),file=sys.stderr)
        raise
    (root/'tmp').mkdir(exist_ok=True);no_links(root/'tmp'/'restart.txt');(root/'tmp'/'restart.txt').touch()
    control(root,'start')
    print('CÓDIGO INSTALADO: midistri-pedidos v7 r2. Falta activar funciones coordinadamente y verificar en el sitio. No se enviaron campañas ni se cambiaron conexiones, catálogo o venv.')
    print('Respaldo: '+str(backup))

if __name__=='__main__':
    try:main()
    except (ValueError,OSError,subprocess.CalledProcessError) as e:
        print('DETENIDO: '+str(e),file=sys.stderr);sys.exit(1)
