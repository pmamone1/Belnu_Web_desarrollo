"""Urban owns the folio. Legacy responses cannot erase an accepted reference."""
from datetime import datetime
from .client import ApiError
CAMPOS=('referencia_version','numero','codigo','fecha_pedido','referencia')

def validar_referencia(data,anterior=None):
    previous={k:anterior[k] for k in CAMPOS if k in (anterior or {})}
    if not any(k in data for k in CAMPOS):return previous
    try:
        if data.get('referencia_version')!=1 or type(data['referencia_version']) is not int:raise ValueError
        n=data['numero']
        if type(n) is not int or not 0<n<=9223372036854775807:raise ValueError
        code='MP-'+str(n).zfill(6)
        day=datetime.strptime(data['fecha_pedido'],'%Y-%m-%d').date()
        if day.isoformat()!=data['fecha_pedido'] or data['codigo']!=code:raise ValueError
        if data['referencia']!=day.strftime('%d/%m/%Y')+' · '+code:raise ValueError
        result={k:data[k] for k in CAMPOS}
        if previous and previous!=result:raise ValueError
        if anterior and anterior.get('id') and data.get('id') and anterior['id']!=data['id']:raise ValueError
        return result
    except (KeyError,ValueError,TypeError):
        raise ApiError('La referencia del pedido no coincide. Se conserva la información anterior para revisión.') from None

def referencia_pedido(pedido):
    return pedido.respuesta.get('referencia') or ('Pendiente de registro' if pedido.estado in ('pendiente','revisar') else str(pedido.pk))
