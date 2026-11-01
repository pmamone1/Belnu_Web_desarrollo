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

def pedido_valido(data,perfil,ident=None,anterior=None):
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
    if len({i['producto_id'] for i in clean})!=len(clean):raise ApiError('Productos repetidos en el pedido.')
    if 'contrato_pedido' in data or 'atencion' in data:
        if type(data.get('contrato_pedido')) is not int or data['contrato_pedido']!=2:raise ApiError('Contrato de pedido incompatible.')
        result.update(contrato_pedido=2,atencion=atencion_valida(clean,data.get('atencion'),data['estado']))
    if 'email_estado' in data:
        if not isinstance(data['email_estado'],str) or len(data['email_estado'])>30:raise ApiError('Estado de Email inválido.')
        result['email_estado']=data['email_estado']
    from .referencias import validar_referencia
    result.update(validar_referencia(data,anterior))
    if data.get('revision_comercial') is not None:
        try:
            rev=data['revision_comercial'];rows=rev['cantidades'];limits={i['producto_id']:i['cantidad'] for i in clean}
            if type(rev['numero']) is not int or rev['numero']<1 or not isinstance(rev['motivo'],str) or len(rev['motivo'])>500:raise ValueError
            if not isinstance(rows,list) or len(rows)!=len(clean):raise ValueError
            seen=set()
            for row in rows:
                if set(row)!={'producto_id','cantidad_preparada'}:raise ValueError
                pid=row['producto_id'];qty=row['cantidad_preparada']
                if type(pid) is not int or pid not in limits or pid in seen or type(qty) is not int or not 0<=qty<=limits[pid]:raise ValueError
                seen.add(pid)
            result['revision_comercial']={'numero':rev['numero'],'motivo':rev['motivo'],'cantidades':[dict(r) for r in rows]}
        except (ValueError,KeyError,TypeError):raise ApiError('Revisión comercial inválida.') from None
    if data.get('anulacion') is not None:
        try:
            from datetime import datetime
            row=data['anulacion']
            if not isinstance(row,dict) or set(row)!={'completa','motivo','fecha'}:raise ValueError
            if type(row['completa']) is not bool or row['completa']!=(data['estado']=='cancelado'):raise ValueError
            if data['estado'] not in ('emitido','cancelado') or not isinstance(row['motivo'],str) or not 5<=len(row['motivo'])<=2000:raise ValueError
            if not isinstance(row['fecha'],str) or len(row['fecha'])>50 or datetime.fromisoformat(row['fecha']).tzinfo is None:raise ValueError
            result['anulacion']=dict(row)
        except (KeyError,ValueError,TypeError):raise ApiError('Anulación de pedido inválida.') from None
    if 'modalidades_pedidos' in data:
        from .modalidades import modalidades_validas
        result['modalidades_pedidos']=modalidades_validas(data['modalidades_pedidos'],data.get('pedidos'))
    result.update(items=clean)
    for key in ('distribuidora','linea','lin','vv','creado','pedidos'):
        if key in data:result[key]=data[key]
    return result


def atencion_valida(items,data,estado=None):
    try:
        if not isinstance(data,dict) or type(data.get('version')) is not int or data['version']!=1:raise ValueError
        rows=data['items']
        original={i['producto_id']:i for i in items}
        if len(original)!=len(items) or not isinstance(rows,list) or len(rows)!=len(original):raise ValueError
        seen=set();prepared=Decimal('0');requested=Decimal('0');n=0;c=0
        pending=data['estado']=='pendiente'
        for row in rows:
            pid=row['producto_id'];p=row['cantidad_preparada'];x=row['cantidad_cancelada']
            if type(pid) is not int or pid in seen or pid not in original or type(p) is not int or type(x) is not int:raise ValueError
            item=original[pid];seen.add(pid)
            if p<0 or x<0 or p+x>item['cantidad']:raise ValueError
            if pending:
                if p or x:raise ValueError
            elif p+x!=item['cantidad']:raise ValueError
            n+=p;c+=x;prepared+=Decimal(str(item['precio']))*p;requested+=Decimal(str(item['precio']))*item['cantidad']
        expected='pendiente' if pending else ('cancelada' if not n else 'parcial' if c else 'total')
        if data['estado']!=expected:raise ValueError
        if estado is not None:
            if (estado in ('ok','recibido')) != pending:raise ValueError
            if estado=='cancelado' and expected!='cancelada':raise ValueError
            if estado=='emitido' and expected not in ('total','parcial'):raise ValueError
        for key,total in (('total_preparado',prepared),('total_solicitado',requested)):
            if not isinstance(data[key],str) or Decimal(data[key])!=total:raise ValueError
        return {'version':1,'estado':expected,'items':[{k:r[k] for k in ('producto_id','cantidad_preparada','cantidad_cancelada')} for r in rows],
            'total_solicitado':format(requested,'.2f'),'total_preparado':format(prepared,'.2f')}
    except (KeyError,TypeError,ValueError,InvalidOperation):
        raise ApiError('No se pudo conciliar la preparación del pedido. No se guardaron los datos recibidos.') from None
