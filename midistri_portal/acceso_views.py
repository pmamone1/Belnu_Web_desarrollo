from hashlib import sha256
import time
import secrets
from urllib.parse import urlencode
from django.core import signing
from django import forms
from django.conf import settings
from django.core.exceptions import PermissionDenied,ValidationError
from django.http import JsonResponse,HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET,require_POST
from django.utils.crypto import salted_hmac
from .client import api,ApiError
from .models import Distribuidora
from .sesion_pestana import datos_prueba,navegador,crear_sesion_pestana


def respuesta_error(error):
    return JsonResponse({'error':str(error)},status=getattr(error,'status',403))


def habilitado():
    if not getattr(settings,'MIDISTRI_LOGIN_CODIGO_ENABLED',False):raise ApiError('Ingreso con código no disponible.',503)
    caps=api('capabilities')
    if (caps.get('login_codigo')!=1 or caps.get('sesion_pestana')!=1
        or caps.get('login_codigo_habilitado') is not True):raise ApiError('Ingreso con código todavía no disponible.',503)
    return caps


@require_GET
def pantalla(request):
    if not getattr(settings,'MIDISTRI_LOGIN_CODIGO_ENABLED',False):return HttpResponse('Ingreso con código no disponible.',status=503)
    ds=Distribuidora.objects.filter(activa=True).order_by('nombre')
    selected=request.GET.get('distribuidora','')
    return render(request,'midistri_portal/acceso_codigo.html',{'titulo':'Entrar a MiDistri-Pedidos',
        'distribuidoras':ds,'seleccionada':int(selected) if selected.isdecimal() else None})


def _pendientes(request):
    pending=request.session.get('midistri_login_pending',{})
    return {k:v for k,v in pending.items() if type(v)==dict and v.get('vence',0)>time.time()}


@require_POST
def iniciar(request):
    try:
        caps=habilitado();ident,proof=datos_prueba(request)
        selected=request.POST.get('distribuidora','')
        legacy=bool(selected)
        if legacy:
            if not selected.isdecimal() or not Distribuidora.objects.filter(activa=True,pk=int(selected)).exists():
                raise ApiError('Tienda no disponible.',400)
            if caps.get('login_codigo_tienda')!=1:raise ApiError('Falta actualizar Urban Soft para ingresar.',503)
        elif caps.get('login_email_perfiles')!=1:
            raise ApiError('Falta actualizar Urban Soft para ingresar sólo con Email. No se envió un código.',503)
        email=forms.EmailField(max_length=254).clean(request.POST.get('email',''))
        navegador(request,True)
        ip=salted_hmac('midistri.login.ip',request.META.get('REMOTE_ADDR',''),algorithm='sha256').hexdigest()
        data={'email':email,'desafio':sha256(proof.encode()).hexdigest(),'ip':ip}
        if legacy:data['distribuidora']=int(selected)
        version=1 if legacy else 2
        result=api('login-code-request' if legacy else 'login-code-email-request',method='POST',data=data)
        if result.get('version')!=version or not isinstance(result.get('solicitud'),str) or len(result['solicitud'])>100:raise ApiError('Respuesta de ingreso inválida.')
        pending=_pendientes(request)
        if ident not in pending and len(pending)>=10:raise ApiError('Demasiadas pestañas de ingreso. Cerrá las anteriores.',429)
        pending[ident]={'version':version,'solicitud':result['solicitud'],'hash':sha256(proof.encode()).hexdigest(),'vence':time.time()+1800}
        request.session['midistri_login_pending']=pending
        return JsonResponse({'fase':'codigo','mensaje':'Si ese Email está habilitado, recibirás un código para ingresar.'})
    except ValidationError:return JsonResponse({'error':'Ingresá un Email válido.'},status=400)
    except (ApiError,PermissionDenied) as e:return respuesta_error(e)


def _pending(request):
    ident,proof=datos_prueba(request)
    pending=_pendientes(request);row=pending.get(ident)
    if row is None or row['hash']!=sha256(proof.encode()).hexdigest():raise PermissionDenied('Solicitá un código en esta pestaña.')
    return ident,proof,row,pending


def _select(request,seleccion):
    ident,proof,row,pending=_pending(request)
    if not row.get('ticket'):raise PermissionDenied('Primero verificá tu código.')
    version=row.get('version',1)
    expected=row.get('opciones',{}).get(seleccion)
    if version==2 and expected is None:raise PermissionDenied('Elegí un perfil válido.')
    if expected and expected['tipo']=='administracion':
        from .operadores import habilitado as admin_habilitado
        if not admin_habilitado():raise ApiError('Administración temporalmente no disponible.',503)
    nonce=secrets.token_urlsafe(32)
    data={'ticket':row['ticket'],'seleccion':seleccion,'desafio':row['hash']}
    if version==2:data['desafio_admin']=nonce
    result=api('login-code-select' if version==1 else 'login-code-email-select',method='POST',data=data)
    if version==2 and result.get('tipo')!=expected['tipo']:raise ApiError('Respuesta de perfil inválida.')
    if version==2 and expected['tipo']=='administracion':
        from .operadores import origen_urban
        from .operadores_views import SALT,nombre_cookie_desafio
        token=result.get('continuacion');did=result.get('distribuidora_id')
        if not isinstance(token,str) or not 20<=len(token)<=100 or type(did) is not int or did<1:
            raise ApiError('Respuesta administrativa inválida.')
        if did!=expected['distribuidora_id']:raise ApiError('La tienda de acceso cambió.')
        request.session.setdefault('midistri_admin_browser',secrets.token_urlsafe(32))
        response=JsonResponse({'fase':'dentro','url':origen_urban()+'/midistri/ingreso-email/?'+urlencode({'codigo':token,'desafio':nonce})})
        contexto={'nonce':nonce,'destino':'tienda','distribuidora':did}
        response.set_cookie(nombre_cookie_desafio(nonce),signing.dumps(contexto,salt=SALT),max_age=600,
            secure=True,httponly=True,samesite='None',path='/portal/administrar/')
    else:
        try:response=JsonResponse(crear_sesion_pestana(request,result['perfil'],result['session_token'],ident,proof))
        except (KeyError,TypeError):raise ApiError('Respuesta de acceso inválida.') from None
    pending.pop(ident,None);request.session['midistri_login_pending']=pending
    return response



@require_POST
def verificar(request):
    try:
        habilitado();ident,proof,row,pending=_pending(request)
        codigo=request.POST.get('codigo','').strip()
        if len(codigo)!=6 or not codigo.isascii() or not codigo.isdigit():raise ApiError('Ingresá los seis números del código.',400)
        result=api('login-code-email-verify' if row.get('version')==2 else 'login-code-verify',method='POST',data={'solicitud':row['solicitud'],'codigo':codigo,'desafio':row['hash']})
        options=result.get('identidades')
        if result.get('version')!=row.get('version',1) or not isinstance(options,list) or not 1<=len(options)<=100:raise ApiError('Respuesta de acceso inválida.')
        clean=[]
        for item in options:
            if (not isinstance(item,dict) or any(not isinstance(item.get(k),str) or not 1<=len(item[k])<=150 for k in ('seleccion','nombre','distribuidora'))):raise ApiError('Respuesta de acceso inválida.')
            option={k:item[k] for k in ('seleccion','nombre','distribuidora')}
            if row.get('version')==2:
                if item.get('tipo') not in ('vendedor','administracion') or type(item.get('distribuidora_id')) is not int or item['distribuidora_id']<1:
                    raise ApiError('Respuesta de perfil inválida.')
                option.update(tipo=item['tipo'],distribuidora_id=item['distribuidora_id'])
            clean.append(option)
        ticket=result.get('ticket')
        if not isinstance(ticket,str) or not 20<=len(ticket)<=100:raise ApiError('Respuesta de acceso inválida.')
        row['ticket']=ticket;row['vence']=time.time()+120
        row['opciones']={i['seleccion']:i for i in clean}
        pending[ident]=row;request.session['midistri_login_pending']=pending
        if len(clean)==1:return _select(request,clean[0]['seleccion'])
        return JsonResponse({'fase':'elegir','identidades':clean})
    except (ApiError,PermissionDenied) as e:return respuesta_error(e)


@require_POST
def seleccionar(request):
    try:
        habilitado()
        return _select(request,request.POST.get('seleccion',''))
    except (ApiError,PermissionDenied) as e:return respuesta_error(e)
