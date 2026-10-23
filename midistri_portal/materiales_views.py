from django.views.decorators.http import require_http_methods
from django.shortcuts import render,redirect
from .operadores_views import contexto_panel,fallo
from .client import api,ApiError

@require_http_methods(['GET','POST'])
def panel(request,producto):
    try:
        ctx=contexto_panel(request,'midistri.catalogo_gestionar');did=ctx['tienda']['id']
        token=request.session['midistri_operador_token'];review=None;error=''
        current=api('operator-media-products',method='POST',operator_token=token,data={'distribuidora':did,'producto':producto})
        if request.method=='POST':
            if request.POST.get('revision'):
                result=api('operator-media-confirm',method='POST',operator_token=token,
                    data={'distribuidora':did,'revision':request.POST['revision']})
                if result.get('publicacion')!=current['publicacion']:raise ApiError('Respuesta de publicación inválida.')
                request.session['midistri_sync_pendiente']=True
                return redirect('/portal/administrar/productos/?distribuidora='+str(did))
            try:ids=[int(i) for i in request.POST.getlist('videos')]
            except ValueError:raise ApiError('Seleccioná videos válidos.',400)
            review=api('operator-media-preview',method='POST',operator_token=token,
                data={'distribuidora':did,'publicacion':current['publicacion'],'videos':ids})
        ctx.update(data=current,review=review,error_form=error)
        return render(request,'midistri_portal/operador_materiales.html',ctx)
    except ApiError as e:return fallo(request,e)
