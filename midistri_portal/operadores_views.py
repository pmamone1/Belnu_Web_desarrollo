from .sesiones_operador import token_operador
"""Distributor pages use delegated identities, never Django staff elevation."""
import secrets
import hashlib
import logging
from urllib.parse import urlencode
from django.conf import settings
from django.core import signing
from django.contrib.auth import logout
from django.http import HttpResponse
from django.shortcuts import redirect,render
from django.views.decorators.http import require_GET,require_POST
from django.views.decorators.csrf import csrf_exempt
from . import operadores as op
from .client import ApiError
def limpiar_autenticacion_heredada(request):
    keep={key:request.session[key] for key in ('midistri_browser','midistri_login_pending','midistri_destino_admin','midistri_admin_browser') if key in request.session}
    logout(request)
    request.session.update(keep)
    request.session.set_expiry(0)

SALT='midistri.operador.desafio.v1'
HANDOFF_COOKIE_PREFIX='midistri_desafio_'


def nombre_cookie_desafio(nonce):
    return HANDOFF_COOKIE_PREFIX+hashlib.sha256(nonce.encode()).hexdigest()[:20]


def clasificar_desafio(request):
    if request.method != 'POST':return None,'cookie_missing'
    if request.headers.get('Origin')!=op.origen_urban():return None,'origin_invalid'
    sent=request.POST.get('desafio','')
    if not 20<=len(sent)<=100:return None,'challenge_mismatch'
    cookie=request.COOKIES.get(nombre_cookie_desafio(sent))
    # Permit an already-started v6 handoff during a rolling update, with its
    # original shorter expiry and the same nonce/origin checks.
    legacy=cookie is None
    cookie=cookie or request.COOKIES.get('midistri_desafio')
    if not cookie:return None,'cookie_missing'
    try:nonce=signing.loads(cookie,salt=SALT,max_age=120 if legacy else 600)
    except signing.SignatureExpired:return None,'challenge_expired'
    except signing.BadSignature:return None,'signature_invalid'
    if isinstance(nonce,dict):nonce=nonce.get('nonce')
    if not isinstance(nonce,str) or not secrets.compare_digest(nonce,sent):return None,'challenge_mismatch'
    if not 20<=len(request.POST.get('codigo',''))<=100:return None,'challenge_mismatch'
    return nonce,None


def fallo_desafio(request,motivo):
    referencia=secrets.token_hex(6)
    logging.getLogger('midistri.handoff').warning('handoff_failed reason=%s reference=%s',motivo,referencia)
    mensajes={
        'challenge_expired':'La pantalla de acceso venció. Iniciá nuevamente el acceso.',
        'cookie_missing':'Falta la validación de este navegador. Iniciá el acceso desde Urban Soft en esta misma pestaña.',
        'challenge_mismatch':'La validación de acceso cambió. Iniciá nuevamente el acceso.',
        'signature_invalid':'La validación del navegador no es válida. Iniciá nuevamente el acceso.',
        'origin_invalid':'No pudimos comprobar el origen del acceso. Iniciá nuevamente desde Urban Soft.'}
    return render(request,'midistri_portal/operador_acceso_error.html',
        {'titulo':'Acceso de Distribuidor','error':mensajes[motivo],'referencia':referencia},status=403)

def fallo(request,error):
    if error.status==401:return redirect('midistri_operador_entrada')
    return render(request,'midistri_portal/operador_base.html',{'error':str(error)},
                  status=error.status if error.status in (400,403,409,503) else 503)

@require_GET
def entrada(request):
    if not op.habilitado():return HttpResponse('Administración de MiDistri desactivada.',status=503)
    destino=request.GET.get('destino','tienda')
    if destino not in ('tienda','banners','panel'):destino='tienda'
    did=request.GET.get('distribuidora','')
    if did and (not did.isdecimal() or int(did)<1 or len(did)>10):
        return HttpResponse('Tienda no válida.',status=400)
    request.session.setdefault('midistri_admin_browser',secrets.token_urlsafe(32))
    nonce=secrets.token_urlsafe(32)
    contexto={'nonce':nonce,'destino':destino,'distribuidora':int(did) if did else None}
    try:url=op.origen_urban()+'/midistri/administrar/?'+urlencode({'desafio':nonce,'distribuidora':did,'destino':destino})
    except ApiError as e:return fallo(request,e)
    response=redirect(url)
    old=[name for name in request.COOKIES if name.startswith(HANDOFF_COOKIE_PREFIX)]
    for name in old[:-9]:
        response.delete_cookie(name,path='/portal/administrar/',samesite='None')
    response.set_cookie(nombre_cookie_desafio(nonce),signing.dumps(contexto,salt=SALT),max_age=600,
        secure=True,httponly=True,samesite='None',path='/portal/administrar/')
    return response

@csrf_exempt
def completar(request):
    if not op.habilitado():return HttpResponse('Administración de MiDistri desactivada.',status=503)
    try:
        nonce,motivo=clasificar_desafio(request)
        if motivo:return fallo_desafio(request,motivo)
        sent=request.POST.get('desafio','');code=request.POST.get('codigo','')
    except ApiError as e:return fallo(request,e)
    try:
        result=op.api('operator-exchange',method='POST',data={'codigo':code,'desafio':sent})
        op.perfil_valido(result['perfil'])
        token=result['session_token']
        if not isinstance(token,str) or not 20<=len(token)<=100:raise ApiError('Respuesta de acceso inválida.')
    except (KeyError,TypeError):return fallo(request,ApiError('Respuesta de acceso inválida.'))
    except ApiError as e:return fallo(request,e)
    cookie=request.COOKIES.get(nombre_cookie_desafio(sent))
    contexto=signing.loads(cookie,salt=SALT,max_age=600) if cookie else {}
    contexto=contexto if isinstance(contexto,dict) else {}
    ids=[d['id'] for d in result['perfil']['distribuidoras']]
    selected=request.POST.get('distribuidora','')
    if selected and (not selected.isdecimal() or len(selected)>10):
        return HttpResponse('Tienda no válida.',status=403)
    did=int(selected) if selected else contexto.get('distribuidora') or ids[0]
    if did not in ids:
        return HttpResponse('La tienda solicitada no está autorizada. Volvé a entrar desde Urban Soft.',status=403)
    destino=contexto.get('destino','panel')
    permiso='midistri.tienda_configurar' in result['perfil']['permisos']
    from .sesiones_operador import guardar_operador
    guardar_operador(request,result['perfil'],token,limpiar_autenticacion_heredada)
    request.session.pop('midistri_destino_admin',None)
    response=redirect(('/portal/administrar/pagina/' if destino in ('tienda','banners') and permiso else '/portal/administrar/')+'?distribuidora='+str(did))
    if not contexto:response=redirect('midistri_operador_panel')
    response.delete_cookie(nombre_cookie_desafio(sent),path='/portal/administrar/',samesite='None')
    response.delete_cookie('midistri_desafio',path='/portal/administrar/',samesite='None')
    return response

@require_GET
def panel(request):
    try:
        perfil=op.perfil_operador(request)
        did=op.tienda_permitida(perfil,request.GET.get('distribuidora',perfil['distribuidoras'][0]['id']))
        return render(request,'midistri_portal/operador_base.html',{'operador':perfil,'titulo':'Administrar MiDistri-Pedidos',
            'tienda':next(d for d in perfil['distribuidoras'] if d['id']==did)})
    except ApiError as e:return fallo(request,e)

@require_POST
def salir(request):
    from .sesiones_operador import tokens_operador
    for token in tokens_operador(request):
        try:op.api('operator-logout',method='POST',operator_token=token)
        except ApiError:pass
    limpiar_autenticacion_heredada(request)
    return redirect('midistri_catalogo')

from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .client import api
from .services import sincronizar
from .administracion_contract import catalogo_valido,pedido_admin_valido

def contexto_panel(request,permiso):
    perfil=op.perfil_operador(request,permiso)
    did=op.tienda_permitida(perfil,request.POST.get('distribuidora') if request.method=='POST'
                           else request.GET.get('distribuidora',perfil['distribuidoras'][0]['id']))
    tienda=next(d for d in perfil['distribuidoras'] if d['id']==did)
    return {'operador':perfil,'tienda':tienda,'titulo':'Administrar MiDistri-Pedidos · '+tienda['nombre']}

@require_GET
def productos(request):
    try:
        ctx=contexto_panel(request,'midistri.catalogo_gestionar')
        data=api('operator-products',method='POST',operator_token=token_operador(request),
                 data={'distribuidora':ctx['tienda']['id'],'q':request.GET.get('q','')[:100],'pagina':request.GET.get('pagina',1)})
        data=catalogo_valido(data,ctx['tienda']['id'])
        ctx.update(catalogo=data,q=request.GET.get('q','')[:100],sync_pendiente=request.session.get('midistri_sync_pendiente'),
            anterior=data['pagina']-1 if data['pagina']>1 else None,
            siguiente=data['pagina']+1 if data['pagina']<data['paginas'] else None)
        return render(request,'midistri_portal/operador_productos.html',ctx)
    except ApiError as e:return fallo(request,e)

@require_POST
def publicar(request):
    try:
        ctx=contexto_panel(request,'midistri.catalogo_gestionar');did=ctx['tienda']['id']
        token=token_operador(request)
        if request.POST.get('accion')=='confirmar':
            result=api('operator-publication-confirm',method='POST',operator_token=token,
                       data={'operacion':request.POST.get('operacion','')})
            if result.get('guardado') is not True:raise ApiError('No se pudo confirmar la publicación.')
            request.session['midistri_sync_pendiente']=True
            try:sincronizar();request.session.pop('midistri_sync_pendiente',None)
            except (ApiError,ValueError):
                messages.warning(request,'Guardado en Urban; falta actualizar catálogo para vendedores.')
            else:messages.success(request,'Publicación guardada y catálogo actualizado.')
            return redirect('/portal/administrar/productos/?'+urlencode({'distribuidora':did}))
        modo=request.POST.get('modo','seleccionados')
        if modo not in ('todos','seleccionados','ocultar'):raise ApiError('Selección no válida.',400)
        try:ids=None if modo=='todos' else [int(p) for p in request.POST.getlist('productos')]
        except ValueError:raise ApiError('Productos no válidos.',400)
        try:proveedor=int(request.POST.get('proveedor') or 0)
        except ValueError:raise ApiError('Proveedor no válido.',400)
        result=api('operator-publication-preview',method='POST',operator_token=token,
            data={'distribuidoras':[did],'ids':ids,'proveedor':proveedor,'accion':'ocultar' if modo=='ocultar' else 'publicar'})
        if (result.get('version')!=1 or not isinstance(result.get('filas'),list)
            or not isinstance(result.get('excluidos'),list) or not isinstance(result.get('resumen'),dict)):
            raise ApiError('Revisión de catálogo inválida.')
        from uuid import UUID
        UUID(result['id'])
        ds=result.get('distribuidoras',[])
        if not ds or not set(ds)<=set(d['id'] for d in ctx['operador']['distribuidoras']):raise ApiError('Revisión fuera de alcance.',403)
        ctx.update(previa=result,destinos=[d for d in ctx['operador']['distribuidoras'] if d['id'] in ds])
        return render(request,'midistri_portal/operador_publicacion.html',ctx)
    except (ValueError,KeyError,TypeError):return fallo(request,ApiError('Selección inválida.'))
    except ApiError as e:return fallo(request,e)

@require_POST
def sincronizar_panel(request):
    try:
        ctx=contexto_panel(request,'midistri.catalogo_gestionar')
        sincronizar();request.session.pop('midistri_sync_pendiente',None)
        messages.success(request,'Catálogo para vendedores actualizado.')
        return redirect('/portal/administrar/productos/?'+urlencode({'distribuidora':ctx['tienda']['id']}))
    except (ApiError,ValueError) as e:return fallo(request,e if isinstance(e,ApiError) else ApiError(str(e)))

@require_GET
def pedidos_panel(request):
    try:
        ctx=contexto_panel(request,'pedidos.gestionar');did=ctx['tienda']['id']
        estado=request.GET.get('estado','pendientes')
        result=api('operator-orders',method='POST',operator_token=token_operador(request),
            data={'distribuidora':did,'estado':estado,'pagina':request.GET.get('pagina',1)})
        if result.get('version')!=1 or not isinstance(result.get('pedidos'),list) or len(result['pedidos'])>50:
            raise ApiError('Bandeja de pedidos inválida.')
        ctx.update({k:result[k] for k in ('total','pagina','paginas')});ctx['pedidos']=[pedido_admin_valido(p,did) for p in result['pedidos']]
        if any(type(result.get(k)) is not int for k in ('total','pagina','paginas')):raise ApiError('Paginación inválida.')
        ctx.update(estado=estado,estados=[('pendientes','Pendientes'),('','Todos'),('recibido','Recibidos'),('ok','OK para preparar'),('emitido','Preparados'),('cancelado','Cancelados')],
            anterior=result['pagina']-1 if result['pagina']>1 else None,
            siguiente=result['pagina']+1 if result['pagina']<result['paginas'] else None)
        return render(request,'midistri_portal/operador_pedidos.html',ctx)
    except ApiError as e:return fallo(request,e)

def capacidades():
    try:
        data=api('capabilities')
    except ApiError as e:
        if e.status in (404,405):return False
        raise
    if (type(data.get('version')) is not int or data['version']!=1 or
        type(data.get('contrato_pedido')) is not int or data['contrato_pedido']!=2 or
        data.get('preparacion_parcial') is not True or data.get('acceso_por_contacto') is not True):
        raise ApiError('Capacidades de Urban Soft incompatibles. No se confirmó la preparación.')
    return True

@require_http_methods(['GET','POST'])
def pedido_panel(request,ident):
    from .contract import atencion_valida
    try:
        ctx=contexto_panel(request,'pedidos.gestionar');did=ctx['tienda']['id']
        partial=capacidades()
        accion=request.POST.get('accion','detalle') if request.method=='POST' else 'detalle'
        if accion=='emitir' and request.POST.get('confirmar_preparacion')!='si':
            raise ApiError('Confirme la preparación del detalle revisado.',409)
        data={'pedido':str(ident),'accion':accion,'revision':request.POST.get('revision','')}
        if accion=='emitir' and any(k.startswith('preparada_') or k=='incluir' for k in request.POST):
            raise ApiError('El detalle cambió. Revise nuevamente antes de confirmar.',409)
        if accion=='revisar_preparacion' and partial:
            cantidades=[]
            selected=set(request.POST.getlist('incluir'))
            for key in request.POST:
                if key.startswith('preparada_'):
                    pid=key[len('preparada_'):]
                    if not pid.isdigit():raise ValueError
                    qty=int(request.POST[key])
                    cantidades.append({'producto_id':int(pid),'cantidad_preparada':qty if pid in selected else 0})
            data['cantidades']=cantidades
        result=api('operator-order',method='POST',operator_token=token_operador(request),data=data)
        pedido=pedido_admin_valido(result['pedido'],did,str(ident))
        preview=None
        if result.get('revision') and partial:
            preview=atencion_valida(pedido['items'],result.get('preparacion_previa'))
        rows=[]
        attention=preview or pedido.get('atencion')
        byid={i['producto_id']:i for i in attention['items']} if attention else {}
        for i in pedido['items']:
            row=dict(i);row.update(byid.get(i['producto_id'],{}));rows.append(row)
        ctx.update(pedido=pedido,items=rows,parciales=partial,preparacion_previa=preview,
            revision=result.get('revision',''),
            puede_emitir=ctx['operador']['financiero'] and 'pedidos.remitos' in ctx['operador']['permisos'],
            puede_remito='pedidos.remitos_ver' in ctx['operador']['permisos'])
        if request.method=='POST' and accion in ('aprobar','cancelar','emitir'):
            messages.success(request,'Operación registrada en Urban Soft.')
            return redirect('/portal/administrar/pedido/'+str(ident)+'/?'+urlencode({'distribuidora':did}))
        return render(request,'midistri_portal/operador_pedido.html',ctx)
    except (KeyError,TypeError,ValueError):return fallo(request,ApiError('Detalle o cantidades de pedido inválidos.',400))
    except ApiError as e:return fallo(request,e)

@require_POST
def excel_panel(request):
    try:
        contexto_panel(request,'pedidos.gestionar')
        data=api('operator-order-excel',method='POST',operator_token=token_operador(request),
            data={'pedidos':request.POST.getlist('pedidos')},
            binary_mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response=HttpResponse(data,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition']='attachment; filename="MiDistri_deposito.xlsx"';return response
    except ApiError as e:return fallo(request,e)

@require_http_methods(['GET','POST'])
def abastecimiento_panel(request):
    from datetime import datetime,timedelta
    try:
        ctx=contexto_panel(request,'pedidos.gestionar')
        if request.method=='POST':
            data=api('operator-order-supply',method='POST',operator_token=token_operador(request),
                data={'distribuidora':ctx['tienda']['id'],'desde':request.POST.get('desde',''),
                    'hasta':request.POST.get('hasta',''),'estado':request.POST.get('estado','pendientes')},
                binary_mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            r=HttpResponse(data,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            r['Content-Disposition']='attachment; filename="MiDistri_abastecimiento_Urban_Point.xlsx"'
            r['Cache-Control']='private, no-store'
            return r
        # Python 3.7 production: use pytz already required by Django 3.2.
        import pytz
        today=datetime.now(pytz.timezone('America/Argentina/Buenos_Aires')).date()
        ctx.update(desde=(today-timedelta(days=29)).isoformat(),hasta=today.isoformat())
        return render(request,'midistri_portal/operador_abastecimiento.html',ctx)
    except ApiError as e:return fallo(request,e)

@require_POST
def remito_panel(request,ident):
    try:
        contexto_panel(request,'pedidos.remitos_ver')
        data=api('operator-order-document',method='POST',operator_token=token_operador(request),
            data={'pedido':str(ident)},binary=True)
        response=HttpResponse(data,content_type='application/pdf')
        response['Content-Disposition']='attachment; filename="MiDistri_remito.pdf"';return response
    except ApiError as e:return fallo(request,e)


@require_http_methods(['GET','POST'])
def tienda_panel(request):
    try:
        from .operadores_views import contexto_panel
        from .pagina_views import url
        ctx=contexto_panel(request,'midistri.tienda_configurar')
        return redirect(url(ctx['tienda']['id']))
    except ApiError as e:return fallo(request,e)
