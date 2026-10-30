"""Persistent HttpOnly ownership, local revocation first, remote authority always."""
from hashlib import sha256
import re
import secrets
from uuid import UUID, uuid4
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from .client import api, ApiError
from .models import DispositivoRecordado, SesionVendedorPortal

COOKIE='midistri_dispositivo'
OLVIDO='midistri_dispositivo_olvido'
MAX_AGE=400*24*60*60


def activo():
    return bool(getattr(settings,'MIDISTRI_ACCESO_RECORDADO_ENABLED',False) and
                getattr(settings,'MIDISTRI_LOGIN_CODIGO_ENABLED',False))


def partes(value):
    try:
        ident,secret=value.split('.')
        ident=str(UUID(ident))
        if not re.fullmatch('[A-Za-z0-9_-]{43}',secret) or value!=ident+'.'+secret:
            raise ValueError
    except (ValueError,TypeError,AttributeError):
        raise PermissionDenied('Acceso recordado no valido.') from None
    return ident,sha256(value.encode()).hexdigest()


def local(request, revocados=False):
    raw=request.COOKIES.get(COOKIE)
    if not raw:return None
    ident,fingerprint=partes(raw)
    row=DispositivoRecordado.objects.filter(pk=ident).first()
    if row is None or not secrets.compare_digest(row.hash_cookie,fingerprint) or (row.revocado and not revocados):
        raise PermissionDenied('El acceso recordado ya no esta habilitado.')
    return row


def cookie(response, credencial):
    response.set_cookie(COOKIE,credencial,max_age=MAX_AGE,secure=True,httponly=True,samesite='Lax',path='/portal/')
    response['Cache-Control']='private, no-store'


def capacidades():
    caps=api('capabilities')
    if caps.get('seller_device')!=1 or caps.get('seller_device_habilitado') is not True:
        raise ApiError('El acceso recordado aun no esta habilitado en ambas aplicaciones.',503)


def conciliar():
    for row in DispositivoRecordado.objects.filter(revocado=True,remoto_pendiente=True).order_by('ultimo_uso')[:3]:
        try:
            result=api('seller-device-revoke',method='POST',data={'dispositivo':str(row.pk)})
            if result.get('version')==1 and result.get('ok') is True:
                DispositivoRecordado.objects.filter(pk=row.pk,revocado=True).update(remoto_pendiente=False)
        except ApiError:
            break


def olvidar(request,response):
    try:row=local(request,revocados=True)
    except PermissionDenied:row=None
    if row:
        DispositivoRecordado.objects.filter(pk=row.pk).update(revocado=True,remoto_pendiente=True,ultimo_uso=timezone.now())
        SesionVendedorPortal.objects.filter(dispositivo=row).update(revocado=True,token_urban='',datos={})
        current=getattr(request,'midistri_tab',None)
        if current and current.dispositivo_id==row.pk:
            current.revocado=True;current.token_urban='';current.datos={}
    response.delete_cookie(COOKIE,path='/portal/',samesite='Lax')
    response.delete_cookie(OLVIDO,path='/portal/',samesite='Lax')
    response['Cache-Control']='private, no-store'
    if row:conciliar()
    return response


def recordar_acceso(request,response,tab,nuevo=False):
    if nuevo and (request.COOKIES.get(COOKIE) or request.COOKIES.get(OLVIDO)):
        olvidar(request,response)
    if not activo():return response
    pending=dict(request.session.get('midistri_dispositivo_pendiente',{}))
    ident=str(tab.pk)
    value=pending.get(ident)
    if not isinstance(value,str):
        value=str(uuid4())+'.'+secrets.token_urlsafe(32)
        pending[ident]=value
        request.session['midistri_dispositivo_pendiente']=pending
    try:
        capacidades()
        result=api('seller-device-remember',method='POST',data={'credencial':value},token=tab.token_urban)
        device_id,fingerprint=partes(value)
        if result.get('version')!=1 or result.get('dispositivo')!=device_id:
            raise ApiError('Respuesta de dispositivo no valida.')
        row,created=DispositivoRecordado.objects.get_or_create(pk=device_id,defaults={'hash_cookie':fingerprint})
        if row.revocado or not secrets.compare_digest(row.hash_cookie,fingerprint):
            raise PermissionDenied('Ese dispositivo fue olvidado.')
        tab.dispositivo=row
        tab.save(update_fields=['dispositivo'])
        pending.pop(ident,None);request.session['midistri_dispositivo_pendiente']=pending
        cookie(response,value)
        import json
        data=json.loads(response.content.decode('utf-8'));data['dispositivo_recordado']=True
        response.content=json.dumps(data)
    except (ApiError,PermissionDenied):
        # Authentication already succeeded. A transport failure never logs the
        # seller out and the same pending credential makes retries idempotent.
        pass
    return response


def opciones(value):
    result=api('seller-device-profiles',method='POST',data={'credencial':value})
    identities=result.get('identidades')
    if result.get('version')!=1 or not isinstance(identities,list) or not 1<=len(identities)<=100:
        raise ApiError('Respuesta de perfiles no valida.')
    for item in identities:
        if (not isinstance(item,dict) or item.get('tipo')!='vendedor' or
            any(type(item.get(k)) is not int or item[k]<1 for k in ('vendedor_id','distribuidora_id')) or
            any(not isinstance(item.get(k),str) or not 1<=len(item[k])<=150 for k in ('seleccion','nombre','distribuidora'))):
            raise ApiError('Respuesta de perfiles no valida.')
    return identities
