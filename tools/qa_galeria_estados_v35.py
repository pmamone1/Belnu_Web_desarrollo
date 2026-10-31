"""Render synthetic orders for browser QA, with no database or remote calls."""
import os,sys
from pathlib import Path
from types import SimpleNamespace as NS
from datetime import datetime,timezone
from uuid import UUID
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
os.environ['DJANGO_SETTINGS_MODULE']='midistri_portal.test_settings'
import django;django.setup()
from django.template.loader import render_to_string
from midistri_portal.test_parciales_v6 import pedido
from midistri_portal.historial_presentacion import resumen_pedido
orders=[]
for n,state in enumerate(('pendiente','recibido','ok','emitido','cancelado','desconocido'),1):
    data=pedido();data['estado']=state
    if state!='emitido':data.pop('atencion',None)
    o=NS(pk=UUID(int=n),referencia_publica='MP-PRUEBA-'+str(n),creado=datetime(2026,10,31,12,tzinfo=timezone.utc),respuesta=data,datos={},estado=state)
    o.resumen=resumen_pedido(o);orders.append(o)
request=NS(user=NS(is_staff=False),midistri_recordar_enabled=False)
html=render_to_string('midistri_portal/pedidos.html',{'pedidos':orders,'request':request})
gallery='''<article class="card" style="width:320px"><a href="#" data-galeria="1"><img src="/small.svg" alt="Foto de prueba"></a><script type="application/json" id="galeria-1">{"nombre":"Fotos de prueba","items":[{"tipo":"foto","url":"/small.svg","descripcion":"Foto pequeña"},{"tipo":"foto","url":"/large.svg","descripcion":"Foto grande"},{"tipo":"foto","url":"/portrait.svg","descripcion":"Foto vertical"}]}</script></article>'''
html=html.replace('</main>',gallery+'</main>')
target=ROOT/'tmp/qa_v35';target.mkdir(exist_ok=True)
(target/'fixture.html').write_text(html,encoding='utf-8')
print('Synthetic HTML ready, no database or SMTP')
