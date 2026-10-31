"""Read-only expansion of the exact state/attention groups shown in a report."""
from collections import defaultdict
from urllib.parse import urlencode
from django.core.paginator import Paginator
from .client import ApiError

def preparar(data,params):
    groups=defaultdict(list)
    for order in data['pedidos']:groups[(order['estado'],order['atencion'])].append(order)
    chosen=params.get('grupo_pedidos','')
    valid={state+'/'+attention for state,attention in groups}
    if chosen and chosen not in valid:raise ApiError('El grupo de pedidos no pertenece a esta consulta o ficha.',400)
    shops={r['id']:r['nombre'] for r in data['consulta'].meta['distribuidoras']}
    for index,row in enumerate(data['estados'],1):
        code=row['codigo_estado']+'/'+row['codigo_atencion'];anchor='estado-pedidos-'+str(index)
        orders=sorted(groups[(row['codigo_estado'],row['codigo_atencion'])],key=lambda o:(o['creado'],o['id']),reverse=True)
        page=Paginator(orders,50).get_page(params.get('pagina_estado',1) if chosen==code else 1)
        for order in page.object_list:order['tienda_label']=shops.get(order['distribuidora_id'],'Tienda '+str(order['distribuidora_id']))
        def url(number):
            query={k:params.get(k) for k in ('distribuidora','grupo','q','vendedor','tienda','producto','tipo') if params.get(k)}
            query.update(grupo_pedidos=code,pagina_estado=number)
            return '?'+urlencode(query)+'#'+anchor
        row.update(ordenes=page,ancla=anchor,abierto=chosen==code,anterior=url(page.previous_page_number()) if page.has_previous() else '',siguiente=url(page.next_page_number()) if page.has_next() else '')
