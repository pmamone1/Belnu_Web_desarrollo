"""Validate admin responses before rendering, independent of vendor identities."""
from decimal import Decimal, InvalidOperation
from .client import ApiError
from .services import validar_snapshot
from .contract import pedido_valido

def catalogo_valido(data,did):
    try:
        if data['version']!=1:raise ValueError
        for k in ('total','pagina','paginas'):
            if type(data[k]) is not int or data[k]<(0 if k=='total' else 1):raise ValueError
        if not isinstance(data['productos'],list) or len(data['productos'])>50:raise ValueError
        products=[]
        for p in data['productos']:
            if type(p['publicado']) is not bool:raise ValueError
            products.append({'producto_id':p['id'],'distribuidora_id':did,'nombre':p['nombre'],
                'codigo':p['sku'],'categoria':'','precio':str(abs(Decimal(str(p['precio'])))),'pvp':str(abs(Decimal(str(p['pvp'])))),
                'imagenes':p['imagenes'],'display':None})
        # Validate structure/finite money without hiding correctable negative master values.
        # Return original values; the Urban publication preview excludes invalid prices.
        validar_snapshot({'version':1,'completo':True,'distribuidoras':[{'id':did,'nombre':'Tienda'}],'publicaciones':products})
        providers=data['proveedores']
        if not isinstance(providers,list) or len(providers)>10000:raise ValueError
        for p in providers:
            if type(p['id']) is not int or p['id']<1 or not isinstance(p['nombre'],str) or len(p['nombre'])>150:raise ValueError
        return {k:data[k] for k in ('total','pagina','paginas','productos','proveedores')}
    except (ValueError,KeyError,TypeError,InvalidOperation):
        raise ApiError('Catálogo administrativo inválido. No se muestran datos sin validar.') from None

def pedido_admin_valido(row,did,ident=None):
    try:
        result=pedido_valido(row,{'id':row['vendedor_id'],'distribuidora_id':did},ident)
        return result
    except (KeyError,TypeError):raise ApiError('Pedido administrativo inválido.') from None
