"""Isolated HTTPS browser fixture. Synthetic DB and API only; never SMTP."""
import argparse,json,os,sys,ssl,tempfile
from pathlib import Path
from uuid import uuid4
from socketserver import ThreadingMixIn
from wsgiref.simple_server import make_server,WSGIServer,WSGIRequestHandler
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=63404);parser.add_argument('--cert',required=True);parser.add_argument('--key',required=True);args=parser.parse_args()
os.environ['DJANGO_SETTINGS_MODULE']='midistri_portal.test_settings'
from django.conf import settings
work=tempfile.TemporaryDirectory(prefix='midistri30_browser_')
settings.DATABASES['default']['NAME']=str(Path(work.name)/'synthetic.sqlite3')
settings.ALLOWED_HOSTS=['127.0.0.1','localhost']
settings.MIDISTRI_LOGIN_CODIGO_ENABLED=True;settings.MIDISTRI_ACCESO_RECORDADO_ENABLED=True
settings.MIDISTRI_ADMIN_ENABLED=False;settings.PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher']
import django;django.setup()
from django.core.management import call_command
call_command('migrate',verbosity=0,interactive=False)
from midistri_portal.models import Distribuidora,Publicacion
for did,name in ((20,'20 - Belgrano'),(61,'61 - Recova')):
 d=Distribuidora.objects.create(pk=did,nombre=name)
 Publicacion.objects.create(producto_id=1,distribuidora=d,nombre='Producto QA',codigo='QA-1',precio=100,pvp=150,imagenes=['https://sistema7000.belnu.com.ar/catalogo-imagenes/qa.jpg'])
from midistri_portal.client import ApiError
state={'down':False};tokens={};tickets={};requests={};devices={}
def profile(did):return {'id':7 if did==20 else 8,'nombre':'Kiosco QA' if did==20 else 'Otro Kiosco QA','distribuidora_id':did,'distribuidora':'20 - Belgrano' if did==20 else '61 - Recova','linea':'QA','lin':1,'vv':7 if did==20 else 8}
def options(email):return [{'seleccion':'qa-seleccion-'+str(did)+'x'*22,'tipo':'vendedor','nombre':profile(did)['nombre'],'distribuidora':profile(did)['distribuidora'],'distribuidora_id':did,'vendedor_id':profile(did)['id']} for did in ([20,61] if email=='multi@example.test' else [20])]
def issue(did,email):
 token='qa-bearer-'+uuid4().hex;tokens[token]={'profile':profile(did),'email':email};return token
def fake(action,**kw):
 if state['down']:raise ApiError('Urban de prueba temporalmente no disponible',503)
 data=kw.get('data') or {};token=kw.get('token')
 if action=='capabilities':return {'login_codigo':1,'sesion_pestana':1,'login_codigo_habilitado':True,'login_email_perfiles':1,'seller_device':1,'seller_device_habilitado':True}
 if action=='login-code-email-request':
  ident=str(uuid4());requests[ident]=data['email'];return {'version':2,'solicitud':ident}
 if action=='login-code-email-verify':
  if data['codigo']!='123456':raise ApiError('Codigo de prueba incorrecto',403)
  email=requests[data['solicitud']];ticket='qa-ticket-'+uuid4().hex;tickets[ticket]=email
  return {'version':2,'ticket':ticket,'identidades':options(email)}
 if action=='login-code-email-select':
  email=tickets[data['ticket']];choice=next(i for i in options(email) if i['seleccion']==data['seleccion'])
  return {'tipo':'vendedor','perfil':profile(choice['distribuidora_id']),'session_token':issue(choice['distribuidora_id'],email)}
 if action=='seller-device-remember':
  value=data['credencial'];devices[value]={'email':tokens[token]['email'],'revocado':False}
  return {'version':1,'dispositivo':value.split('.')[0]}
 if action in ('seller-device-profiles','seller-device-resume'):
  value=data['credencial'];device=devices.get(value)
  if not device or device['revocado']:raise ApiError('Dispositivo revocado',403)
  opts=options(device['email'])
  if action.endswith('profiles'):return {'version':1,'identidades':opts}
  choice=next(i for i in opts if i['seleccion']==data['seleccion']);did=choice['distribuidora_id']
  if not token or tokens[token]['profile']['distribuidora_id']!=did:token=issue(did,device['email'])
  return {'version':1,'tipo':'vendedor','perfil':profile(did),'session_token':token}
 if action=='seller-device-revoke':
  for value,row in devices.items():
   if value.split('.')[0]==data['dispositivo']:row['revocado']=True
  return {'version':1,'ok':True}
 if action=='profile':return tokens[token]['profile']
 if action=='orders':return {'pedidos':[]}
 if action=='logout':return {'ok':True}
 raise AssertionError('Unexpected synthetic API action: '+action)
from django.core.wsgi import get_wsgi_application
from django.contrib.staticfiles.handlers import StaticFilesHandler
app=StaticFilesHandler(get_wsgi_application())
def wrapped(environ,start_response):
 environ['wsgi.url_scheme']='https'
 if environ['PATH_INFO'].startswith('/__qa__/'):
  state['down']=environ['PATH_INFO'].endswith('/down/')
  start_response('200 OK',[('Content-Type','application/json')]);return [b'{"ok":true}']
 return app(environ,start_response)
class Server(ThreadingMixIn,WSGIServer):daemon_threads=True
with patch('midistri_portal.acceso_views.api',side_effect=fake),patch('midistri_portal.dispositivos.api',side_effect=fake),patch('midistri_portal.views.api',side_effect=fake):
 server=make_server('127.0.0.1',args.port,wrapped,server_class=Server)
 tls=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);tls.load_cert_chain(args.cert,args.key)
 server.socket=tls.wrap_socket(server.socket,server_side=True)
 print('READY synthetic-only https://127.0.0.1:'+str(args.port),flush=True)
 try:server.serve_forever()
 finally:server.server_close();work.cleanup()
