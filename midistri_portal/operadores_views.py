"""Distributor pages use delegated identities, never Django staff elevation."""
import secrets
from urllib.parse import urlencode
from django.conf import settings
from django.core import signing
from django.contrib.auth import logout
from django.http import HttpResponse
from django.shortcuts import redirect,render
from django.views.decorators.http import require_GET,require_POST
from django.views.decorators.csrf import csrf_exempt
from . import operadores as op
from .client import ApiError
SALT='midistri.operador.desafio.v1'

def fallo(request,error):
    if error.status==401:return redirect('midistri_operador_entrada')
    return render(request,'midistri_portal/operador_base.html',{'error':str(error)},
                  status=403 if error.status==403 else 503)

@require_GET
def entrada(request):
    if not op.habilitado():return HttpResponse('Administración de MiDistri desactivada.',status=503)
    nonce=secrets.token_urlsafe(32)
    try:url=op.origen_urban()+'/midistri/administrar/?'+urlencode({'desafio':nonce})
    except ApiError as e:return fallo(request,e)
    response=redirect(url)
    response.set_cookie('midistri_desafio',signing.dumps(nonce,salt=SALT),max_age=120,
        secure=True,httponly=True,samesite='None',path='/portal/administrar/')
    return response

@csrf_exempt
@require_POST
def completar(request):
    if not op.habilitado():return HttpResponse('Administración de MiDistri desactivada.',status=503)
    try:
        if request.headers.get('Origin')!=op.origen_urban():raise ValueError
        nonce=signing.loads(request.COOKIES.get('midistri_desafio',''),salt=SALT,max_age=120)
        sent=request.POST.get('desafio','');code=request.POST.get('codigo','')
        if not isinstance(nonce,str) or not 20<=len(sent)<=100 or not secrets.compare_digest(nonce,sent):raise ValueError
        if not 20<=len(code)<=100:raise ValueError
    except (ValueError,signing.BadSignature):
        return HttpResponse('El acceso no pertenece a este navegador. Ingrese desde Urban Soft.',status=403)
    try:
        result=op.api('operator-exchange',method='POST',data={'codigo':code,'desafio':sent})
        op.perfil_valido(result['perfil'])
        token=result['session_token']
        if not isinstance(token,str) or not 20<=len(token)<=100:raise ApiError('Respuesta de acceso inválida.')
    except (KeyError,TypeError):return fallo(request,ApiError('Respuesta de acceso inválida.'))
    except ApiError as e:return fallo(request,e)
    logout(request)
    request.session.cycle_key()
    request.session['midistri_operador_token']=token
    request.session.set_expiry(8*60*60)
    response=redirect('midistri_operador_panel')
    response.delete_cookie('midistri_desafio',path='/portal/administrar/',samesite='None')
    return response

@require_GET
def panel(request):
    try:perfil=op.perfil_operador(request)
    except ApiError as e:return fallo(request,e)
    return render(request,'midistri_portal/operador_base.html',{'operador':perfil})

@require_POST
def salir(request):
    token=request.session.get('midistri_operador_token')
    if token:
        try:op.api('operator-logout',method='POST',operator_token=token)
        except ApiError:pass
    logout(request)
    return redirect('midistri_catalogo')
