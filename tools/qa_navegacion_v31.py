"""Render real catalog templates with synthetic data; no database, API or SMTP."""
import os,re,sys
from pathlib import Path
from types import SimpleNamespace as NS
from decimal import Decimal
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','midistri_portal.test_settings')
import django
django.setup()
from django.template import engines
from django.test import RequestFactory
from django.core.paginator import Paginator
ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/'tmp/qa_navegacion31';OUTPUT.mkdir(parents=True,exist_ok=True)
source="{% extends 'midistri_portal/base.html' %}{% block content %}<div class='pagina-catalogo'>{% include 'midistri_portal/catalogo_productos.html' %}</div>{% endblock %}"
template=engines['django'].from_string(source)
products=[NS(nombre='Producto de prueba '+str(i),producto_id=i,precio=Decimal('12500'),pvp=Decimal('18000'),
    codigo='SKU-'+str(i),categorias_catalogo=['Alimentos'],subcategoria_catalogo='',display=0,imagenes=[],galeria=[],cantidad_carrito=0) for i in range(1,73)]
for page in (1,2,12):
    req=RequestFactory().get('/portal/');req.user=NS(is_staff=False);req.midistri_recordar_enabled=True
    html=template.render({'perfil':{'nombre':'Kiosco de prueba'},'distribuidora':NS(pk=1),
        'pagina_mensajes':{'titulo':'Productos para tu kiosco','encabezado':'MiDistri'},'productos':Paginator(products,6).page(page),
        'q':'coní & chocolate','categoria':'Alimentos y Bebidas','orden':'precio_desc','ranking_disponible':True},request=req)
    # This fixture verifies presentation only: no behavior scripts or external assets.
    html=re.sub(r'<script\b[^>]*>.*?</script>','',html,flags=re.S)
    html=re.sub(r'<link\b[^>]*>','',html)
    css='\n'.join((ROOT/'midistri_portal/static/midistri_portal'/n).read_text(encoding='utf-8') for n in ('galeria.css','temas.css','pagina.css'))
    html=html.replace('</head>','<style>'+css+'</style></head>')
    (OUTPUT/('pagina'+str(page)+'.html')).write_bytes(html.encode('utf-8'))
print('Rendered synthetic catalog pages1/2/12')
