"""Bounded, actor-scoped report preparation from a private frozen Urban source."""
from datetime import timedelta
from decimal import Decimal,InvalidOperation
import re
from uuid import UUID
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_date,parse_datetime
from .client import api,ApiError
from .models import ConsultaAnalitica

PERMISOS={'pedidos.gestionar','midistri.tienda_configurar'}

def alcance(perfil,did):
    if not PERMISOS<=set(perfil.get('permisos',[])):raise ApiError('No tiene permiso para consultar estadísticas.',403)
    if type(did) is not int:raise ApiError('Distribuidora inválida.',403)
    ds={d['id']:d['nombre'] for d in perfil['distribuidoras']}
    if did not in ds:raise ApiError('Distribuidora fuera de alcance.',403)
    amba={i for i,n in ds.items() if re.search(r'(?<!\d)(?:20|65)(?!\d)',n.lower())}
    return sorted(amba if did in amba else {did})

def fechas(datos):
    try:
        a=parse_date(str(datos['desde']));b=parse_date(str(datos['hasta']))
        if a is None or b is None or a>b or b.year>=9999:raise ValueError
        return a,b
    except (KeyError,ValueError,TypeError):raise ApiError('Revise las fechas Desde/Hasta.',400) from None

def cargar_consulta(ident,perfil,lock=False):
    try:ident=UUID(str(ident))
    except (TypeError,ValueError):raise ApiError('Consulta inválida.',400) from None
    qs=ConsultaAnalitica.objects.select_for_update() if lock else ConsultaAnalitica.objects
    q=qs.filter(pk=ident,operador_id=perfil['operador_id'],vence__gt=timezone.now()).first()
    if q is None:raise ApiError('La consulta venció o pertenece a otro usuario; vuelva a consultar.',403)
    if q.distribuidoras!=alcance(perfil,q.distribuidora_id):raise ApiError('Cambió el alcance; vuelva a consultar.',403)
    return q

def iniciar_consulta(request,perfil,datos):
    try:
        raw=datos['distribuidora']
        if type(raw) is bool:raise ValueError
        did=int(raw)
    except (ValueError,TypeError,KeyError):raise ApiError('Distribuidora inválida.',400) from None
    ids=alcance(perfil,did);a,b=fechas(datos);now=timezone.now()
    old=list(ConsultaAnalitica.objects.filter(operador_id=perfil['operador_id'],vence__lt=now).values_list('pk',flat=True)[:100])
    if old:ConsultaAnalitica.objects.filter(pk__in=old,operador_id=perfil['operador_id']).delete()
    return ConsultaAnalitica.objects.create(operador_id=perfil['operador_id'],distribuidora_id=did,distribuidoras=ids,desde=a,hasta=b,
        datos={'vendedores':[],'pedidos':[]},vence=now+timedelta(minutes=15))

def _fecha(value):
    try:
        dt=parse_datetime(value)
        if dt is None or timezone.is_naive(dt):raise ValueError
        return dt
    except (ValueError,TypeError):raise ApiError('La fuente devolvió una fecha incompatible.',503) from None

def _vendedor(row,ids):
    keys=('id','distribuidora_id','nombre','lin','vv','activo','actual','contacto','pedidos_historicos')
    if not isinstance(row,dict) or not set(keys)<=set(row):raise ValueError
    if type(row['id']) is not int or row['id']<1 or type(row['distribuidora_id']) is not int or row['distribuidora_id'] not in ids:raise ValueError
    if not isinstance(row['nombre'],str) or len(row['nombre'])>150:raise ValueError
    if any(row[k] is not None and (type(row[k]) is not int or row[k]<0) for k in ('lin','vv')):raise ValueError
    if any(type(row[k]) is not bool for k in ('activo','actual','contacto')) or type(row['pedidos_historicos']) is not int or row['pedidos_historicos']<0:raise ValueError
    return {k:row[k] for k in keys}

def _pedido(row,ids,corte):
    keys=('id','vendedor_id','distribuidora_id','vendedor','creado','referencia','estado','items','total_solicitado','total_confirmado','unidades_solicitadas','unidades_confirmadas','atencion','conciliacion')
    if not isinstance(row,dict) or not set(keys)<=set(row):raise ValueError
    UUID(row['id'])
    if type(row['vendedor_id']) is not int or row['vendedor_id']<1 or type(row['distribuidora_id']) is not int or row['distribuidora_id'] not in ids:raise ValueError
    if row['estado'] not in ('recibido','ok','emitido','cancelado') or type(row['conciliacion']) is not bool:raise ValueError
    if any(not isinstance(row[k],str) or len(row[k])>180 for k in ('vendedor','referencia')):raise ValueError
    if _fecha(row['creado'])>corte:raise ValueError
    if not isinstance(row['items'],list) or len(row['items'])>200:raise ValueError
    # Only public historical order fields cross this boundary.
    items=[]
    for x in row['items']:
        if type(x.get('producto_id')) is not int or type(x.get('cantidad')) is not int or x['cantidad']<1:raise ValueError
        for k in ('precio','pvp'):
            number=Decimal(str(x[k]))
            if not number.is_finite() or number<0:raise ValueError
        items.append({k:x.get(k) for k in ('producto_id','nombre','codigo','cantidad','precio','pvp')})
    if not row['conciliacion']:
        for k in ('total_solicitado','total_confirmado'):
            number=Decimal(str(row[k]))
            if not number.is_finite() or number<0:raise ValueError
        if Decimal(row['total_confirmado'])>Decimal(row['total_solicitado']):raise ValueError
        if any(type(row[k]) is not int or row[k]<0 for k in ('unidades_solicitadas','unidades_confirmadas')):raise ValueError
        if row['unidades_confirmadas']>row['unidades_solicitadas']:raise ValueError
    result={k:row[k] for k in keys};result['items']=items;return result

def progreso(q):
    total=sum(q.meta.get('totales',{}).values());loaded=sum(len(v) for v in q.datos.values())
    return {'id':str(q.pk),'listo':q.completa,'revision':q.revision,'cargadas':loaded,'total':total,'fase':q.fase}

@transaction.atomic
def avanzar_consulta(request,ident,revision,perfil):
    q=cargar_consulta(ident,perfil,lock=True)
    if type(revision) is not int or revision<0:raise ApiError('Revisión inválida.',400)
    if q.completa or revision!=q.revision:return progreso(q)
    params={'distribuidora':q.distribuidora_id,'desde':q.desde.isoformat(),'hasta':q.hasta.isoformat(),'fase':q.fase,'cursor':q.cursor}
    if q.fuente:params['snapshot']=str(q.fuente)
    data=api('operator-analytics-source',method='POST',data=params,operator_token=request.midistri_operador_token)
    try:
        if data['version']!=1 or data['fase']!=q.fase or type(data['cursor']) is not int or data['cursor']!=q.cursor:raise ValueError
        if data['desde']!=q.desde.isoformat() or data['hasta']!=q.hasta.isoformat():raise ValueError
        ds=data['distribuidoras']
        if not isinstance(ds,list) or sorted(d['id'] for d in ds)!=q.distribuidoras or any(not isinstance(d['nombre'],str) for d in ds):raise ValueError
        snap=UUID(data['snapshot']);cut=_fecha(data['corte']);expires=_fecha(data['vence'])
        if cut>timezone.now()+timedelta(minutes=2) or expires<=timezone.now():raise ValueError
        totals=data['totales']
        if set(totals)!={'vendedores','pedidos'} or any(type(n) is not int or not 0<=n<=20000 for n in totals.values()):raise ValueError
        if q.fuente and (q.fuente!=snap or data['corte']!=q.meta['corte'] or totals!=q.meta['totales']):raise ValueError
        raw=data['filas'];nxt=data['siguiente']
        if not isinstance(raw,list) or len(raw)>500 or (nxt is not None and (type(nxt) is not int or nxt!=q.cursor+len(raw))):raise ValueError
        rows=[_vendedor(r,q.distribuidoras) for r in raw] if q.fase=='vendedores' else [_pedido(r,q.distribuidoras,cut) for r in raw]
        complete=q.cursor+len(rows)
        if complete>totals[q.fase] or (nxt is None and complete!=totals[q.fase]) or (nxt is not None and (not rows or complete>=totals[q.fase])):raise ValueError
        existing=q.datos[q.fase]
        key=lambda r:(r['distribuidora_id'],r['id'])
        keys=[key(r) for r in existing+rows]
        if len(keys)!=len(set(keys)):raise ValueError
    except (ValueError,KeyError,TypeError,InvalidOperation,AttributeError):raise ApiError('La fuente está incompleta o cambió; vuelva a consultar. No se mostraron ceros como resultados.',503) from None
    from .analitica_cobertura import congelar
    local=q.meta.get('local') if q.fuente else congelar(q.distribuidoras,cut)
    q.fuente=snap;q.meta={k:data[k] for k in ('version','corte','distribuidoras','totales')};q.vence=min(q.vence,expires);q.meta['local']=local
    q.datos[q.fase].extend(rows);q.revision+=1
    if nxt is not None:q.cursor=nxt
    elif q.fase=='vendedores':q.fase='pedidos';q.cursor=0
    else:q.completa=True
    q.save();return progreso(q)
