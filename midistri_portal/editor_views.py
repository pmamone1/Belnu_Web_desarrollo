"""Private JSON editing; saving a draft never publishes it."""
import json
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST
from . import pagina as p
from .pagina_views import privada,contenido_contexto,recursos
from .operadores_views import contexto_panel
from .sesiones_operador import token_operador
from .client import ApiError
from .catalogo_elegible import elegibles
from .models import Distribuidora,Publicacion
from .presentacion import TEMAS

def html_pagina(data,d):
    ctx=contenido_contexto(data,d,True)
    from django.core.paginator import Paginator
    from django.conf import settings
    from types import SimpleNamespace
    ctx['request']=SimpleNamespace(user=SimpleNamespace(is_staff=False),midistri_codigo_enabled=getattr(settings,'MIDISTRI_LOGIN_CODIGO_ENABLED',False))
    ctx.update(titulo=data['mensajes'].get('titulo') or p.MENSAJES['titulo'],distribuidora=d,
        productos=Paginator(elegibles(Publicacion.objects.filter(distribuidora=d)),24).get_page(1),temas=TEMAS)
    return render_to_string('midistri_portal/catalogo.html',ctx)

@require_POST
def dinamica(request):
    try:
        if len(request.body)>300000:raise ValidationError('Borrador demasiado grande.')
        data=json.loads(request.body)
        if not isinstance(data,dict):raise ValidationError('Solicitud inválida.')
        ctx=contexto_panel(request,'midistri.tienda_configurar',distribuidora=request.GET.get('distribuidora'));did=ctx['tienda']['id'];token=token_operador(request)
        page=p.borrador_tienda(ctx['operador'],did,token);d=Distribuidora.objects.get(pk=did,activa=True)
        action=data.get('accion','cargar');result={}
        if action=='guardar':page=p.guardar_borrador(ctx['operador'],did,data['datos'],data['revision'],data['operacion'],token)
        elif action=='render':
            clean=p.validar_pagina(data['datos'],did)
            return privada(JsonResponse({'html':html_pagina(clean,d)}))
        elif action=='revisar':result['firma']=p.revisar_borrador(ctx['operador'],did,token)
        elif action=='publicar':
            v=p.publicar_revision(ctx['operador'],did,data.get('firma',''),token);result['publicada']=str(v.pk)
        elif action!='cargar':raise ValidationError('Acción inválida.')
        from .editor_estilos import validar_estilo
        result['estilos_defecto']=validar_estilo({})
        result.update(datos=page.datos,revision=page.revision,html=html_pagina(page.datos,d),recursos=recursos(did))
        return privada(JsonResponse(result))
    except ApiError as e:return privada(JsonResponse({'error':str(e)},status=e.status if e.status in (401,403) else 503))
    except (ValidationError,KeyError,ValueError,TypeError) as e:return privada(JsonResponse({'error':str(e)},status=409 if 'cambió' in str(e) or 'confirmar' in str(e) else 400))

@require_POST
def subir(request):
    try:
        from .pagina_views import guardar_accion
        ctx=contexto_panel(request,'midistri.tienda_configurar',distribuidora=request.GET.get('distribuidora'));did=ctx['tienda']['id'];token=token_operador(request)
        page=p.borrador_tienda(ctx['operador'],did,token)
        if request.POST.get('accion')!='archivo':raise ValidationError('Subida inválida.')
        from .models import EdicionPagina
        from hashlib import sha256
        from uuid import UUID
        file=request.FILES.get('archivo')
        if file is None or not 0<file.size<=16*1024*1024:raise ValidationError('Archivo vacío o fuera de límite.')
        digest=sha256(file.read()).hexdigest();file.seek(0)
        op=UUID(request.POST.get('operacion',''))
        metadata=sha256(json.dumps([digest,file.name,file.content_type,request.POST.get('bloque'),request.POST.get('como_logo'),request.POST.get('revision')],sort_keys=True).encode()).hexdigest()
        previous=EdicionPagina.objects.filter(pk=op).first()
        if previous:
            if previous.pagina_id!=page.pk or previous.operador_id!=ctx['operador']['operador_id'] or previous.datos.get('_subida')!=metadata:raise ValidationError('La operación corresponde a otra subida.')
            if previous.revision!=page.revision:raise ValidationError('El borrador cambió después de subir. Recargá la página.')
            return privada(JsonResponse({'datos':page.datos,'revision':page.revision}))
        if int(request.POST['revision'])!=page.revision:raise ValidationError('El borrador cambió. Recargá antes de subir.')
        # Remote file operation is idempotent and finishes before the draft lock.
        from .pagina_views import subir_material_tienda
        result=subir_material_tienda(file,did,token,str(op))
        page=guardar_accion(request,page,ctx,token,subida=result,metadata=metadata)
        return privada(JsonResponse({'datos':page.datos,'revision':page.revision}))
    except ApiError as e:return privada(JsonResponse({'error':str(e)},status=e.status if e.status in (401,403) else 503))
    except (ValidationError,KeyError,ValueError,TypeError) as e:return privada(JsonResponse({'error':str(e)},status=409 if 'cambió' in str(e) else 400))
