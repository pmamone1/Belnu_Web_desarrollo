"""Public storefront content, with current Urban permission and local audit."""
from io import BytesIO
from uuid import UUID,uuid4
import warnings
from PIL import Image,UnidentifiedImageError
from django import forms
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from .client import api,ApiError
from .operadores import perfil_valido,tienda_permitida
from .models import Distribuidora,Tienda,CambioTienda

TEMAS=[('claro','Claro'),('nocturno','Nocturno'),('azul','Azul'),('verde','Verde')]

class TiendaForm(forms.Form):
    tema=forms.ChoiceField(choices=TEMAS,required=False,label='Tema predeterminado')
    def clean_tema(self):return self.cleaned_data.get('tema') or 'claro'

    email=forms.EmailField(required=False,max_length=254,label='Email de contacto')
    telefono=forms.CharField(required=False,max_length=40,label='Teléfono de contacto')
    bienvenida=forms.CharField(required=False,max_length=500,widget=forms.Textarea(attrs={'rows':3}))
    instrucciones=forms.CharField(required=False,max_length=1000,widget=forms.Textarea(attrs={'rows':4}),label='Instrucciones para pedidos')

def validar_logo(archivo):
    try:
        raw=archivo.read(2*1024*1024+1)
        if not raw or len(raw)>2*1024*1024:raise ValueError
        with warnings.catch_warnings():
            warnings.simplefilter('error',Image.DecompressionBombWarning)
            with Image.open(BytesIO(raw)) as im:
                if im.format not in ('PNG','JPEG','WEBP') or im.width*im.height>8_000_000:raise ValueError
                im.verify()
            with Image.open(BytesIO(raw)) as im:
                im=im.convert('RGBA' if 'A' in im.getbands() else 'RGB')
                im.thumbnail((768,768))
                clean=Image.new(im.mode,im.size);clean.paste(im)
                out=BytesIO();clean.save(out,format='PNG')
        data=out.getvalue()
        if len(data)>2*1024*1024:raise ValueError
        return ContentFile(data,name=uuid4().hex+'.png')
    except (ValueError,OSError,UnidentifiedImageError,Image.DecompressionBombError,Image.DecompressionBombWarning):
        raise ValidationError('Logo inválido. Use PNG, JPG o WebP hasta 2 MB y ocho megapíxeles.') from None

def _confirmar(cambio,token):
    if cambio.confirmado_urban:return
    try:
        result=api('operator-store-audit',method='POST',operator_token=token,
            data={'operacion':str(cambio.pk),'distribuidora':cambio.tienda.distribuidora_id,
                  'revision':cambio.despues['revision'],'huella':cambio.huella})
        if result.get('ok') is True:
            CambioTienda.objects.filter(pk=cambio.pk).update(confirmado_urban=True)
    except ApiError:pass

def guardar_tienda(perfil,dist_id,datos,logo=None,*,revision,operacion_id,token,quitar_logo=False):
    fresh=perfil_valido(api('operator-profile',operator_token=token))
    if fresh['operador_id']!=perfil['operador_id'] or 'midistri.tienda_configurar' not in fresh['permisos']:
        raise ApiError('Sin permiso para configurar la tienda.',403)
    did=tienda_permitida(fresh,dist_id);oid=UUID(str(operacion_id))
    form=TiendaForm(datos)
    if not form.is_valid():raise ValidationError(form.errors.as_text())
    cleaned=form.cleaned_data;archivo=validar_logo(logo) if logo else None
    from hashlib import sha256
    import json
    request_fp=sha256(json.dumps([cleaned,bool(quitar_logo),
        sha256(archivo.read()).hexdigest() if archivo else None],sort_keys=True).encode()).hexdigest()
    if archivo:archivo.seek(0)
    new_file=None
    try:
        with transaction.atomic():
            d,created=Distribuidora.objects.get_or_create(pk=did,
                defaults={'nombre':next(x['nombre'] for x in fresh['distribuidoras'] if x['id']==did)})
            Tienda.objects.get_or_create(distribuidora=d)
            tienda=Tienda.objects.select_for_update().get(distribuidora=d)
            cambio=CambioTienda.objects.filter(pk=oid).first()
            if cambio:
                if cambio.tienda_id!=tienda.pk or cambio.operador_id!=fresh['operador_id']:
                    raise ApiError('Operación fuera de alcance.',403)
                if cambio.despues.get('peticion_huella')!=request_fp:
                    raise ValidationError('La referencia ya fue utilizada con otro contenido.')
            else:
                if tienda.revision!=revision:raise ValidationError('La tienda cambió. Recargue antes de guardar.')
                before={k:getattr(tienda,k) for k in cleaned}
                before['logo']=tienda.logo.name;before['revision']=tienda.revision
                for k,v in cleaned.items():setattr(tienda,k,v)
                if archivo:
                    tienda.logo.save(archivo.name,archivo,save=False);new_file=tienda.logo.name
                elif quitar_logo:tienda.logo=''
                tienda.revision+=1;tienda.save()
                after={k:getattr(tienda,k) for k in cleaned}
                after.update(logo=tienda.logo.name,revision=tienda.revision,peticion_huella=request_fp)
                fp=sha256(json.dumps(after,sort_keys=True).encode()).hexdigest()
                cambio=CambioTienda.objects.create(id=oid,tienda=tienda,operador_id=fresh['operador_id'],
                    antes=before,despues=after,huella=fp)
    except Exception:
        if new_file:Tienda._meta.get_field('logo').storage.delete(new_file)
        raise
    _confirmar(cambio,token)
    return tienda

def presentacion_publica(distribuidora):
    if not distribuidora:return None
    from .pagina import pagina_publica
    from .pagina_views import contenido_contexto
    return contenido_contexto(pagina_publica(distribuidora),distribuidora)['presentacion']
