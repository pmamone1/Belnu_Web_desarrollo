"""No device secret or Urban operational bearer is returned to JavaScript."""
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from . import dispositivos as d
from .client import ApiError
from .models import SesionVendedorPortal
from .sesion_pestana import datos_prueba,resolver_sesion_pestana,crear_sesion_pestana


def error(exc):
    return JsonResponse({'error':str(exc)},status=getattr(exc,'status',403))


@require_POST
@transaction.atomic
def recordado(request):
    if not d.activo():return JsonResponse({'fase':'deshabilitado'})
    d.conciliar()
    if request.COOKIES.get(d.OLVIDO)=='1':
        return JsonResponse({'error':'El cierre esta pendiente. Confirma el olvido antes de ingresar.'},status=403)
    try:
        row=d.local(request)
        if row is None:
            try:tab=resolver_sesion_pestana(request)
            except PermissionDenied:return JsonResponse({'fase':'sin_recuerdo'})
            if tab.dispositivo_id:
                return JsonResponse({'fase':'sin_recuerdo'})
            response=JsonResponse({'fase':'dentro','url':'/portal/'})
            return d.recordar_acceso(request,response,tab)
        d.capacidades()
        value=request.COOKIES[d.COOKIE]
        choices=d.opciones(value)
        ident,proof=datos_prueba(request)
        old=SesionVendedorPortal.objects.select_for_update().filter(pk=ident).first()
        if old and (old.dispositivo_id!=row.pk or old.prueba_hash!=__import__('hashlib').sha256(proof.encode()).hexdigest() or old.revocado):
            raise PermissionDenied('Inicia el acceso en una pestana nueva.')
        selected=request.POST.get('seleccion','')
        if not selected and old and request.POST.get('elegir')!='1':
            selected=next((i['seleccion'] for i in choices if i['vendedor_id']==old.vendedor_id and i['distribuidora_id']==old.distribuidora_id),'')
        if not selected and len(choices)==1:selected=choices[0]['seleccion']
        if not selected:return JsonResponse({'fase':'elegir','identidades':choices})
        expected=next((i for i in choices if i['seleccion']==selected),None)
        if expected is None:raise PermissionDenied('Elegi un perfil habilitado.')
        result=d.api('seller-device-resume',method='POST',data={'credencial':value,'seleccion':selected},token=old.token_urban if old else None)
        profile=result.get('perfil',{})
        if (result.get('version')!=1 or result.get('tipo')!='vendedor' or
            profile.get('id')!=expected['vendedor_id'] or profile.get('distribuidora_id')!=expected['distribuidora_id']):
            raise ApiError('Respuesta de restauracion no valida.')
        response=JsonResponse(crear_sesion_pestana(request,profile,result.get('session_token'),ident,proof,dispositivo=row,conservar=True))
        row.ultimo_uso=timezone.now();row.save(update_fields=['ultimo_uso'])
        d.cookie(response,value)
        return response
    except PermissionDenied as exc:
        response=error(exc)
        response.delete_cookie(d.COOKIE,path='/portal/',samesite='Lax')
        return response
    except ApiError as exc:
        response=error(exc)
        if exc.status in (401,403):
            response.delete_cookie(d.COOKIE,path='/portal/',samesite='Lax')
        return response


@require_POST
@transaction.atomic
def olvidar(request):
    return d.olvidar(request,JsonResponse({'ok':True,'url':'/portal/'}))
