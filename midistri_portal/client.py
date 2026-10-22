"""Private server-to-server transport. Never send its credentials to the browser."""
import json
from urllib.parse import urlsplit
import requests
from django.conf import settings

class ApiError(Exception):
    def __init__(self,message,status=503):
        self.status=status
        super().__init__(message)


def api(action,method='GET',data=None,token=None,binary=False,operator_token=None):
    base=settings.URBAN_API_BASE.rstrip('/')+'/'
    parsed=urlsplit(base)
    if parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ApiError('Falta configurar la conexión HTTPS con Urban Soft.')
    if not settings.URBAN_API_TOKEN:raise ApiError('Falta configurar la conexión con Urban Soft.')
    if not all(part and all(c.isalnum() or c=='-' for c in part) for part in action.split('/')):
        raise ApiError('Operación inválida.',400)
    headers={'Authorization':'Bearer '+settings.URBAN_API_TOKEN,'Accept':'application/json'}
    if token:headers['X-Midistri-Session']=token
    if operator_token:headers['X-Midistri-Operator']=operator_token
    try:
        with requests.request(method,base+action+'/',json=data if method=='POST' else None,
                headers=headers,timeout=(5,30),allow_redirects=False,stream=True) as r:
            content=bytearray()
            for chunk in r.iter_content(65536):
                content.extend(chunk)
                if len(content)>16*1024*1024:raise ApiError('Respuesta demasiado grande; consulte con la distribuidora.')
            if r.status_code!=200:
                try:message=json.loads(content.decode('utf-8')).get('error','No se pudo completar la operación.')
                except (ValueError,AttributeError):message='No se pudo completar la operación.'
                raise ApiError(str(message)[:300],r.status_code)
            if binary:
                if not content.startswith(b'%PDF-') or 'application/pdf' not in r.headers.get('Content-Type','').lower():
                    raise ApiError('El remito no es un PDF válido. Reintentá más tarde.')
                return bytes(content)
            value=json.loads(content.decode('utf-8'))
            if not isinstance(value,dict):raise ValueError
            return value
    except (requests.RequestException,ValueError):
        raise ApiError('No pudimos conectar con la distribuidora. Conservamos tu pedido para reintentar.') from None
