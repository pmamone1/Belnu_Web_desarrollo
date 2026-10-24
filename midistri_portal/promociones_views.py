from .sesiones_operador import token_operador
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
        result=api('operator-promotion-preview',method='POST',operator_token=token_operador(request),
            data={'distribuidora':did,'material':str(material)},binary_media=True)
        response=HttpResponse(result[0],content_type=result[1])
        response['Cache-Control']='private, no-store';response['X-Content-Type-Options']='nosniff'
        response['X-Robots-Tag']='noindex, nofollow';return response
    except ApiError as e:return fallo(request,e)

@require_http_methods(['GET','POST'])
def panel(request):
    try:
        from .operadores_views import contexto_panel
        from .pagina_views import url
        ctx=contexto_panel(request,'midistri.tienda_configurar')
        return redirect(url(ctx['tienda']['id']))
    except ApiError as e:return fallo(request,e)
