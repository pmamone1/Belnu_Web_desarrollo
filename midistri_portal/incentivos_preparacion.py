"""Private weekly activity producer. No SMTP and no automatic network retry."""
import json
from collections import defaultdict
from django.db.models import Count,Max
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from .models import EventoAnalitico,Distribuidora
from .analitica_cobertura import congelar,cobertura
from .client import api,ApiError

def preparar_periodo(config):
    ids=config.get('distribuidoras');start=parse_datetime(str(config.get('desde')));end=parse_datetime(str(config.get('hasta')))
    if not isinstance(ids,list) or not ids or any(type(i) is not int or i<1 for i in ids) or len(set(ids))!=len(ids):raise ApiError('Alcance semanal inválido.')
    if start is None or end is None or timezone.is_naive(start) or timezone.is_naive(end) or (end-start).total_seconds()!=7*86400:raise ApiError('Período semanal inválido.')
    if set(ids)!=set(Distribuidora.objects.filter(pk__in=ids,activa=True).values_list('pk',flat=True)):raise ApiError('Falta sincronizar una tienda autorizada.')
    cover=congelar(ids,end)
    if any(cobertura(cover['intervalos'],cover['incidencias'],i,start,end)!='completa' for i in ids):raise ApiError('Cobertura analítica incompleta; no se prepararon incentivos.')
    base=EventoAnalitico.objects.filter(distribuidora_id__in=ids,fecha__gte=start,fecha__lt=end)
    rows=list(base.values('vendedor_id','distribuidora_id').annotate(visitas=Count('visita',distinct=True),ultima=Max('fecha')).order_by('distribuidora_id','vendedor_id')[:2001])
    if len(rows)>2000:raise ApiError('Más de2000 perfiles; no se truncan los destinatarios.')
    result=[]
    for row in rows:
        products=list(base.filter(vendedor_id=row['vendedor_id'],distribuidora_id=row['distribuidora_id'],tipo__in=['producto_consulta','foto_ampliada','video_mp4','video_enlace']).exclude(producto_id=None).order_by('producto_id').values_list('producto_id',flat=True).distinct()[:201])
        if len(products)>200:raise ApiError('Más de200 intereses por vendedor; no se truncan los datos.')
        result.append({'id':row['vendedor_id'],'distribuidora_id':row['distribuidora_id'],'visitas':row['visitas'],'productos':products,'ultima':row['ultima'].isoformat()})
    data={'version':1,'distribuidoras':ids,'desde':config['desde'],'hasta':config['hasta'],'cobertura':'completa','actividad':result}
    if len(json.dumps(data).encode('utf-8'))>950000:raise ApiError('La fuente supera el tamaño admitido; no se envía parcialmente.')
    return data

def procesar():
    due=api('weekly-incentives-due')
    configs=due.get('configuraciones')
    if due.get('version')!=1 or not isinstance(configs,list) or len(configs)>200:raise ApiError('Contrato semanal incompatible.')
    count=0;errors=[]
    for c in configs:
        try:
            data=preparar_periodo(c)
            api('weekly-incentives-prepare',method='POST',data={'configuracion':c['id'],'revision':c['revision'],'hasta':c['hasta'],'actividad':data,'vista_previa':c.get('vista_previa',False)})
            count+=1
        except ApiError as exc:errors.append({'configuracion':c.get('id'),'motivo':str(exc)})
    return {'preparadas':count,'errores':errors,'sin_envios_smtp':True}
