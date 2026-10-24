import os,shutil,sys
from pathlib import Path
from types import SimpleNamespace as N
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','midistri_portal.test_settings')
import django
django.setup()
from django.template.loader import render_to_string
out=Path('tmp/qa_v14');out.mkdir(parents=True,exist_ok=True)
request=N(user=N(is_staff=False),midistri_codigo_enabled=True)
context={'titulo':'Entrar a MiDistri-Pedidos','request':request,'messages':[]}
html=render_to_string('midistri_portal/acceso_codigo.html',context)
html=html.replace('/static/','/static/')
(out/'acceso.html').write_text(html,encoding='utf-8')
shutil.copytree('midistri_portal/static',out/'static',dirs_exist_ok=True)
print('Vista sintética sin base, API ni correo preparada.')
