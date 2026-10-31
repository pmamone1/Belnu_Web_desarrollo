"""Recorded product interest and later order requests; no causal attribution."""
from collections import defaultdict
from django.core.paginator import Paginator
from django.db.models import Count,Min,Max,Q
from django.utils.dateparse import parse_datetime
from .client import ApiError
from .analitica_detalle import celda,fecha,parametros

TIPOS=('producto_consulta','foto_ampliada','video_mp4','video_enlace')

class InteresProductos:
    def __init__(self,data,producto_ids=None):
        self.data=data;self.q=data['consulta'];base=data['metricas_base'];self.events=base['eventos'];orders=base['pedidos']
        if producto_ids is not None:self.events=self.events.filter(producto_id__in=producto_ids)
        ficha=data.get('ficha')
        if ficha:
            self.events=self.events.filter(distribuidora_id=ficha['distribuidora_id'],vendedor_id=ficha['id'])
            orders=[o for o in orders if (o['distribuidora_id'],o['vendedor_id'])==(ficha['distribuidora_id'],ficha['id'])]
        self.shops={r['id']:r['nombre'] for r in self.q.meta['distribuidoras']}
        roster={(r['distribuidora_id'],r['id']):r for r in base['vendedores']}
        grouped=self.events.filter(tipo__in=TIPOS,producto_id__isnull=False).values('producto_id','distribuidora_id','vendedor_id').annotate(nombre=Max('vendedor'),primera=Min('fecha'),ultima=Max('fecha'),consultas=Count('pk',filter=Q(tipo='producto_consulta')),fotos=Count('pk',filter=Q(tipo='foto_ampliada')),videos=Count('pk',filter=Q(tipo__in=['video_mp4','video_enlace'])))
        self.by_key={};self.by_product=defaultdict(list);self.by_shop=defaultdict(list);self.sin_desglose=set()
        for r in grouped:
            key=(r['distribuidora_id'],r['producto_id'],r['vendedor_id']);r=dict(r,pedidos=set())
            r['nombre']=roster.get((r['distribuidora_id'],r['vendedor_id']),{}).get('nombre') or r['nombre']
            self.by_key[key]=r;self.by_product[r['producto_id']].append(r);self.by_shop[(r['distribuidora_id'],r['producto_id'])].append(r)
        for order in orders:
            if order['estado']=='cancelado':continue
            who=(order['distribuidora_id'],order['vendedor_id'])
            if not order['items']:self.sin_desglose.add(who);continue
            created=parse_datetime(order['creado'])
            for item in order['items']:
                row=self.by_key.get((who[0],item['producto_id'],who[1]))
                if row is not None and created>row['primera']:row['pedidos'].add(order['id'])

    def actores(self,pid,did=None):return self.by_shop.get((did,pid),[]) if did is not None else self.by_product.get(pid,[])

    def resumen(self,pid,did=None):
        rows=self.actores(pid,did);viewers=len(rows);queries=sum(r['consultas'] for r in rows);buyers=sum(bool(r['pedidos']) for r in rows)
        orders=set().union(*(r['pedidos'] for r in rows)) if rows else set()
        incomplete=any((r['distribuidora_id'],r['vendedor_id']) in self.sin_desglose for r in rows)
        return dict(consultas=queries,vendedores=viewers,vendedores_pidieron=buyers,pedidos_posteriores=len(orders),conversion=round(100*buyers/viewers,1) if viewers and not incomplete else None,pedidos_por_consulta=round(100*len(orders)/queries,1) if queries and not incomplete else None,incompleto=incomplete)

    def filas(self,pid,did=None):return sorted(self.actores(pid,did),key=lambda r:(r['nombre'].casefold(),r['distribuidora_id'],r['vendedor_id']))

def enriquecer(data,params,productos=None):
    products=data['productos'] if productos is None else productos
    if not products:return
    index=InteresProductos(data,producto_ids={p['producto_id'] for p in products})
    for p in products:
        p['interes']=index.resumen(p['producto_id'],p['distribuidora_id'])
        p['detalle_url']=parametros(params,detalle='producto',producto_detalle=p['producto_id'],tienda_producto=p['distribuidora_id'])+'#detalle-indicador'

def detalle_producto(data,params,pagina):
    try:
        pid=int(params.get('producto_detalle',''));did=int(params['tienda_producto']) if params.get('tienda_producto') else None
        if pid<1 or (did is not None and did<1):raise ValueError
    except (ValueError,TypeError):raise ApiError('Producto inválido.',400) from None
    if did is not None and did not in data['consulta'].distribuidoras:raise ApiError('Producto fuera de la consulta.',403)
    index=InteresProductos(data,producto_ids=[pid]);events=index.events.filter(producto_id=pid)
    if did is not None:events=events.filter(distribuidora_id=did)
    first=events.order_by('-fecha','-pk').first()
    if first is None:raise ApiError('Producto fuera de la consulta.',403)
    stats=index.resumen(pid,did);page=Paginator(index.filas(pid,did),50).get_page(pagina);rows=[]
    for r in page.object_list:
        link=parametros({'distribuidora':params.get('distribuidora',data['consulta'].distribuidora_id)},tienda=r['distribuidora_id'],vendedor=r['vendedor_id'])+'#ficha-vendedor'
        rows.append({'celdas':[celda(r['nombre'],link),celda(index.shops[r['distribuidora_id']]),celda(r['consultas']),celda(r['fotos']),celda(r['videos']),celda(len(r['pedidos'])),celda(fecha(r['primera'])),celda(fecha(r['ultima']))]})
    note='Interés incluye consultas, fotos ampliadas y videos/enlaces registrados. Los pedidos posteriores contienen este producto y son posteriores a la primera interacción del vendedor; se excluyen cancelados. Son solicitudes, no ventas cobradas. El vínculo temporal no prueba que la visita haya causado el pedido. Las tasas usan todas las interacciones del período de este producto/perfil, no el filtro de acción del historial.'
    if stats['incompleto']:note+=' Hay pedidos de estos vendedores sin desglose: las tasas quedan por determinar; los pedidos posteriores mostrados son sólo los conocidos.'
    else:note+=' Pedidos/consultas puede superar100% si una persona hace varios pedidos; la conversión de vendedores no.'
    return dict(clave='producto',titulo=(first.producto or 'Producto '+str(pid))+(' · SKU '+first.sku if first.sku else ''),columnas=['Vendedor','Distribuidora','Consultas','Fotos','Videos / enlaces','Pedidos posteriores conocidos','Primera interacción','Última interacción'],filas=rows,total=page.paginator.count,pagina=page,nota=note,resumen_producto=stats,anterior=parametros(params,detalle='producto',pagina_detalle=page.previous_page_number())+'#detalle-indicador' if page.has_previous() else '',siguiente=parametros(params,detalle='producto',pagina_detalle=page.next_page_number())+'#detalle-indicador' if page.has_next() else '',cerrar=parametros({k:v for k,v in params.items() if k not in ('producto_detalle','tienda_producto')})+'#resumen-indicadores')
