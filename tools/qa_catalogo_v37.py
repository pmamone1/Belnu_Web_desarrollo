"""Local synthetic portal only. Memory DB, API stub, no SMTP or external calls."""
import os,sys,json,mimetypes
from pathlib import Path
from types import SimpleNamespace as NS
from http.server import HTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlsplit,parse_qs
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
os.environ['DJANGO_SETTINGS_MODULE']='midistri_portal.test_settings'
import django;django.setup()
from django.conf import settings
settings.ALLOWED_HOSTS+=['127.0.0.1'];settings.MIDISTRI_MULTIMEDIA_ENABLED=True
from django.core.management import call_command
from django.test import Client
from midistri_portal.models import Distribuidora,Tienda,Publicacion
from midistri_portal.pagina import inicial,validar_pagina
from midistri_portal.editor_views import html_pagina
call_command('migrate',verbosity=0,interactive=False)
d=Distribuidora.objects.create(pk=20,nombre='Distribuidora de prueba');t=Tienda.objects.create(distribuidora=d)
for i in range(1,106):
    name='Producto de prueba '+str(i)
    if i%3==0:name='Producto con nombre muy largo para verificar el ajuste de la tarjeta '+str(i)
    Publicacion.objects.create(distribuidora=d,producto_id=i,codigo='SKU-'+str(i),nombre=name,categoria='Alimentos',clasificacion={'categorias':['Alimentos'],'subcategoria':'Alfajores' if i%2 else 'Bebidas'},display=15 if i%2 else 0,precio=12500,pvp=18000,imagenes=['https://example.test/producto'+str(i)+'.svg'],multimedia=[{'tipo':'foto','url':'https://example.test/producto'+str(i)+'.svg','descripcion':name},{'tipo':'foto','url':'https://example.test/detalle'+str(i)+'.svg','descripcion':'Detalle'}],indicadores={'orden_ventas':i,'ranking':i} if i<11 else {})
data=inicial(t);data['inicial_anterior']=False;data['mensajes'].update(encabezado='MiDistri - Tienda de prueba',bienvenida='Todo para tu kiosco')
blocks=[dict(id='lateral-derecha',tipo='texto',titulo='Promoción derecha',texto='Material promocional publicado a la derecha',enlace='https://example.test/promo',boton='Ver',activo=True,estilo={'zona':'derecha'}),dict(id='lateral-izquierda',tipo='texto',titulo='Promoción izquierda',texto='Material promocional publicado a la izquierda',enlace='https://example.test/promo',boton='Ver',activo=True,estilo={'zona':'izquierda'}),dict(id='central',tipo='texto',titulo='Banner central conservado',texto='Productos para tu kiosco',activo=True,estilo={'zona':'centro'})]
data['bloques']=blocks+data['bloques'];data=validar_pagina(data,d.pk,fuentes=False)
perfil={'id':7,'nombre':'Kiosco de prueba','linea':'Prueba','distribuidora_id':20,'distribuidora':d.nombre}
def identify(request):request.midistri_perfil=perfil;return perfil
client=Client();settings.EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_GET(self):self.handle_request()
    def do_POST(self):self.handle_request()
    def handle_request(self):
        url=urlsplit(self.path);params=parse_qs(url.query)
        from django.template import engines
        for loader in engines['django'].engine.template_loaders:
            if hasattr(loader,'reset'):loader.reset()
        if url.path.startswith('/static/'):
            static=ROOT/'midistri_portal/static';file=(static/url.path[8:]).resolve()
            if static.resolve() in file.parents and file.is_file():
                b=file.read_bytes();self.send_response(200);self.send_header('Content-Type',mimetypes.guess_type(str(file))[0] or 'application/octet-stream');self.end_headers();self.wfile.write(b);return
            self.send_error(404);return
        data['diseno']=params.get('diseno',['compacto'])[0] if params.get('diseno',['compacto'])[0] in ('compacto','fotos','promociones','lista') else 'compacto'
        with patch('midistri_portal.views.identificar',side_effect=identify),patch('midistri_portal.pagina.pagina_publica',return_value=data):
            if url.path=='/qa/preview/':
                html=html_pagina(data,d).replace('<main>','<main class="preview-movil">');status=200;headers={'Content-Type':'text/html; charset=utf-8'};body=html.encode()
            else:
                if self.command=='POST':response=client.post(self.path,{k:v[-1] for k,v in parse_qs(self.rfile.read(int(self.headers.get('Content-Length',0))).decode()).items()})
                else:response=client.get(self.path)
                status=response.status_code;headers=dict(response.items());body=response.content
        self.send_response(status)
        for k,v in headers.items():self.send_header(k,v)
        self.end_headers();self.wfile.write(body)
print('QA_CATALOGO_READY http://127.0.0.1:63737/portal/?distribuidora=20',flush=True)
HTTPServer(('127.0.0.1',63737),Handler).serve_forever()
