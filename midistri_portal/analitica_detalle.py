"""Paginated, read-only drilldowns of the exact summary population."""
from collections import defaultdict
from urllib.parse import urlencode
from django.core.paginator import Paginator
from django.db.models import Count,Min,Max
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from .client import ApiError
from .analitica_informes import AR,ETIQUETAS,ESTADOS,ATENCION
from .templatetags.midistri_formatos import precio_ar

METRICAS=(('consultas_productos','Consultas de productos'),('productos_consultados','Productos distintos consultados'),('vendedores_activos','Vendedores con actividad'),('visitas','Visitas'),('ingresos','Ingresos'),('fotos','Fotos ampliadas'),('videos','Videos iniciados / enlaces abiertos'),('pedidos','Pedidos recibidos'),('conversion','Conversión a pedido'))

def parametros(params,**updates):
    out={k:params.get(k) for k in ('distribuidora','grupo','q','vendedor','tienda','producto','tipo','pagina','pagina_pedidos','pagina_vendedores','pagina_productos','producto_detalle','tienda_producto') if params.get(k)}
    out.update(updates)
    return '?'+urlencode({k:v for k,v in out.items() if v is not None and v!=''})

def tarjetas(resumen,params):
    return [dict(clave=key,titulo=label,valor=resumen[key],porcentaje=key=='conversion',url=parametros(params,detalle=key,producto_detalle=None,tienda_producto=None)+'#detalle-indicador') for key,label in METRICAS]

def fecha(value):
    if isinstance(value,str):value=parse_datetime(value)
    return timezone.localtime(value,AR).strftime('%d/%m/%Y %H:%M:%S') if value else 'Sin fecha'

def celda(texto,url=''):
    return {'texto':texto,'url':url}

def detalle(data,metrica,pagina=1,params=None):
    q=data['consulta']
    if not q.completa or q.vence<=timezone.now():raise ApiError('La consulta venció o está incompleta. Volvé a consultar.',409)
    if metrica=='producto':
        from .analitica_productos import detalle_producto
        return detalle_producto(data,params or {},pagina)
    if metrica not in dict(METRICAS):raise ApiError('Indicador inválido.',400)
    params=params or {'distribuidora':q.distribuidora_id}
    base=data['metricas_base'];events=base['eventos'];vendors=base['vendedores'];orders=base['pedidos']
    shops={r['id']:r['nombre'] for r in q.meta['distribuidoras']}
    byvendor={(r['distribuidora_id'],r['id']):r for r in vendors}
    def shop(did):return shops.get(did,'Tienda '+str(did))
    def vendor_link(row):return parametros({'distribuidora':params.get('distribuidora',q.distribuidora_id)},tienda=row['distribuidora_id'],vendedor=row.get('vendedor_id',row.get('id')))+'#ficha-vendedor'
    def vendor_name(row):return row.get('nombre') or row.get('vendedor') or 'Vendedor '+str(row.get('vendedor_id',row.get('id')))
    nota='Detalle del resumen completo: los filtros de las tablas inferiores no modifican estas cifras.'
    if metrica in ('vendedores_activos','conversion'):
        source=[v for v in vendors if v['acciones']>0]
        headers=['Vendedor','Distribuidora','Visitas','Consultas de productos','Pedidos del período']
        if metrica=='conversion':
            headers.append('Resultado')
            count=sum(v['pedidos']>0 for v in source)
            nota=str(count)+' de '+str(len(source))+' vendedores con actividad registrada hicieron al menos un pedido. Se cuentan pedidos recibidos; no equivale a cobros.'
    elif metrica=='productos_consultados':
        source=events.filter(tipo='producto_consulta',producto_id__isnull=False).values('producto_id').annotate(nombre=Max('producto'),sku=Max('sku'),consultas=Count('pk'),ultima=Max('fecha')).order_by('-consultas','producto_id')
        headers=['Producto','SKU','Consultas','Última consulta']
        nota+=' Una fila por producto, aunque se consulte en ambas tiendas del bloque20/65.'
    elif metrica=='visitas':
        source=events.values('visita').annotate(primera=Min('fecha'),ultima=Max('fecha'),acciones=Count('pk')).order_by('-ultima','visita')
        headers=['Vendedores / perfiles','Primera acción registrada','Última acción registrada','Acciones']
        nota+=' Una fila por visita distinta. Las fechas son acciones registradas, no acreditan tiempo de permanencia.'
    elif metrica=='pedidos':
        source=sorted(orders,key=lambda r:(r['creado'],r['id']),reverse=True)
        headers=['Fecha y referencia','Vendedor','Distribuidora','Estado / atención','Solicitado','Confirmado']
        nota+=' Se incluyen los pedidos recibidos en el período, aunque no tengan una visita registrada.'
    else:
        types={'consultas_productos':['producto_consulta'],'ingresos':['ingreso','ingreso_recordado'],'fotos':['foto_ampliada'],'videos':['video_mp4','video_enlace']}[metrica]
        source=events.filter(tipo__in=types).order_by('-fecha','-pk')
        headers=['Fecha y hora','Vendedor','Distribuidora','Acción','Producto / SKU']
        if metrica=='ingresos':nota+=' Incluye ingresos con código y accesos recordados; no equivale a visitas distintas.'
        if metrica=='videos':nota+=' Un enlace abierto o una reproducción iniciada no confirma que el video se haya visto completo.'
    page=Paginator(source,50).get_page(pagina);rows=[]
    participants=defaultdict(dict)
    if metrica=='visitas':
        visit_ids=[r['visita'] for r in page.object_list]
        for e in events.filter(visita__in=visit_ids).values('visita','distribuidora_id','vendedor_id','vendedor').distinct():
            k=(e['distribuidora_id'],e['vendedor_id']);v=byvendor.get(k,e)
            participants[e['visita']][k]=vendor_name(v)+' · '+shop(e['distribuidora_id'])
    for r in page.object_list:
        if metrica in ('vendedores_activos','conversion'):
            values=[celda(vendor_name(r),vendor_link(r)),celda(shop(r['distribuidora_id'])),celda(r['visitas']),celda(r['consultas_productos']),celda(r['pedidos'])]
            if metrica=='conversion':values.append(celda('Con pedidos' if r['pedidos'] else 'Sin pedidos en el período'))
        elif metrica=='productos_consultados':values=[celda(r['nombre'] or 'Producto '+str(r['producto_id']),parametros({'distribuidora':params.get('distribuidora',q.distribuidora_id)},detalle='producto',producto_detalle=r['producto_id'])+'#detalle-indicador'),celda(r['sku'] or '—'),celda(r['consultas']),celda(fecha(r['ultima']))]
        elif metrica=='visitas':values=[celda('; '.join(participants[r['visita']].values())),celda(fecha(r['primera'])),celda(fecha(r['ultima'])),celda(r['acciones'])]
        elif metrica=='pedidos':
            values=[celda(fecha(r['creado'])+' · '+r['referencia'],'/portal/administrar/pedido/'+r['id']+'/?'+urlencode({'distribuidora':r['distribuidora_id']})),celda(r['vendedor'],vendor_link(r)),celda(shop(r['distribuidora_id'])),celda(ESTADOS.get(r['estado'],r['estado'])+' / '+ATENCION.get(r['atencion'],r['atencion'])),celda('Por conciliar' if r['conciliacion'] else '$ '+precio_ar(r['total_solicitado'])),celda('Por conciliar' if r['conciliacion'] else '$ '+precio_ar(r['total_confirmado']))]
        else:
            values=[celda(fecha(r.fecha)),celda(r.vendedor,vendor_link({'distribuidora_id':r.distribuidora_id,'vendedor_id':r.vendedor_id})),celda(shop(r.distribuidora_id)),celda(ETIQUETAS.get(r.tipo,r.tipo)),celda((r.producto or '—')+(' · SKU '+r.sku if r.sku else ''))]
        rows.append({'celdas':values})
    return dict(clave=metrica,titulo=dict(METRICAS)[metrica],nota=nota,columnas=headers,filas=rows,total=page.paginator.count,pagina=page,anterior=parametros(params,detalle=metrica,pagina_detalle=page.previous_page_number())+'#detalle-indicador' if page.has_previous() else '',siguiente=parametros(params,detalle=metrica,pagina_detalle=page.next_page_number())+'#detalle-indicador' if page.has_next() else '',cerrar=parametros(params)+'#resumen-indicadores')
