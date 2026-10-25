from decimal import Decimal, InvalidOperation
from urllib.parse import urlsplit
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from .models import Distribuidora,Publicacion,Sincronizacion


def validar_snapshot(data):
    try:
        if data['version']!=1 or data['completo'] is not True:raise ValueError
        ds=data['distribuidoras'];ps=data['publicaciones']
        if not isinstance(ds,list) or not isinstance(ps,list) or len(ds)>1000 or len(ps)>10000:raise ValueError
        ids=set();seen=set();rows=[]
        for d in ds:
            if type(d['id']) is not int or d['id']<1 or d['id'] in ids or not isinstance(d['nombre'],str) or not 1<=len(d['nombre'])<=150:raise ValueError
            ids.add(d['id'])
        base=urlsplit(settings.URBAN_API_BASE)
        for p in ps:
            did=p['distribuidora_id'];pid=p['producto_id']
            if type(pid) is not int or pid<1 or did not in ids or (did,pid) in seen:raise ValueError
            seen.add((did,pid))
            for k,limit in [('nombre',200),('codigo',80),('categoria',100)]:
                if not isinstance(p[k],str) or len(p[k])>limit:raise ValueError
            price=Decimal(str(p['precio']));pvp=Decimal(str(p['pvp']))
            if not all(x.is_finite() and 0<=x<Decimal('10000000000') and x==x.quantize(Decimal('.01')) for x in (price,pvp)):raise ValueError
            images=[]
            for i in p.get('imagenes',[]):
                u=urlsplit(i['url'])
                if u.scheme!='https' or u.netloc!=base.netloc or not u.path.startswith('/catalogo-imagenes/') or u.query or u.fragment:raise ValueError
                images.append(i['url'])
            display=p.get('display')
            # Urban allows zero for an unspecified optional presentation.
            if type(display) is int and display == 0:display=None
            if display is not None and (type(display) is not int or display<1):raise ValueError
            from .multimedia_contract import validar_multimedia
            multimedia=validar_multimedia(p.get('multimedia',[]),settings.URBAN_API_BASE)
            indicators=p.get('indicadores',{})
            if indicators:
                if not isinstance(indicators,dict) or set(indicators)!={'ranking','entrega','ultimas_unidades'}:raise ValueError
                rank=indicators['ranking']
                if rank is not None and (type(rank) is not int or not 1<=rank<=10):raise ValueError
                if indicators['entrega'] not in ('24/48','96') or type(indicators['ultimas_unidades']) is not bool:raise ValueError
                if indicators['ultimas_unidades'] and indicators['entrega']!='24/48':raise ValueError
            elif not isinstance(indicators,dict):raise ValueError
            order=p.get('orden_ventas')
            if order is not None and (type(order) is not int or not 1<=order<=1000000):raise ValueError
            indicators=dict(indicators)
            if order is not None:indicators['orden_ventas']=order
            rows.append((did,pid,{'indicadores':indicators,'multimedia':multimedia,'nombre':p['nombre'],'codigo':p['codigo'],'categoria':p['categoria'],
                'precio':price,'pvp':pvp,'imagenes':images,'display':display,'activa':True}))
    except (KeyError,ValueError,TypeError,InvalidOperation,AttributeError):
        raise ValueError('Catálogo incompleto o inválido. Se conserva la última copia válida.') from None
    return ds,rows


@transaction.atomic
def aplicar_snapshot(data):
    ds,rows=validar_snapshot(data)
    stores={}
    try:
        from .comercial_views import validar_config
        from .client import ApiError
        for store in data.get('tiendas',[]):
            did=store['distribuidora_id']
            if did not in {d['id'] for d in ds} or did in stores:raise ValueError
            stores[did]=validar_config(store,did)
    except (KeyError,ValueError,TypeError,ApiError):raise ValueError('Configuración de tienda inválida. Se conserva la copia anterior.') from None
    # All synchronizations lock this singleton before applying a complete snapshot.
    Sincronizacion.objects.get_or_create(pk=1)
    state=Sincronizacion.objects.select_for_update().get(pk=1)
    Distribuidora.objects.update(activa=False);Publicacion.objects.update(activa=False)
    for d in ds:
        defaults={'nombre':d['nombre'],'activa':True}
        if d['id'] in stores:defaults.update({k:stores[d['id']][k] for k in ('nombre_comercial','email_respuesta')})
        Distribuidora.objects.update_or_create(pk=d['id'],defaults=defaults)
    for did,pid,defaults in rows:Publicacion.objects.update_or_create(distribuidora_id=did,producto_id=pid,defaults=defaults)
    state.completada=timezone.now();state.error='';state.save()
    return len(rows)


def sincronizar():
    from .client import api,ApiError
    try:return aplicar_snapshot(api('snapshot'))
    except (ApiError,ValueError) as e:
        Sincronizacion.objects.update_or_create(pk=1,defaults={'error':str(e)[:150]})
        raise
