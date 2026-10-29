"""Local bounded telemetry; financial operations do not depend on this log."""
from datetime import timedelta
from hashlib import sha256
import json,logging
from uuid import UUID,uuid4,uuid5,NAMESPACE_URL
from types import SimpleNamespace
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from .models import ControlAnalitica,IntervaloAnalitico,SesionAnalitica,EventoAnalitico,Distribuidora,Publicacion
from .catalogo_elegible import elegibles

CLIENTE={'producto_consulta','foto_ampliada','video_mp4','video_enlace'}
TIPOS=CLIENTE|{'ingreso','catalogo','carrito','pedido','carrito_visto','pedidos_vistos','pedido_visto'}

def activa():return ControlAnalitica.objects.filter(pk=1,activa=True).exists()

@transaction.atomic
def cambiar_estado(valor):
    if type(valor) is not bool:raise ValidationError('Estado de captura inválido.')
    control,_=ControlAnalitica.objects.get_or_create(pk=1)
    control=ControlAnalitica.objects.select_for_update().get(pk=1)
    now=timezone.now()
    if valor:
        from .analitica_cobertura import guardar_previos
        guardar_previos()
        for did in Distribuidora.objects.filter(activa=True).values_list('pk',flat=True):
            IntervaloAnalitico.objects.get_or_create(distribuidora_id=did,hasta__isnull=True,defaults={'desde':now})
    else:IntervaloAnalitico.objects.filter(hasta__isnull=True).update(hasta=now)
    if control.activa!=valor:control.activa=valor;control.cambiado=now;control.save(update_fields=['activa','cambiado'])
    return {'activa':valor,'intervalos_abiertos':IntervaloAnalitico.objects.filter(hasta__isnull=True).count()}

def _actor(request,perfil):
    if not perfil or request.path.startswith(('/portal/administrar/','/portal/gestion/')):return None
    if any(type(perfil.get(k)) is not int or perfil[k]<1 for k in ('id','distribuidora_id')):raise ValidationError('Perfil inválido.')
    if getattr(request,'midistri_perfil',None)!=perfil:raise ValidationError('Falta perfil validado.')
    token=request.session.get('midistri_token')
    if not token:return None
    tab=str(getattr(getattr(request,'midistri_tab',None),'pk','heredada'))
    return sha256((tab+':'+str(perfil['id'])+':'+str(perfil['distribuidora_id'])+':'+token).encode()).hexdigest()

def _datos(perfil,tipo,producto,recurso,cantidad,pedido):
    if tipo not in TIPOS:raise ValidationError('Acción no válida.')
    p=None
    if tipo in CLIENTE or tipo=='carrito':
        if type(producto) is not int or producto<1:raise ValidationError('Producto inválido.')
        p=elegibles(Publicacion.objects.filter(producto_id=producto,distribuidora_id=perfil['distribuidora_id'])).first()
        if p is None:raise ValidationError('Producto no disponible en esta tienda.')
    elif producto is not None or recurso is not None:raise ValidationError('Recurso inesperado.')
    if tipo in ('foto_ampliada','video_mp4','video_enlace'):
        if type(recurso) is not int or not 0<=recurso<len(p.multimedia):raise ValidationError('Recurso inválido.')
        item=p.multimedia[recurso];kind=item.get('tipo')
        if (tipo=='foto_ampliada' and kind!='foto') or (tipo=='video_mp4' and kind!='mp4') or (tipo=='video_enlace' and kind not in ('youtube','vimeo')):raise ValidationError('Tipo de recurso inválido.')
    elif recurso is not None:raise ValidationError('Recurso inesperado.')
    if tipo=='carrito':
        if type(cantidad) is not int or not 0<=cantidad<=9999:raise ValidationError('Cantidad inválida.')
    elif cantidad is not None:raise ValidationError('Cantidad inesperada.')
    if tipo=='pedido':
        try:pedido=str(UUID(str(pedido)))
        except (ValueError,TypeError):raise ValidationError('Pedido inválido.') from None
    elif pedido is not None:raise ValidationError('Pedido inesperado.')
    return p,pedido

@transaction.atomic
def _registrar(request,perfil,tipo,producto=None,recurso=None,cantidad=None,pedido=None,event_id=None):
    clave=_actor(request,perfil)
    if not clave or not activa():return None
    from .analitica_cobertura import conciliar_fallo
    conciliar_fallo()
    p,pedido=_datos(perfil,tipo,producto,recurso,cantidad,pedido)
    try:ident=UUID(str(event_id)) if event_id else uuid4()
    except (ValueError,TypeError):raise ValidationError('Identificador de acción inválido.') from None
    data=[perfil['distribuidora_id'],perfil['id'],tipo,producto,recurso,cantidad,pedido]
    huella=sha256(json.dumps(data,separators=(',',':')).encode()).hexdigest()
    old=EventoAnalitico.objects.filter(pk=ident).first()
    if old:
        if old.huella!=huella:raise ValidationError('La acción ya existe con otros datos.')
        return old
    now=timezone.now()
    # A unique cursor serializes one tab+actor without holding a global lock.
    SesionAnalitica.objects.get_or_create(clave=clave,defaults={'vendedor_id':perfil['id'],'distribuidora_id':perfil['distribuidora_id'],'ultima':now,'cupo_inicio':now})
    ses=SesionAnalitica.objects.select_for_update().get(pk=clave)
    old=EventoAnalitico.objects.filter(pk=ident).first()
    if old:
        if old.huella!=huella:raise ValidationError('La acción ya existe con otros datos.')
        return old
    if now-ses.ultima>=timedelta(minutes=30):ses.visita=uuid4()
    if now-ses.cupo_inicio>=timedelta(minutes=1):ses.cupo=0;ses.cupo_inicio=now
    if ses.cupo>=100:raise ValidationError('Demasiadas acciones; reintente más tarde.')
    ses.cupo+=1;ses.ultima=now;ses.save()
    IntervaloAnalitico.objects.get_or_create(distribuidora_id=perfil['distribuidora_id'],hasta__isnull=True,defaults={'desde':now})
    return EventoAnalitico.objects.create(id=ident,fecha=now,distribuidora_id=perfil['distribuidora_id'],vendedor_id=perfil['id'],vendedor=perfil.get('nombre','')[:150],
        visita=ses.visita,tipo=tipo,producto_id=producto,producto=p.nombre if p else '',sku=(p.codigo or '') if p else '',recurso=recurso,cantidad=cantidad,pedido=pedido,huella=huella)

def registrar(request,perfil,tipo,**kwargs):
    try:return _registrar(request,perfil,tipo,**kwargs)
    except Exception:
        logging.getLogger('midistri.analytics').warning('capture_failed; activity may be incomplete')
        from .analitica_cobertura import marcar_fallo
        if perfil and type(perfil.get('distribuidora_id')) is int:marcar_fallo(perfil['distribuidora_id'])
        return None

@transaction.atomic
def recibir_lote(request,perfil,events):
    if not isinstance(events,list) or not 1<=len(events)<=20:raise ValidationError('El lote admite entre1 y20 acciones.')
    for e in events:
        if not isinstance(e,dict) or set(e)-{'id','tipo','producto','recurso'} or not {'id','tipo','producto'}<=set(e) or e['tipo'] not in CLIENTE:
            raise ValidationError('Datos de acción inválidos.')
    rows=[_registrar(request,perfil,e['tipo'],producto=e['producto'],recurso=e.get('recurso'),event_id=e['id']) for e in events]
    return {'aceptados':sum(r is not None for r in rows),'activa':activa()}

def registrar_ingreso(request,perfil,token,tab=None):
    from .analitica_cobertura import acreditar
    acreditar(perfil['id'],perfil['distribuidora_id'])
    context=SimpleNamespace(path='/portal/',session={'midistri_token':token},midistri_perfil=perfil,midistri_tab=SimpleNamespace(pk=tab) if tab else None)
    ident=uuid5(NAMESPACE_URL,'midistri-ingreso:'+sha256(token.encode()).hexdigest())
    return registrar(context,perfil,'ingreso',event_id=ident)
