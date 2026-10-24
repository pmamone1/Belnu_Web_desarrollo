"""Synthetic distributor panel preview; no database or API calls."""
import os
from pathlib import Path
from types import SimpleNamespace as N
os.environ.setdefault('DJANGO_SETTINGS_MODULE','midistri_portal.test_settings')
import django
django.setup()
from django.template.loader import render_to_string
out=Path('tmp/qa_v13');out.mkdir(parents=True,exist_ok=True)
profile=dict(nombre='Responsable Recova',permisos=['midistri.tienda_configurar','pedidos.gestionar','midistri.catalogo_gestionar'],
    distribuidoras=[dict(id=61,nombre='61 - Recova')])
html=render_to_string('midistri_portal/operador_base.html',dict(operador=profile,tienda=profile['distribuidoras'][0],
    titulo='Administrar MiDistri-Pedidos',request=N(user=N(is_staff=False)),messages=[]))
html=html.replace('/static/',Path('midistri_portal/static').resolve().as_uri()+'/')
(out/'panel.html').write_text(html,encoding='utf8')
print('Synthetic panel HTML written. No database/API.')
