"""Cookie + tab proof. No Urban bearer credential is sent to JavaScript."""
from collections.abc import MutableMapping
from hashlib import sha256
import re
import secrets
from uuid import UUID
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from .models import SesionVendedorPortal
from .contract import perfil_valido


def hash_texto(value):return sha256(value.encode()).hexdigest()


def datos_prueba(request):
    try:
        ident=str(UUID(request.headers.get('X-Midistri-Tab','')))
        proof=request.headers.get('X-Midistri-Tab-Proof','')
        if not re.fullmatch('[0-9a-f]{64}',proof):raise ValueError
    except (ValueError,TypeError,AttributeError):raise PermissionDenied('Iniciá tu acceso en esta pestaña.') from None
    return ident,proof


def navegador(request,crear=False):
    value=request.session.get('midistri_browser')
    if not value and crear:
        value=secrets.token_urlsafe(32);request.session['midistri_browser']=value
        request.session.set_expiry(0)
    return hash_texto(value) if value else None


def crear_sesion_pestana(request,perfil,token_urban,tab_id,prueba):
    perfil=perfil_valido(perfil)
    ident,proof=datos_prueba(request)
    if ident!=str(tab_id) or not secrets.compare_digest(proof,prueba):raise PermissionDenied
    if not isinstance(token_urban,str) or not 20<=len(token_urban)<=100:raise PermissionDenied
    browser=navegador(request,True)
    old=SesionVendedorPortal.objects.filter(pk=ident).first()
    if old and (old.navegador_hash!=browser or old.prueba_hash!=hash_texto(proof)):raise PermissionDenied
    SesionVendedorPortal.objects.update_or_create(pk=ident,defaults={'navegador_hash':browser,
        'prueba_hash':hash_texto(proof),'token_urban':token_urban,'vendedor_id':perfil['id'],
        'distribuidora_id':perfil['distribuidora_id'],'datos':{},'revocado':False,'actividad':timezone.now()})
    request.session.cycle_key()
    from .analitica_captura import registrar_ingreso
    registrar_ingreso(request,perfil,token_urban,ident)
    return {'fase':'dentro','url':'/portal/'}


def resolver_sesion_pestana(request):
    ident,proof=datos_prueba(request)
    browser=navegador(request)
    rows=SesionVendedorPortal.objects.select_for_update().filter(pk=ident)
    if request.path!='/portal/salir/':rows=rows.filter(revocado=False)
    row=rows.first()
    if row is None or not browser or not secrets.compare_digest(row.navegador_hash,browser) or not secrets.compare_digest(row.prueba_hash,hash_texto(proof)):
        raise PermissionDenied('Tu acceso no está disponible en esta pestaña. Ingresá con tu Email.')
    return row


def cerrar_sesion_pestana(request):
    row=getattr(request,'midistri_tab',None)
    if row:
        row.revocado=True;row.token_urban='';row.datos={}


class TabSession(MutableMapping):
    """Reuse the tested order flow, isolating its entire state and messages."""
    PRIVATE={'midistri_token','midistri_cart','midistri_cart_id','midistri_revision','midistri_catalogo_filtros','_messages'}
    def __init__(self,original,row):self.original=original;self.row=row;self.empty={}
    def __getitem__(self,key):
        if key=='midistri_token':
            if self.row and self.row.token_urban:return self.row.token_urban
            raise KeyError(key)
        if key in self.PRIVATE:return (self.row.datos if self.row else self.empty)[key]
        return self.original[key]
    def __setitem__(self,key,value):
        if key=='midistri_token':
            if self.row:self.row.token_urban=value
        elif key in self.PRIVATE:(self.row.datos if self.row else self.empty).__setitem__(key,value)
        else:self.original[key]=value
    def __delitem__(self,key):
        if key=='midistri_token':
            if self.row:self.row.token_urban=''
        elif key in self.PRIVATE:del (self.row.datos if self.row else self.empty)[key]
        else:del self.original[key]
    def __iter__(self):
        return iter(set(self.original)-self.PRIVATE | set(self.row.datos if self.row else self.empty) | ({'midistri_token'} if self.row and self.row.token_urban else set()))
    def __len__(self):return len(list(iter(self)))
    def __getattr__(self,name):return getattr(self.original,name)
    @property
    def modified(self):return self.original.modified
    @modified.setter
    def modified(self,value):self.original.modified=value
    @property
    def accessed(self):return self.original.accessed
    @accessed.setter
    def accessed(self,value):self.original.accessed=value
    def set_expiry(self,value):self.original.set_expiry(0)
