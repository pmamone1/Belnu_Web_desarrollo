"""Validate the private API contract before saving vendor information."""
from decimal import Decimal, InvalidOperation
from uuid import UUID
from .client import ApiError

def perfil_valido(data):
    try:
        if not isinstance(data,dict):raise ValueError
        for key in ('id','distribuidora_id'):
            if type(data[key]) is not int or data[key]<1:raise ValueError
        for key,limit in (('nombre',150),('distribuidora',150),('linea',120)):
            if not isinstance(data[key],str) or len(data[key])>limit:raise ValueError
        for key in ('lin','vv'):
            if data.get(key) is not None and (type(data[key]) is not int or data[key]<0):raise ValueError
    except (KeyError,ValueError,TypeError):
        raise ApiError('No se pudo validar tu acceso. Conservamos la sesión para reintentar.') from None
    return data

def pedido_valido(data,perfil,ident=None):
    try:
        if not isinstance(data,dict):raise ValueError
        UUID(data['id'])
        if ident is not None and data['id']!=str(ident):raise ValueError
        if data['vendedor_id']!=perfil['id'] or data['distribuidora_id']!=perfil['distribuidora_id']:raise ValueError
        if type(data['vendedor_id']) is not int or type(data['distribuidora_id']) is not int:raise ValueError
        if data['estado'] not in ('recibido','ok','cancelado','emitido'):raise ValueError
        if not isinstance(data['vendedor'],str) or not 1<=len(data['vendedor'])<=150:raise ValueError
        items=data['items']
        if not isinstance(items,list) or not 1<=len(items)<=200:raise ValueError
        clean=[]
        for item in items:
            if type(item['producto_id']) is not int or item['producto_id']<1:raise ValueError
            if type(item['cantidad']) is not int or not 1<=item['cantidad']<=9999:raise ValueError
            for key,limit in (('nombre',200),('codigo',80)):
                if not isinstance(item[key],str) or len(item[key])>limit:raise ValueError
            for key in ('precio','pvp'):
                price=Decimal(str(item[key]))
                if not price.is_finite() or price<0 or price!=price.quantize(Decimal('.01')):raise ValueError
            clean.append({k:item[k] for k in ('producto_id','cantidad','nombre','codigo','precio','pvp')})
    except (KeyError,ValueError,TypeError,InvalidOperation,AttributeError):
        raise ApiError('No se pudo validar la respuesta del pedido. Conservamos el intento para reintentar.') from None
    result={k:data[k] for k in ('id','vendedor_id','distribuidora_id','vendedor','estado')}
    result.update(items=clean)
    for key in ('distribuidora','linea','lin','vv','creado','pedidos'):
        if key in data:result[key]=data[key]
    return result
