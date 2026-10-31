import json
from django.core import signing
from django.core.exceptions import PermissionDenied,ValidationError
from django.http import JsonResponse
from django.db import DatabaseError
from django.views.decorators.http import require_GET,require_POST
from .client import ApiError
from .analitica_captura import recibir_lote
from .analitica_contexto import contexto,perfil_firmado

def privada(response):response['Cache-Control']='private, no-store';return response

@require_POST
def eventos(request):
    try:
        if len(request.body)>16384:raise ValidationError('Lote demasiado grande.')
        data=json.loads(request.body)
        if not isinstance(data,dict) or set(data)!={'firma','eventos'}:raise ValidationError('Datos inválidos.')
        perfil=perfil_firmado(request,data['firma'])
        try:return privada(JsonResponse(recibir_lote(request,perfil,data['eventos'])))
        except DatabaseError:
            from .analitica_cobertura import marcar_fallo
            if getattr(request,'_midistri_atomic',None) is not None:request._midistri_analitica_fallo=perfil['distribuidora_id']
            else:marcar_fallo(perfil['distribuidora_id'])
            return privada(JsonResponse({'error':'No se pudo registrar la actividad; la cobertura se informa incompleta.'},status=503))
    except signing.SignatureExpired:return privada(JsonResponse({'renovar':True},status=409))
    except (PermissionDenied,signing.BadSignature,ApiError):return privada(JsonResponse({'error':'Contexto no autorizado.'},status=403))
    except (ValueError,TypeError,KeyError,ValidationError):return privada(JsonResponse({'error':'Acción inválida.'},status=400))

@require_GET
def renovar_contexto(request):
    from .views import identificar
    try:
        perfil=identificar(request)
        if not perfil:raise PermissionDenied
        return privada(JsonResponse({'contexto':contexto(request,perfil)}))
    except (ApiError,PermissionDenied):return privada(JsonResponse({'error':'Acceso no disponible.'},status=403))

from datetime import timedelta
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from . import analitica_fuentes as fuentes,analitica_informes as informes,operadores_views as ov

def _operador(request):
    ctx=ov.contexto_panel(request,'midistri.tienda_configurar')
    fuentes.alcance(ctx['operador'],ctx['tienda']['id'])
    return ctx

def _consulta(ident,ctx):
    q=fuentes.cargar_consulta(ident,ctx['operador'])
    if ctx['tienda']['id'] not in q.distribuidoras:raise ApiError('La consulta pertenece a otra tienda. Volvé a consultar desde esta tienda.',403)
    return q

def _error(request,error,ajax=False):
    if ajax:return privada(JsonResponse({'error':str(error)},status=error.status if error.status in (400,401,403,409,503) else 503))
    return privada(ov.fallo(request,error))

@require_GET
def panel(request,ident=None):
    ajax=request.GET.get('parcial')=='metrica'
    try:
        ctx=_operador(request);today=timezone.localtime(timezone.now(),informes.AR).date()
        ctx.update(titulo='Estadísticas de vendedores',desde=(today-timedelta(days=29)).isoformat(),hasta=today.isoformat())
        if ident:
            q=_consulta(ident,ctx);data=informes.resultado(q,request.GET)
            params=request.GET.copy();params.pop('pagina',None);params.pop('pagina_pedidos',None);params.pop('pagina_vendedores',None);params.pop('pagina_productos',None)
            params['distribuidora']=ctx['tienda']['id']
            ctx.update(data,desde=q.desde.isoformat(),hasta=q.hasta.isoformat(),acciones=Paginator(data['eventos'],50).get_page(request.GET.get('pagina',1)),ordenes=Paginator(data['pedidos'],50).get_page(request.GET.get('pagina_pedidos',1)),vendedores_pagina=Paginator(data['vendedores'],50).get_page(request.GET.get('pagina_vendedores',1)),productos_pagina=Paginator(data['productos'],50).get_page(request.GET.get('pagina_productos',1)),params=params.urlencode(),excel_url=reverse('midistri_analitica_excel',args=[ident])+'?'+params.urlencode())
            from .analitica_detalle import detalle,tarjetas
            ctx['tarjetas']=tarjetas(data['resumen'],params)
            if not ajax:
                from .analitica_productos import enriquecer
                enriquecer(data,params,ctx['productos_pagina'].object_list)
            if request.GET.get('detalle'):
                ctx['detalle_indicador']=detalle(data,request.GET['detalle'],request.GET.get('pagina_detalle',1),params)
            if ajax:
                if 'detalle_indicador' not in ctx:raise ApiError('Elegí un indicador.',400)
                from django.template.loader import render_to_string
                return privada(JsonResponse({'html':render_to_string('midistri_portal/analitica_detalle.html',ctx,request=request)}))
        elif ajax:raise ApiError('Volvé a consultar antes de abrir un indicador.',409)
        return privada(render(request,'midistri_portal/analitica_panel.html',ctx))
    except ApiError as e:return _error(request,e,ajax=ajax)

@require_POST
def iniciar(request):
    try:
        ctx=_operador(request);q=fuentes.iniciar_consulta(request,ctx['operador'],request.POST)
        return privada(JsonResponse(fuentes.progreso(q)))
    except ApiError as e:return _error(request,e,True)

@require_POST
def paso(request,ident):
    try:
        ctx=_operador(request)
        try:revision=int(request.POST.get('revision',''))
        except (ValueError,TypeError):raise ApiError('Revisión inválida.',400)
        _consulta(ident,ctx)
        data=fuentes.avanzar_consulta(request,ident,revision,ctx['operador'])
        data['url']=reverse('midistri_analitica_resultado',args=[ident])+'?distribuidora='+str(ctx['tienda']['id'])
        return privada(JsonResponse(data))
    except ApiError as e:return _error(request,e,True)

@require_GET
def exportar(request,ident):
    try:
        ctx=_operador(request);q=_consulta(ident,ctx)
        data=informes.resultado(q,request.GET);response=HttpResponse(informes.excel(data),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition']='attachment; filename="midistri_estadisticas.xlsx"'
        return privada(response)
    except ApiError as e:return _error(request,e)
