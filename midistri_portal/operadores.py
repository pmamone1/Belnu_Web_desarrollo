"""Server-held operator sessions, validated in Urban on every request."""
from urllib.parse import urlsplit
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse
from .client import api,ApiError
from .sesiones_operador import token_operador,borrar_token

PERMISOS={'pedidos.gestionar','pedidos.remitos','pedidos.remitos_ver',
          'midistri.catalogo_gestionar','midistri.tienda_configurar'}

def origen_urban():
    u=urlsplit(settings.URBAN_API_BASE)
    if u.scheme!='https' or not u.netloc or u.username or u.password or u.query or u.fragment:
        raise ApiError('Falta configurar la conexión HTTPS con Urban Soft.')
    return u.scheme+'://'+u.netloc

def habilitado():
    return bool(settings.MIDISTRI_ENABLED and getattr(settings,'MIDISTRI_ADMIN_ENABLED',False))

def perfil_valido(data):
    try:
        if data['version']!=1 or data['rol']!='distribuidor':raise ValueError
        if type(data['operador_id']) is not int or data['operador_id']<1:raise ValueError
        if not isinstance(data['nombre'],str) or not 1<=len(data['nombre'])<=200:raise ValueError
        ds=data['distribuidoras'];perms=data['permisos']
        if not isinstance(ds,list) or not 1<=len(ds)<=1000:raise ValueError
        ids=set()
        for d in ds:
            if type(d['id']) is not int or d['id']<1 or d['id'] in ids:raise ValueError
            if not isinstance(d['nombre'],str) or not 1<=len(d['nombre'])<=150:raise ValueError
            ids.add(d['id'])
        if not isinstance(perms,list) or not perms or any(p not in PERMISOS for p in perms):raise ValueError
        if type(data['financiero']) is not bool:raise ValueError
        expires=datetime.fromisoformat(data['vence'].replace('Z','+00:00'))
        if expires.tzinfo is None:raise ValueError
        return {k:data[k] for k in ('version','rol','operador_id','nombre','distribuidoras','permisos','financiero','vence')}
    except (KeyError,ValueError,TypeError,AttributeError):
        raise ApiError('Respuesta administrativa inválida; no se concede acceso.') from None

def perfil_operador(request,permiso=None):
    if not habilitado():raise ApiError('La administración de MiDistri está desactivada.')
    token=token_operador(request)
    if not token:raise ApiError('Ingrese desde Urban Soft.',401)
    try:perfil=perfil_valido(api('operator-profile',operator_token=token))
    except ApiError as e:
        if e.status in (401,403):borrar_token(request,token)
        raise
    if permiso and permiso not in perfil['permisos']:raise ApiError('No tiene permiso para esta operación.',403)
    request.midistri_operador_token=token
    request.midistri_operador=perfil
    return perfil

def tienda_permitida(perfil,value):
    try:
        did=int(value)
        if not any(d['id']==did for d in perfil['distribuidoras']):raise ValueError
        return did
    except (ValueError,TypeError):
        raise ApiError('Distribuidora fuera de alcance.',403) from None
