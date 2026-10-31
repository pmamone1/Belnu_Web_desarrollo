"""Synthetic local UI harness: in-memory SQLite, no remote APIs or SMTP."""
import os,sys,json,re
from pathlib import Path
from types import SimpleNamespace as NS
from http.server import HTTPServer,BaseHTTPRequestHandler
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
os.environ['DJANGO_SETTINGS_MODULE']='midistri_portal.test_settings'
import django;django.setup()
from django.core.management import call_command
from django.template.loader import render_to_string
from django.test import RequestFactory
from midistri_portal.models import Distribuidora,Tienda,Publicacion
from midistri_portal.pagina import inicial,validar_pagina,advertencias_pagina
from midistri_portal.editor_views import html_pagina
from midistri_portal.editor_estilos import validar_estilo
from midistri_portal.marcas import opciones
from midistri_portal.test_parciales_v6 import pedido
from midistri_portal.historial_presentacion import resumen_pedido
from uuid import UUID
from datetime import datetime,timezone
call_command('migrate',verbosity=0,interactive=False)
d=Distribuidora.objects.create(pk=20,nombre='Distribuidora de prueba');t=Tienda.objects.create(distribuidora=d)
draft=inicial(t);draft['mensajes'].update(encabezado='MiDistri · tienda de prueba',titulo='Productos para tu kiosco')
draft['bloques'].insert(0,dict(id='promocion',tipo='texto',activo=True,titulo='Promoción de prueba',texto='Texto editable'))
draft['bloques'].insert(0,dict(id='retirado',tipo='banner',activo=True,titulo='Promoción retirada',diapositivas=[dict(publicacion=999,tipo='foto',url='https://example.test/retirada.jpg')]))
revision=0;output=ROOT/'tmp/qa_analitica34';output.mkdir(exist_ok=True)
req=RequestFactory().get('/portal/');req.user=NS(is_staff=False);req.midistri_recordar_enabled=False
orders=[]
for i,state in enumerate(('recibido','emitido','cancelado'),1):
    data=pedido();data['estado']=state
    if state!='emitido':data.pop('atencion')
    order=NS(pk=UUID(int=i),referencia_publica='MP-00000'+str(i),creado=datetime(2026,10,30,12,tzinfo=timezone.utc),respuesta=data,datos={},estado=state)
    order.resumen=resumen_pedido(order);orders.append(order)
from datetime import timedelta
from django.utils import timezone as dz
from django.core.paginator import Paginator
from urllib.parse import urlsplit,parse_qs
from midistri_portal.models import ConsultaAnalitica,EventoAnalitico
from midistri_portal.analitica_informes import resultado
from midistri_portal.analitica_detalle import detalle,tarjetas
from midistri_portal.analitica_productos import enriquecer
now=dz.now();today=dz.localtime(now).date();visits=[UUID(int=1),UUID(int=2)]
for i in range(51):EventoAnalitico.objects.create(fecha=now-timedelta(seconds=60-i),distribuidora_id=20,vendedor_id=7,vendedor='Kiosco Norte',visita=visits[0],tipo='foto_ampliada',producto_id=101,producto='Termo de prueba',sku='T-101',huella='a'*64)
for seller,kind,pid in ((7,'ingreso',None),(7,'producto_consulta',101),(8,'producto_consulta',102)):
    EventoAnalitico.objects.create(fecha=now-timedelta(seconds=5),distribuidora_id=20,vendedor_id=seller,vendedor='Kiosco Norte' if seller==7 else 'Kiosco Sur',visita=visits[0] if seller==7 else visits[1],tipo=kind,producto_id=pid,producto='Termo de prueba' if pid==101 else 'Mate de prueba' if pid else '',sku='T-101' if pid==101 else 'M-102' if pid else '',huella='a'*64)
qa_query=ConsultaAnalitica.objects.create(id=UUID(int=34),operador_id=7,distribuidora_id=20,distribuidoras=[20],desde=today,hasta=today,vence=now+timedelta(hours=2),completa=True,meta={'corte':now.isoformat(),'distribuidoras':[{'id':20,'nombre':'Distribuidora de prueba'}],'local':{'intervalos':[{'distribuidora_id':20,'desde':(now-timedelta(days=1)).isoformat(),'hasta':None}],'incidencias':[],'evidencia':[]}},datos={'vendedores':[{'id':i,'distribuidora_id':20,'nombre':n,'lin':1,'vv':i,'actual':True,'activo':True,'contacto':True,'pedidos_historicos':1} for i,n in ((7,'Kiosco Norte'),(8,'Kiosco Sur'))],'pedidos':[{'id':str(UUID(int=35)),'distribuidora_id':20,'vendedor_id':8,'vendedor':'Kiosco Sur','creado':(now-timedelta(seconds=1)).isoformat(),'items':[{'producto_id':102,'nombre':'Mate de prueba','codigo':'M-102','cantidad':2,'precio':'6250.00','pvp':'8000.00'}],'referencia':'MP-000035','estado':'recibido','atencion':'pendiente','conciliacion':False,'unidades_solicitadas':2,'unidades_confirmadas':0,'total_solicitado':'12500.00','total_confirmado':'0.00'}]})
qa_operator={'nombre':'Operador de prueba','permisos':['midistri.tienda_configurar','pedidos.gestionar'],'distribuidoras':[{'id':20,'nombre':'Distribuidora de prueba'}]}
def analitica_html(path):
    query={k:v[-1] for k,v in parse_qs(urlsplit(path).query).items()};query['distribuidora']='20'
    data=resultado(qa_query,query);enriquecer(data,query);ctx=dict(data,tienda={'id':20},operador=qa_operator,request=req,csrf_token='synthetic-csrf',tarjetas=tarjetas(data['resumen'],query),desde=today.isoformat(),hasta=today.isoformat(),params='distribuidora=20',excel_url='#',acciones=Paginator(data['eventos'],50).page(1),ordenes=Paginator(data['pedidos'],50).page(1),productos_pagina=Paginator(data['productos'],50).page(1),vendedores_pagina=Paginator(data['vendedores'],50).page(1))
    if query.get('detalle'):ctx['detalle_indicador']=detalle(data,query['detalle'],query.get('pagina_detalle',1),query)
    partial=query.get('parcial')=='metrica'
    content=render_to_string('midistri_portal/analitica_detalle.html' if partial else 'midistri_portal/analitica_panel.html',ctx)
    return json.dumps({'html':content}) if partial else content, 'application/json' if partial else 'text/html'
def pedidos_html():return render_to_string('midistri_portal/pedidos.html',dict(pedidos=orders,perfil={'nombre':'Vendedor de prueba'},pagina=draft,pagina_mensajes=draft['mensajes'],cart_count=0,request=req))
def editor_html():return render_to_string('midistri_portal/editor_visual.html',dict(tienda={'id':20},marcas=opciones(),request=req,csrf_token='synthetic-csrf-token',operador=qa_operator))
def reply():return dict(datos=draft,revision=revision,html=html_pagina(draft,d),recursos=[],estilos_defecto=validar_estilo({}),advertencias=advertencias_pagina(draft,20))
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def send(self,content,kind='text/html',status=200):
        content=content.encode('utf-8') if isinstance(content,str) else content
        self.send_response(status);self.send_header('Content-Type',kind+'; charset=utf-8');self.send_header('Content-Length',str(len(content)));self.end_headers();self.wfile.write(content)
    def do_GET(self):
        if self.path.startswith('/static/midistri_portal/'):
            name=self.path.split('?')[0].replace('/static/','');file=ROOT/name
            file=ROOT/'midistri_portal/static'/name
            if file.is_file():return self.send(file.read_bytes(),'text/javascript' if file.suffix=='.js' else 'text/css' if file.suffix=='.css' else 'image/svg+xml')
        if self.path.startswith('/portal/administrar/estadisticas/'):
            content,kind=analitica_html(self.path);return self.send(content,kind)
        if self.path.startswith('/portal/pedidos/'):return self.send(pedidos_html())
        return self.send(editor_html())
    def do_POST(self):
        global draft,revision
        try:
            data=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            if data['accion']=='guardar':
                assert data['revision']==revision
                draft=validar_pagina(data['datos'],20,fuentes=False);revision+=1
            if data['accion']=='render':
                clean=validar_pagina(data['datos'],20,fuentes=False)
                return self.send(json.dumps(dict(html=html_pagina(clean,d),advertencias=advertencias_pagina(clean,20))),'application/json')
            self.send(json.dumps(reply()),'application/json')
        except Exception as e:self.send(json.dumps({'error':str(e)}),'application/json',400)
print('QA_READY http://127.0.0.1:63434',flush=True)
HTTPServer(('127.0.0.1',63434),Handler).serve_forever()
