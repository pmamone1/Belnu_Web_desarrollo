"""Private server-to-server transport. Never send its credentials to the browser."""
import json
from urllib.parse import urlsplit
import requests
from django.conf import settings

class ApiError(Exception):
    def __init__(self,message,status=503):
        self.status=status
        super().__init__(message)


def api(action,method='GET',data=None,token=None,binary=False,operator_token=None,binary_mime=None,binary_media=False):
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
            if binary_media:
                mime=r.headers.get('Content-Type','').split(';')[0].strip().lower()
                if action!='operator-promotion-preview' or mime not in ('image/png','video/mp4'):
                    raise ApiError('Material de vista previa inválido.')
                if mime=='image/png' and not content.startswith(b'\x89PNG\r\n\x1a\n'):raise ApiError('Foto inválida.')
                if mime=='video/mp4' and content[4:8]!=b'ftyp':raise ApiError('Video inválido.')
                return bytes(content),mime
            if binary_mime:
                from io import BytesIO
                from zipfile import ZipFile,BadZipFile
                if binary_mime not in r.headers.get('Content-Type','').lower():raise ApiError('Tipo de documento inválido.')
                if binary_mime=='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                    try:
                        with ZipFile(BytesIO(content)) as z:
                            if '[Content_Types].xml' not in z.namelist() or 'xl/workbook.xml' not in z.namelist():raise BadZipFile
                    except BadZipFile:raise ApiError('El Excel no es válido.') from None
                else:raise ApiError('Tipo de documento no permitido.')
                return bytes(content)
            if binary:
                if not content.startswith(b'%PDF-') or 'application/pdf' not in r.headers.get('Content-Type','').lower():
                    raise ApiError('El remito no es un PDF válido. Reintentá más tarde.')
                return bytes(content)
            value=json.loads(content.decode('utf-8'))
            if not isinstance(value,dict):raise ValueError
            return value
    except (requests.RequestException,ValueError):
        raise ApiError('No pudimos conectar con la distribuidora. Conservamos tu pedido para reintentar.') from None


def subir_material_tienda(archivo,distribuidora_id,operator_token,operacion_id):
    if archivo is None:raise ApiError('Seleccioná una foto o video.',400)
    if archivo.size>16*1024*1024:raise ApiError('El archivo supera 16 MB.',400)
    from uuid import UUID
    try:oid=str(UUID(str(operacion_id)))
    except (ValueError,TypeError):raise ApiError('Referencia de subida inválida.',400)
    base=settings.URBAN_API_BASE.rstrip('/')+'/'
    parsed=urlsplit(base)
    if parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment or not settings.URBAN_API_TOKEN:
        raise ApiError('Falta configurar la conexión HTTPS con Urban Soft.')
    headers={'Authorization':'Bearer '+settings.URBAN_API_TOKEN,'X-Midistri-Operator':operator_token,
        'X-Midistri-Distribuidora':str(distribuidora_id),'X-Midistri-Operacion':oid,'Accept':'application/json'}
    try:
        archivo.seek(0)
        with requests.request('POST',base+'operator-media-upload/',files={'archivo':('material'+__import__('pathlib').Path(archivo.name).suffix.lower(),archivo,'application/octet-stream')},
                headers=headers,timeout=(5,60),allow_redirects=False,stream=True) as response:
            body=bytearray()
            for chunk in response.iter_content(8192):
                body.extend(chunk)
                if len(body)>65536:raise ApiError('Respuesta de subida inválida.')
            result=json.loads(body.decode('utf-8'))
            if response.status_code!=200:raise ApiError(str(result.get('error','No se pudo subir el material.'))[:300],response.status_code)
            from .multimedia_contract import validar_multimedia
            item=dict(result)
            if item.get('tipo')=='foto':
                # Promo images use the same dedicated UUID endpoint as MP4.
                check=dict(item,tipo='mp4')
                validar_multimedia([check],base)
            else:validar_multimedia([item],base)
            return result
    except (requests.RequestException,ValueError,KeyError,TypeError):
        raise ApiError('No pudimos confirmar la subida. Reintentá con la misma referencia.') from None
