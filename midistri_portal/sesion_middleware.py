from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from .sesion_pestana import TabSession,resolver_sesion_pestana


class SesionPestanaMiddleware(MiddlewareMixin):
    def process_request(self,request):
        request.midistri_codigo_enabled=bool(getattr(settings,'MIDISTRI_LOGIN_CODIGO_ENABLED',False))
        if not request.midistri_codigo_enabled or not request.path.startswith('/portal/') or request.path.startswith(('/portal/administrar/','/portal/gestion/')):return None
        public=request.path=='/portal/' or request.path.startswith(('/portal/acceso/','/portal/activar/'))
        row=None
        if not request.path.startswith(('/portal/acceso/','/portal/activar/')) and request.headers.get('X-Midistri-Tab'):
            ctx=transaction.atomic();ctx.__enter__();request._midistri_atomic=ctx
            try:row=resolver_sesion_pestana(request)
            except PermissionDenied as e:
                ctx.__exit__(None,None,None);request._midistri_atomic=None
                return JsonResponse({'error':str(e)},status=403)
        elif not public:
            if request.method=='GET':return render(request,'midistri_portal/sesion_shell.html',{'titulo':'MiDistri-Pedidos'})
            return JsonResponse({'error':'Ingresá con tu Email en esta pestaña.'},status=403)
        request.midistri_tab=row
        request.session=TabSession(request.session,row)

    def _finish(self,request,error=None):
        ctx=getattr(request,'_midistri_atomic',None)
        if ctx is None:return
        request._midistri_atomic=None
        try:
            if error is None:
                row=getattr(request,'midistri_tab',None)
                if row:
                    row.actividad=timezone.now();row.save()
        except Exception as exc:
            ctx.__exit__(type(exc),exc,exc.__traceback__);raise
        ctx.__exit__(type(error) if error else None,error,error.__traceback__ if error else None)
        # Persist telemetry gaps after the failed event request rolled back.
        # This callback never grants access or participates in an order mutation.
        did=getattr(request,'_midistri_analitica_fallo',None)
        if did:
            from .analitica_cobertura import marcar_fallo
            marcar_fallo(did)

    def process_response(self,request,response):
        self._finish(request,RuntimeError('response_failed') if response.status_code>=500 else None)
        return response

    def process_exception(self,request,exception):self._finish(request,exception)
