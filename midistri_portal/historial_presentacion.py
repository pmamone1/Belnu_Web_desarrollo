"""Read-only presentation of an already validated order snapshot."""
from decimal import Decimal

def resumen_pedido(pedido):
    data=pedido.respuesta or {};items=data.get('items',pedido.datos.get('items',[]))
    attention=data.get('atencion') or {};detail=bool(attention and attention.get('estado')!='pendiente')
    final=pedido.estado=='emitido' or detail
    unknown=pedido.estado=='emitido' and not detail
    accepted={i['producto_id']:i['cantidad_preparada'] for i in attention.get('items',[])} if detail else {}
    review=data.get('revision_comercial') or {}
    if not final:accepted={i['producto_id']:i['cantidad_preparada'] for i in review.get('cantidades',[])}
    rows=[];requested=Decimal('0');current=Decimal('0');known=False
    for item in items:
        quantity=item['cantidad'];price=Decimal(str(item['precio']));requested+=price*quantity
        amount=0 if pedido.estado=='cancelado' else accepted.get(item['producto_id'])
        if amount is not None:known=True;current+=price*amount
        rows.append(dict(nombre=item.get('nombre') or str(item['producto_id']),codigo=item.get('codigo',''),solicitada=quantity,aceptada=amount,faltante=quantity-amount if amount is not None else None,precio=price))
    return dict(filas=rows,total_solicitado=requested,total_vigente=current if known or pedido.estado=='cancelado' else None,finalizado=final,sin_desglose=unknown,motivo=(data.get('anulacion') or {}).get('motivo') or review.get('motivo',''))
