from uuid import uuid4
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods
from django.shortcuts import render,redirect
from . import operadores as op
from .operadores_views import fallo
from .client import ApiError,subir_material_tienda
from .promociones import PromocionForm,guardar_promocion
from .models import Tienda,BloquePromocional,Publicacion

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
        error='';uploaded=None
        if request.method=='POST':
            try:
                if request.POST.get('accion')=='subir':
                    uploaded=subir_material_tienda(request.FILES.get('archivo'),did,token,request.POST.get('operacion'))
                    initial.update(tipo=uploaded['tipo'],url=uploaded['url'],material_id=uploaded['id'])
                else:
                    guardar_promocion(perfil,did,request.POST,int(request.POST.get('revision','0')),
                        request.POST['operacion'],token,bloque_id=ident or request.POST.get('nuevo_bloque'))
                    return redirect('/portal/administrar/promociones/?distribuidora='+str(did))
            except (ValidationError,ValueError,ApiError) as e:error=str(e)
        form=PromocionForm(request.POST if request.method=='POST' and request.POST.get('accion')!='subir' else None,initial=initial)
        return render(request,'midistri_portal/operador_promociones.html',{'operador':perfil,'tienda':tienda,'form':form,
            'promociones':BloquePromocional.objects.filter(tienda__distribuidora_id=did).order_by('-activo','orden','id'),
            'productos_media':Publicacion.objects.filter(distribuidora_id=did,activa=True).exclude(multimedia=[]).order_by('nombre'),
            'error_form':error,'uploaded':uploaded,'revision':row.revision if row else 0,'bloque':row,
            'nuevo_bloque':str(uuid4()),'operacion':str(uuid4())})
    except ValueError:return fallo(request,ApiError("Referencia de promoción inválida.",400))
    except ApiError as e:return fallo(request,e)
