from uuid import uuid4
from django.core import signing
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods,require_GET
from django.shortcuts import render,redirect
from django.http import HttpResponse
from . import operadores as op
from .operadores_views import fallo
from .client import ApiError,subir_material_tienda,api
from .promociones import PromocionForm,guardar_promocion,confirmar_pendiente,validar_material
from .models import BloquePromocional,Publicacion,CambioPromocional
SALT='midistri.promocion.previa.v1'

@require_GET
def archivo_previo(request,distribuidora,material):
    try:
        perfil=op.perfil_operador(request,'midistri.tienda_configurar')
        did=op.tienda_permitida(perfil,distribuidora)
        # Only a fixed server-to-server operation can read an inactive private upload.
        result=api('operator-promotion-preview',method='POST',operator_token=request.session['midistri_operador_token'],
            data={'distribuidora':did,'material':str(material)},binary_media=True)
        response=HttpResponse(result[0],content_type=result[1])
        response['Cache-Control']='private, no-store';response['X-Content-Type-Options']='nosniff'
        response['X-Robots-Tag']='noindex, nofollow';return response
    except ApiError as e:return fallo(request,e)

@require_http_methods(['GET','POST'])
def panel(request):
    try:
        perfil=op.perfil_operador(request,'midistri.tienda_configurar')
        did=op.tienda_permitida(perfil,request.POST.get('distribuidora') or request.GET.get('distribuidora'))
        token=request.session['midistri_operador_token'];tienda=next(d for d in perfil['distribuidoras'] if d['id']==did)
        ident=request.POST.get('bloque') or request.GET.get('bloque')
        row=BloquePromocional.objects.filter(pk=ident,tienda__distribuidora_id=did).first() if ident else None
        if ident and row is None:raise ApiError('Promoción fuera de alcance.',403)
        initial={k:getattr(row,k) for k in PromocionForm.base_fields if hasattr(row,k)} if row else {}
        error='';uploaded=None;preview=None;signed=None
        new_id=request.POST.get('nuevo_bloque') or str(uuid4())
        oid=request.POST.get('operacion') or str(uuid4())
        form=None
        if request.method=='POST':
            try:
                accion=request.POST.get('accion')
                if accion=='subir':
                    uploaded=subir_material_tienda(request.FILES.get('archivo'),did,token,oid)
                    initial.update(tipo=uploaded['tipo'],url=uploaded['url'],material_id=uploaded['id'])
                    oid=str(uuid4())
                elif accion=='reintentar':
                    confirmar_pendiente(perfil,did,request.POST.get('operacion'),token)
                    return redirect('/portal/administrar/promociones/?distribuidora='+str(did))
                elif accion=='confirmar':
                    review=signing.loads(request.POST.get('previa',''),salt=SALT,max_age=1800)
                    if review['did']!=did or review['operador']!=perfil['operador_id']:raise ApiError('Revisión fuera de alcance.',403)
                    guardar_promocion(perfil,did,review['datos'],review['revision'],review['operacion'],token,bloque_id=review['bloque'])
                    return redirect('/portal/administrar/promociones/?distribuidora='+str(did))
                elif accion=='revisar':
                    form=PromocionForm(request.POST)
                    if not form.is_valid():raise ValidationError(form.errors.as_text())
                    preview=dict(form.cleaned_data);validar_material(preview,did,row)
                    bid=str(row.pk) if row else new_id
                    review={'did':did,'operador':perfil['operador_id'],'datos':dict(form.cleaned_data),
                        'revision':row.revision if row else 0,'operacion':oid,'bloque':bid}
                    signed=signing.dumps(review,salt=SALT,compress=True)
                    if preview.get('material_id'):
                        preview['url']='/portal/administrar/promociones/material/'+str(did)+'/'+preview['material_id']+'/'
                else:raise ValidationError('Revisá la promoción antes de confirmar.')
            except (ValidationError,ValueError,ApiError,signing.BadSignature,KeyError) as e:error=str(e)
        if form is None:form=PromocionForm(None,initial=initial)
        pending=CambioPromocional.objects.filter(bloque__tienda__distribuidora_id=did,estado='pendiente',
            operador_id=perfil['operador_id']).select_related('bloque').order_by('creado')
        try:media_producto,media_indice=map(int,request.POST.get('material_producto','').split(':'))
        except ValueError:media_producto=media_indice=None
        response=render(request,'midistri_portal/operador_promociones.html',{'operador':perfil,'tienda':tienda,'form':form,'titulo':'Promociones de '+tienda['nombre'],'media_producto':media_producto,'media_indice':media_indice,
            'promociones':BloquePromocional.objects.filter(tienda__distribuidora_id=did).order_by('-activo','orden','id'),
            'productos_media':Publicacion.objects.filter(distribuidora_id=did,activa=True).exclude(multimedia=[]).order_by('nombre'),
            'error_form':error,'uploaded':uploaded,'revision':row.revision if row else 0,'bloque':row,'previa':preview,'firma_previa':signed,
            'nuevo_bloque':new_id,'operacion':oid,'pendientes':pending})
        response['Cache-Control']='private, no-store';return response
    except (ValueError,ValidationError):return fallo(request,ApiError('Referencia de promoción inválida.',400))
    except ApiError as e:return fallo(request,e)
