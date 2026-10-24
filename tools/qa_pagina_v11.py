"""Render synthetic PC/mobile storefronts without a production connection."""
import os
os.environ['DJANGO_SETTINGS_MODULE']='midistri_portal.test_settings'
import django
django.setup()
from pathlib import Path
from uuid import uuid4
from django.core.management import call_command
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from midistri_portal.models import Distribuidora,Tienda,Publicacion
from midistri_portal.pagina import inicial,validar_pagina,DISENOS
from midistri_portal.pagina_views import contenido_contexto
call_command('migrate',verbosity=0)
root=Path(__file__).resolve().parents[1];output=root/'tmp/qa_v11';output.mkdir(parents=True,exist_ok=True)
d=Distribuidora.objects.create(pk=20,nombre='20 - Belgrano')
t=Tienda.objects.create(distribuidora=d,bienvenida='Novedades para tu kiosco')
products=[]
for index,name in enumerate(['Parlante portátil','Termo de acero','Juguetes virales']):
    p=Publicacion.objects.create(producto_id=index+1,distribuidora=d,nombre=name,categoria='Novedades',precio=25000,pvp=31000,
        multimedia=[dict(tipo='foto',url='https://foto.invalid/'+str(index)+'.png',descripcion=name,id=str(uuid4()),principal=True,orden=0)])
    p.galeria=p.multimedia;p.foto_card=p.multimedia[0]['url'];p.galeria_dom_id='galeria-'+str(p.producto_id);p.galeria_datos=dict(nombre=p.nombre,items=p.multimedia)
    products.append(p)
data=inicial(t)
slides=[dict(publicacion=p.pk,tipo='foto',url=p.multimedia[0]['url'],titulo=p.nombre,texto='Seleccionado para vos',boton='',enlace='') for p in products]
data['bloques'].insert(0,dict(id=str(uuid4()),tipo='banner',titulo='Productos virales',texto='Consultá las novedades de tu distribuidora',activo=True,automatico=True,segundos=3,diapositivas=slides))
data['bloques'].append(dict(id=str(uuid4()),tipo='banner',titulo='Una sola foto',texto='',activo=True,automatico=True,segundos=3,diapositivas=slides[:1]))
for layout,_ in DISENOS:
    data['diseno']=layout;clean=validar_pagina(data,20)
    ctx=contenido_contexto(clean,d);ctx.update(titulo='MiDistri · Tu kiosco',distribuidora=d,productos=Paginator(products,24).get_page(1),temas=[('claro','Claro'),('nocturno','Nocturno'),('azul','Azul'),('verde','Verde')])
    html=render_to_string('midistri_portal/catalogo.html',ctx)
    html=html.replace('/static/midistri_portal/',(root/'midistri_portal/static/midistri_portal').as_uri()+'/')
    (output/(layout+'.html')).write_text(html,encoding='utf-8')
print('QA sintética renderizada en',output)
