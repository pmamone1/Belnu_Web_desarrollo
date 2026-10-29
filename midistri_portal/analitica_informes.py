"""Read-only analytics: recorded activity, current roster and historical orders."""
from collections import defaultdict
from datetime import datetime,time,timedelta
from decimal import Decimal
from io import BytesIO
import pytz
from django.db.models import Count,Max,Q
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from .client import ApiError
from .models import EventoAnalitico,IntervaloAnalitico,SesionVendedorPortal

AR=pytz.timezone('America/Argentina/Buenos_Aires')
ETIQUETAS={'ingreso':'Ingreso','catalogo':'Catálogo','producto_consulta':'Consulta de producto','foto_ampliada':'Foto ampliada','video_mp4':'Video: reproducción iniciada','video_enlace':'Enlace de video abierto','carrito':'Cantidad en carrito','carrito_visto':'Carrito consultado','pedidos_vistos':'Historial consultado','pedido_visto':'Pedido consultado','pedido':'Pedido aceptado'}
GRUPOS=[('activos','Vendedores actuales'),('sin_ingresos','Sin ingreso registrado desde la medición'),('sin_actividad','Sin actividad en el período'),('sin_pedidos_periodo','Ingresaron, sin pedido en el período'),('nunca_pedido','Sin pedidos históricos'),('con_pedidos','Con pedidos en el período'),('sin_contacto','Sin Email habilitado'),('historicos','Inactivos / históricos')]

def resultado(q,filtros):
    if not q.completa or q.vence<=timezone.now():raise ApiError('La consulta no está completa o venció. Volvé a consultar.',409)
    cut=parse_datetime(q.meta['corte']);start=AR.localize(datetime.combine(q.desde,time.min));end=AR.localize(datetime.combine(q.hasta+timedelta(days=1),time.min))
    all_events=EventoAnalitico.objects.filter(distribuidora_id__in=q.distribuidoras,fecha__lte=cut)
    events=all_events.filter(fecha__gte=start,fecha__lt=end)
    key=lambda r:(r['distribuidora_id'],r['vendedor_id'])
    activity={key(r):r for r in events.values('distribuidora_id','vendedor_id').annotate(acciones=Count('pk'),visitas=Count('visita',distinct=True),ingresos=Count('pk',filter=Q(tipo='ingreso')),ultima=Max('fecha'))}
    ever={key(r):r for r in all_events.values('distribuidora_id','vendedor_id').annotate(ultima=Max('fecha'),nombre=Max('vendedor'))}
    intervals=list(IntervaloAnalitico.objects.filter(distribuidora_id__in=q.distribuidoras,desde__lte=cut).order_by('desde').values('distribuidora_id','desde','hasta'))
    covered={r['distribuidora_id'] for r in intervals};measurement=min((r['desde'] for r in intervals),default=None)
    prior=set(SesionVendedorPortal.objects.filter(distribuidora_id__in=q.distribuidoras,actividad__lt=measurement).values_list('distribuidora_id','vendedor_id')) if measurement else set()
    orders=q.datos['pedidos'];byorder=defaultdict(list)
    for o in orders:byorder[key(o)].append(o)
    roster={(v['distribuidora_id'],v['id']):dict(v) for v in q.datos['vendedores']}
    for k,e in ever.items():
        if k not in roster:roster[k]=dict(id=k[1],distribuidora_id=k[0],nombre=e['nombre'],lin=None,vv=None,activo=False,actual=False,contacto=False,pedidos_historicos=None)
    rows=[]
    for k,v in roster.items():
        a=activity.get(k,{});v.update(acciones=a.get('acciones',0),visitas=a.get('visitas',0),ingresos=a.get('ingresos',0),ultima=ever.get(k,{}).get('ultima'),pedidos=len(byorder[k]),medido=k[0] in covered,acceso_previo=k in prior)
        rows.append(v)
    rows.sort(key=lambda r:(r['nombre'].casefold(),r['distribuidora_id'],r['id']))
    activekeys=set(activity);orderedkeys={k for k,v in byorder.items() if v};totals=events.aggregate(fotos=Count('pk',filter=Q(tipo='foto_ampliada')),videos=Count('pk',filter=Q(tipo__in=['video_mp4','video_enlace'])),ingresos=Count('pk',filter=Q(tipo='ingreso')),visitas=Count('visita',distinct=True))
    reconciled=any(o['conciliacion'] for o in orders)
    summary=dict(vendedores_activos=len(activekeys),**totals,pedidos=len(orders),pedidos_sin_visita=sum(key(o) not in activekeys for o in orders),conversion=round(100*len(activekeys&orderedkeys)/len(activekeys),1) if activekeys else None,total_solicitado=None if reconciled else sum((Decimal(o['total_solicitado']) for o in orders),Decimal(0)),total_confirmado=None if reconciled else sum((Decimal(o['total_confirmado']) for o in orders),Decimal(0)),conciliacion=reconciled)
    group=filtros.get('grupo','activos');text=str(filtros.get('q','')).strip().casefold()
    def included(v):
        current=v['actual'] and v['activo']
        if group=='historicos':return not current
        if not current:return False
        if group=='sin_ingresos':return v['medido'] and v['ultima'] is None and not v['acceso_previo']
        if group=='sin_actividad':return v['medido'] and not v['acciones']
        if group=='sin_pedidos_periodo':return v['acciones']>0 and not v['pedidos']
        if group=='nunca_pedido':return v['pedidos_historicos']==0
        if group=='con_pedidos':return v['pedidos']>0
        if group=='sin_contacto':return not v['contacto']
        return True
    vendors=[v for v in rows if included(v) and (not text or text in ('%s %s %s'%(v['nombre'],v['lin'],v['vv'])).casefold())]
    selected=None
    if filtros.get('vendedor'):
        try:k=(int(filtros['tienda']),int(filtros['vendedor']));selected=roster[k]
        except (ValueError,TypeError,KeyError):raise ApiError('Vendedor fuera de la consulta.',403) from None
        events=events.filter(distribuidora_id=k[0],vendedor_id=k[1]);orders=byorder[k]
    if filtros.get('producto'):events=events.filter(Q(producto__icontains=str(filtros['producto'])[:100])|Q(sku__icontains=str(filtros['producto'])[:100]))
    if filtros.get('tipo'):
        if filtros['tipo'] not in ETIQUETAS:raise ApiError('Tipo de acción inválido.',400)
        events=events.filter(tipo=filtros['tipo'])
    products=list(events.filter(producto_id__isnull=False).values('producto_id','distribuidora_id').annotate(nombre=Max('producto'),sku=Max('sku'),consultas=Count('pk',filter=Q(tipo='producto_consulta')),fotos=Count('pk',filter=Q(tipo='foto_ampliada')),videos=Count('pk',filter=Q(tipo__in=['video_mp4','video_enlace']))).order_by('-consultas','nombre'))
    return dict(consulta=q,resumen=summary,vendedores=vendors,ficha=selected,productos=products,pedidos=orders,eventos=events.order_by('-fecha','-pk'),medicion_desde=measurement,intervalos=intervals,grupos=GRUPOS,tipos=ETIQUETAS,filtros=dict(filtros),distribuidoras=q.meta['distribuidoras'])

def seguro(value):
    if isinstance(value,str) and value.lstrip().startswith(('=','+','-','@')):return "'"+value
    if isinstance(value,datetime):return timezone.localtime(value,AR).strftime('%d/%m/%Y %H:%M:%S')
    return value

def excel(data):
    from openpyxl import Workbook
    if data['eventos'].count()>20000 or any(len(data[k])>20000 for k in ('vendedores','productos','pedidos')):raise ApiError('Hay más de 20.000 filas. Reducí el período o los filtros antes de exportar.',400)
    wb=Workbook();wb.remove(wb.active)
    def sheet(name,headers,rows):
        s=wb.create_sheet(name);s.append(headers)
        for row in rows:s.append([seguro(x) for x in row])
        s.freeze_panes='A2';s.auto_filter.ref=s.dimensions
        for col in s.columns:s.column_dimensions[col[0].column_letter].width=min(55,max(18,max(len(str(c.value or '')) for c in col[:100])+2))
    summary=data['resumen'];q=data['consulta']
    sheet('Resumen',['Medida','Valor'],[(k,v) for k,v in summary.items()]+[('Desde',q.desde),('Hasta',q.hasta),('Corte',q.meta['corte']),('Medición desde',data['medicion_desde']),('Aviso','Actividad orientativa; no registra acciones anteriores al inicio ni confirma lectura de videos externos.')])
    sheet('Vendedores',['Vendedor','Distribuidora ID','Vendedor ID','LIN','VV','Actual','Activo','Email habilitado','Acciones período','Visitas','Ingresos','Última acción registrada','Pedidos período','Pedidos históricos'],[(v['nombre'],v['distribuidora_id'],v['id'],v['lin'],v['vv'],v['actual'],v['activo'],v['contacto'],v['acciones'],v['visitas'],v['ingresos'],v['ultima'],v['pedidos'],v['pedidos_historicos']) for v in data['vendedores']])
    sheet('Productos',['Producto','SKU','Distribuidora ID','Consultas','Fotos ampliadas','Videos iniciados / enlaces abiertos'],[(p['nombre'],p['sku'],p['distribuidora_id'],p['consultas'],p['fotos'],p['videos']) for p in data['productos']])
    sheet('Pedidos',['Referencia','Fecha','Distribuidora ID','Vendedor','Estado','Atención','Solicitado','Confirmado','Unidades solicitadas','Unidades confirmadas','Conciliación'],[(o['referencia'],parse_datetime(o['creado']),o['distribuidora_id'],o['vendedor'],o['estado'],o['atencion'],o['total_solicitado'],o['total_confirmado'],o['unidades_solicitadas'],o['unidades_confirmadas'],o['conciliacion']) for o in data['pedidos']])
    sheet('Acciones',['Fecha Argentina','Distribuidora ID','Vendedor','Acción','Producto','SKU','Recurso','Cantidad','Pedido'],[(e.fecha,e.distribuidora_id,e.vendedor,ETIQUETAS.get(e.tipo,e.tipo),e.producto,e.sku,e.recurso,e.cantidad,str(e.pedido) if e.pedido else '') for e in data['eventos'].iterator()])
    sheet('Cobertura',['Distribuidora ID','Desde','Hasta'],[(r['distribuidora_id'],r['desde'],r['hasta']) for r in data['intervalos']])
    out=BytesIO();wb.save(out);return out.getvalue()
