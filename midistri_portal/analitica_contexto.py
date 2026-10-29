"""Short-lived page attestation; no Urban request is needed for each photo."""
from django.core import signing
from django.core.exceptions import PermissionDenied
from .analitica_captura import activa,_actor
from .contract import perfil_valido
SALT='midistri.analitica.contexto.v1'

def contexto(request,perfil):
    if not perfil or not activa():return None
    actor=_actor(request,perfil)
    if not actor:return None
    clean={k:perfil.get(k) for k in ('id','nombre','distribuidora_id','distribuidora','linea','lin','vv')}
    return {'firma':signing.dumps({'perfil':clean,'actor':actor},salt=SALT,compress=True),'actor':actor}

def perfil_firmado(request,firma):
    data=signing.loads(firma,salt=SALT,max_age=300)
    perfil=perfil_valido(data['perfil']);request.midistri_perfil=perfil
    row=getattr(request,'midistri_tab',None)
    if row and (perfil['id']!=row.vendedor_id or perfil['distribuidora_id']!=row.distribuidora_id):raise PermissionDenied
    if _actor(request,perfil)!=data['actor']:raise PermissionDenied
    return perfil
