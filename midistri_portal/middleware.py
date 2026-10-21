from django.conf import settings
from django.shortcuts import redirect
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django_session_timeout.middleware import SessionTimeoutMiddleware

class PortalMiddleware(MiddlewareMixin):
    def process_request(self,request):
        if not settings.MIDISTRI_ENABLED:
            if request.path.startswith('/portal/'):
                return HttpResponse('MiDistri - Pedidos Online: integración pendiente de habilitación.',status=503)
            return None
        # Legacy public catalog, registration and ordering are hidden, not deleted.
        if request.path=='/' or request.path.startswith(('/store/','/cart/','/orders/')):
            return redirect('/portal/')
        if request.path.startswith('/accounts/') and not request.path.startswith(('/accounts/login/','/accounts/logout/','/accounts/forgotPassword/','/accounts/reset')):
            return redirect('/portal/')
    def process_response(self,request,response):
        if request.path.startswith('/portal/'):
            response['Cache-Control']='private, no-store'
            response['Referrer-Policy']='no-referrer'
            response['X-Robots-Tag']='noindex, nofollow'
        return response

class LegacyTimeoutMiddleware(SessionTimeoutMiddleware):
    def process_request(self,request):
        if getattr(settings,'MIDISTRI_ENABLED',False) and request.path.startswith('/portal/'):
            return None
        return super().process_request(request)
