from hashlib import sha256
import time
from django import forms
from django.conf import settings
from django.core.exceptions import PermissionDenied,ValidationError
from django.http import JsonResponse,HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET,require_POST
from django.utils.crypto import salted_hmac
from .client import api,ApiError
from .sesion_pestana import datos_prueba,navegador,crear_sesion_pestana


def respuesta_error(error):
    return JsonResponse({'error':str(error)},status=getattr(error,'status',403))


def habilitado():
    if not getattr(settings,'MIDISTRI_LOGIN_CODIGO_ENABLED',False):raise ApiError('Ingreso con código no disponible.',503)
    caps=api('capabilities')
    if (caps.get('login_codigo')!=1 or caps.get('sesion_pestana')!=1
        or caps.get('login_codigo_habilitado') is not True):raise ApiError('Ingreso con código todavía no disponible.',503)


@require_GET
def pantalla(request):
    if not getattr(settings,'MIDISTRI_LOGIN_CODIGO_ENABLED',False):return HttpResponse('Ingreso con código no disponible.',status=503)
    return render(request,'midistri_portal/acceso_codigo.html',{'titulo':'Entrar a MiDistri-Pedidos'})


def _pendientes(request):
    pending=request.session.get('midistri_login_pending',{})
    return {k:v for k,v in pending.items() if type(v)==dict and v.get('vence',0)>time.time()}


@require_POST
def iniciar(request):
    try:
        habilitado();ident,proof=datos_prueba(request)
        email=forms.EmailField(max_length=254).clean(request.POST.get('email',''))
        navegador(request,True)
        ip=salted_hmac('midistri.login.ip',request.META.get('REMOTE_ADDR',''),algorithm='sha256').hexdigest()
        result=api('login-code-request',method='POST',data={'email':email,'desafio':sha256(proof.encode()).hexdigest(),'ip':ip})
        if result.get('version')!=1 or not isinstance(result.get('solicitud'),str) or len(result['solicitud'])>100:raise ApiError('Respuesta de ingreso inválida.')
        pending=_pendientes(request)
        if ident not in pending and len(pending)>=10:raise ApiError('Demasiadas pestañas de ingreso. Cerrá las anteriores.',429)
        pending[ident]={'solicitud':result['solicitud'],'hash':sha256(proof.encode()).hexdigest(),'vence':time.time()+1800}
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
    result=api('login-code-select',method='POST',data={'ticket':row['ticket'],'seleccion':seleccion,'desafio':row['hash']})
    try:response=crear_sesion_pestana(request,result['perfil'],result['session_token'],ident,proof)
    except (KeyError,TypeError):raise ApiError('Respuesta de acceso inválida.') from None
    pending.pop(ident,None);request.session['midistri_login_pending']=pending
    return JsonResponse(response)


@require_POST
def verificar(request):
    try:
        habilitado();ident,proof,row,pending=_pending(request)
        codigo=request.POST.get('codigo','').strip()
        if len(codigo)!=6 or not codigo.isascii() or not codigo.isdigit():raise ApiError('Ingresá los seis números del código.',400)
        result=api('login-code-verify',method='POST',data={'solicitud':row['solicitud'],'codigo':codigo,'desafio':row['hash']})
        options=result.get('identidades')
        if result.get('version')!=1 or not isinstance(options,list) or not 1<=len(options)<=100:raise ApiError('Respuesta de acceso inválida.')
        clean=[]
        for item in options:
            if (not isinstance(item,dict) or any(not isinstance(item.get(k),str) or not 1<=len(item[k])<=150 for k in ('seleccion','nombre','distribuidora'))):raise ApiError('Respuesta de acceso inválida.')
            clean.append({k:item[k] for k in ('seleccion','nombre','distribuidora')})
        ticket=result.get('ticket')
        if not isinstance(ticket,str) or not 20<=len(ticket)<=100:raise ApiError('Respuesta de acceso inválida.')
        row['ticket']=ticket;row['vence']=time.time()+120
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
