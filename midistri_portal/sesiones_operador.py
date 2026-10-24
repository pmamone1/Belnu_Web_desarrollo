"""Server-side store sessions, kept separate without merging delegated scopes."""
from django.conf import settings
from django.db import transaction

def token_operador(request):
    if hasattr(request,'midistri_operador_token'):return request.midistri_operador_token
    selected=request.POST.get('distribuidora') or request.GET.get('distribuidora')
    match=getattr(request,'resolver_match',None)
    if not selected and match:selected=match.kwargs.get('distribuidora')
    rows=request.session.get('midistri_operador_sesiones',{})
    token=rows.get(str(selected)) if isinstance(rows,dict) and selected else None
    return token or request.session.get('midistri_operador_token')

def tokens_operador(request):
    rows=request.session.get('midistri_operador_sesiones',{})
    values=list(rows.values()) if isinstance(rows,dict) else []
    values.append(request.session.get('midistri_operador_token'))
    return {t for t in values if isinstance(t,str) and t}

def borrar_token(request,token):
    rows=request.session.get('midistri_operador_sesiones',{})
    if isinstance(rows,dict):request.session['midistri_operador_sesiones']={k:v for k,v in rows.items() if v!=token}
    if request.session.get('midistri_operador_token')==token:request.session.pop('midistri_operador_token',None)

@transaction.atomic
def guardar_operador(request,perfil,token,limpiar):
    # Refresh the current DB session under a row lock before merging same-user
    # store sessions. Never union the permissions or scopes inside the tokens.
    if request.session.session_key and getattr(settings,'SESSION_ENGINE','django.contrib.sessions.backends.db')=='django.contrib.sessions.backends.db':
        from django.contrib.sessions.models import Session
        Session.objects.select_for_update().filter(session_key=request.session.session_key).first()
        request.session.update(request.session.load())
    mismo=request.session.get('midistri_operador_id')==perfil['operador_id']
    rows=request.session.get('midistri_operador_sesiones',{}) if mismo else {}
    rows=dict(rows) if isinstance(rows,dict) else {}
    if not mismo:
        limpiar(request)
        request.session.cycle_key()
    for d in perfil['distribuidoras']:rows[str(d['id'])]=token
    request.session['midistri_operador_id']=perfil['operador_id']
    request.session['midistri_operador_sesiones']=rows
    request.session['midistri_operador_token']=token
    request.session.set_expiry(0)
    if mismo:
        request.session.save()
        # Avoid a later middleware write overwriting a second completed callback.
        request.session.modified=False
