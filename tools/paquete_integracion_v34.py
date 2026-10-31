"""Build a reviewed source-only package; never walk media, databases or virtualenvs."""
import argparse, ast, hashlib, json, subprocess
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
ROOT=Path(__file__).resolve().parents[1]
BASE='a6fd563c8708d596a7b27bbf0afb81892dad8bea'
BASES=['a6fd563c8708d596a7b27bbf0afb81892dad8bea', '5ca742b64783d0ba74c0c689c27bd5b44a58b5bf']
PROJECT="midistri-pedidos"
APP="midistri_portal"
VERSION='34'
ZIP_NAME='midistri_pedidos_v34_analitica_detalle.zip'
INSTALLER='tools/instalar_release_midistri_v34.py'
REQUIRED=['midistri_portal','0014_dispositivo_recordado']
FILELIST='tools/release_files_v34.json'
def digest(data):return hashlib.sha256(data).hexdigest()
def normalized(data):return digest(data.replace(b'\r\n',b'\n').rstrip(b'\n'))
def build(output):
    names=json.loads((ROOT/FILELIST).read_text(encoding='utf-8'))
    if len(names)!=len(set(names)):raise ValueError('Inventario duplicado.')
    for commit in BASES:
        subprocess.run(['git','-c','core.fsmonitor=false','cat-file','-e',commit+'^{commit}'],cwd=str(ROOT),check=True)
    files=[];payload={}
    for name in names:
        path=Path(name)
        if path.is_absolute() or '..' in path.parts or any(part.startswith('.') for part in path.parts):
            raise ValueError('Ruta no permitida.')
        if any(part.lower() in ('media','venv','tmp','__pycache__','node_modules') for part in path.parts):
            raise ValueError('Contenido privado/runtime excluido.')
        data=(ROOT/name).read_bytes()
        if name.endswith('.py'):ast.parse(data,filename=name,feature_version=(3,7))
        accepted=[];missing=False
        for commit in BASES:
            previous=subprocess.run(['git','-c','core.fsmonitor=false','show',commit+':'+name],cwd=str(ROOT),capture_output=True)
            if previous.returncode==0:accepted.append(normalized(previous.stdout))
            else:missing=True
        item={'path':name,'sha256':digest(data)}
        if accepted:item['accepted_base_normalized_sha256']=sorted(set(accepted))
        else:item['new_code']=True
        if missing:item['base_missing_allowed']=True
        files.append(item);payload['payload/'+name]=data
    source_commit=subprocess.check_output(['git','-c','core.fsmonitor=false','rev-parse','HEAD'],cwd=str(ROOT),text=True).strip()
    manifest={'source_commit':source_commit,'schema':1,'project':PROJECT,'version':VERSION,'base_commit':BASE,'accepted_base_commits':BASES,'app':APP,
        'required_migration':REQUIRED,'migration_targets':[],'production_installation':'pending','files':files}
    manifest_data=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    installer=(ROOT/INSTALLER).read_bytes()
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(output,'w',ZIP_DEFLATED) as z:
        z.writestr('instalar.py',installer);z.writestr('release_manifest.json',manifest_data)
        for name,data in sorted(payload.items()):z.writestr(name,data)
    with ZipFile(output) as z:
        if z.testzip() is not None or len(z.namelist())!=len(payload)+2:raise ValueError('ZIP incorrecto.')
        if z.read('instalar.py')!=installer:raise ValueError('Instalador diferente.')
        for item in files:
            if digest(z.read('payload/'+item['path']))!=item['sha256']:raise ValueError('Hash incorrecto.')
    (ROOT/('MANIFEST_'+VERSION.replace('.','_')+'.json')).write_bytes(manifest_data)
    sha=digest(output.read_bytes())
    output.with_suffix('.zip.sha256').write_bytes((sha+'  '+output.name+'\n').encode('ascii'))
    print('ZIP:',output);print('Archivos:',len(payload)+2);print('SHA256:',sha)
    return output
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=ROOT/'output'/ZIP_NAME)
    build(parser.parse_args().output)
