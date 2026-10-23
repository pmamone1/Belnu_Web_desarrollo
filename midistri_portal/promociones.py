"""Per-store promotions with current delegated permissions and a remote audit gate."""
from hashlib import sha256
from uuid import UUID,uuid4
from urllib.parse import urlsplit
import json
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from .client import api,ApiError
from .operadores import perfil_valido,tienda_permitida
from .models import Distribuidora,Tienda,BloquePromocional,CambioPromocional,Publicacion

def enlace_https(value):
    if not value:return ''
    try:
        u=urlsplit(value)
        if u.scheme!='https' or not u.hostname or u.username is not None or u.password is not None or u.port not in (None,443):raise ValueError
        if any(ord(c)<32 for c in value):raise ValueError
    except (ValueError,TypeError):raise ValidationError('Usá enlaces HTTPS sin credenciales.') from None
    return value

class PromocionForm(forms.Form):
    titulo=forms.CharField(max_length=150,label='Título')
    texto=forms.CharField(max_length=1000,required=False,widget=forms.Textarea(attrs={'rows':3}))
    enlace=forms.URLField(max_length=500,required=False,label='Enlace de la promoción')
    tipo=forms.ChoiceField(choices=[('texto','Sólo texto'),('foto','Foto'),('mp4','Video MP4'),('youtube','YouTube'),('vimeo','Vimeo')])
    material_id=forms.CharField(max_length=36,required=False,widget=forms.HiddenInput)
    url=forms.URLField(max_length=500,required=False,label='Enlace del video o recurso')
    orden=forms.IntegerField(min_value=0,max_value=9999,initial=0,label='Orden')
    activo=forms.BooleanField(required=False,initial=True,label='Publicar en la tienda')
    material_producto=forms.CharField(required=False,max_length=100,label='Material de producto (opcional)')
    def clean_enlace(self):return enlace_https(self.cleaned_data['enlace'])

def validar_material(datos,did,existente=None):
    tipo=datos['tipo'];url=datos['url'];material=datos['material_id']
    selected=datos.pop('material_producto','')
    if selected:
        try:
            pid,index=map(int,selected.split(':'))
            product=Publicacion.objects.get(pk=pid,distribuidora_id=did,activa=True)
            media=product.multimedia[index]
            if index<0:raise ValueError
        except (ValueError,IndexError,Publicacion.DoesNotExist):raise ValidationError('El material del producto cambió; volvé a seleccionarlo.') from None
        datos.update(tipo=media['tipo'],url=media['url'],material_id='')
        datos['origen_publicacion_id']=product.pk
        return
    if existente and (existente.tipo,existente.url,existente.material_id)==(tipo,url,material):
        if not datos['activo'] or fuente_vigente(existente):
            datos['origen_publicacion_id']=existente.origen_publicacion_id
            return
    if tipo=='texto':
        if url or material:raise ValidationError('Una promoción de texto no lleva archivo.')
        return
    if tipo in ('youtube','vimeo'):
        from .multimedia_contract import validar_multimedia
        validar_multimedia([dict(id=str(uuid4()),tipo=tipo,url=url,principal=False,orden=0)],settings.URBAN_API_BASE)
        if material:raise ValidationError('El enlace externo no necesita archivo.')
        return
    if not material:
        for product in Publicacion.objects.filter(distribuidora_id=did,activa=True).only('multimedia','producto_id'):
            if any(i.get('tipo')==tipo and i.get('url')==url for i in product.multimedia):
                datos['origen_publicacion_id']=product.pk;return
    try:mid=str(UUID(material))
    except (ValueError,TypeError):raise ValidationError('Subí y elegí un archivo para la promoción.') from None
    base=urlsplit(settings.URBAN_API_BASE)
    expected=base.scheme+'://'+base.netloc+'/midistri-media/'+mid+'/'
    if url!=expected:raise ValidationError('El archivo no corresponde a esta promoción.')


def perfil_actual(perfil,token,tienda_id):
    fresh=perfil_valido(api('operator-profile',operator_token=token))
    if fresh['operador_id']!=perfil['operador_id'] or 'midistri.tienda_configurar' not in fresh['permisos']:
        raise ApiError('Sin permiso para configurar promociones.',403)
    return fresh,tienda_permitida(fresh,tienda_id)

def guardar_promocion(perfil,tienda_id,datos,revision,operacion_id,token,*,bloque_id=None):
    fresh,did=perfil_actual(perfil,token,tienda_id)
    form=PromocionForm(datos)
    if not form.is_valid():raise ValidationError(form.errors.as_text())
    existente=BloquePromocional.objects.filter(pk=bloque_id,tienda__distribuidora_id=did).first() if bloque_id else None
    clean=form.cleaned_data;validar_material(clean,did,existente)
    clean.setdefault('origen_publicacion_id',None)
    if type(revision) is not int or revision<0:raise ValidationError('Revisión inválida.')
    try:oid=UUID(str(operacion_id));bid=UUID(str(bloque_id)) if bloque_id else uuid4()
    except (ValueError,TypeError):raise ValidationError('Referencia inválida.') from None
    fp=sha256(json.dumps(clean,sort_keys=True).encode()).hexdigest()
    # Commit intent BEFORE the remote side effect, preserving idempotency after a lost response.
    with transaction.atomic():
        d=Distribuidora.objects.select_for_update().get(pk=did,activa=True)
        tienda,_=Tienda.objects.get_or_create(distribuidora=d)
        old=CambioPromocional.objects.select_related('bloque').filter(pk=oid).first()
        if old:
            if old.bloque.tienda_id!=tienda.pk or old.operador_id!=fresh['operador_id'] or old.bloque_id!=bid:
                raise ApiError('Fuera de alcance.',403)
            if old.huella!=fp:raise ValidationError('La referencia ya se usó con otro contenido.')
            if old.estado=='confirmado':return old.bloque
            cambio=old
        else:
            row=BloquePromocional.objects.filter(pk=bid).first()
            if row and row.tienda_id!=tienda.pk:raise ApiError('Promoción fuera de alcance.',403)
            if row and CambioPromocional.objects.filter(bloque=row,estado='pendiente').exists():
                raise ValidationError('Hay una publicación pendiente. Reintentá la misma operación desde la lista.')
            if row and row.revision!=revision or not row and revision!=0:
                raise ValidationError('La promoción cambió. Recargá la pantalla.')
            if clean['activo'] and (not row or not row.activo) and BloquePromocional.objects.filter(tienda=tienda,activo=True).count()>=10:
                raise ValidationError('Hasta diez promociones activas por tienda.')
            if row is None:row=BloquePromocional.objects.create(id=bid,tienda=tienda,titulo=clean['titulo'],activo=False)
            before={k:getattr(row,k) for k in ('titulo','texto','enlace','tipo','url','material_id','orden','activo','revision','origen_publicacion_id')}
            cambio=CambioPromocional.objects.create(id=oid,bloque=row,operador_id=fresh['operador_id'],
                antes=before,despues=dict(clean,revision=revision+1),huella=fp,estado='pendiente')
    return confirmar_pendiente(perfil,did,cambio.pk,token)

def confirmar_pendiente(perfil,tienda_id,operacion_id,token):
    fresh,did=perfil_actual(perfil,token,tienda_id)
    cambio=CambioPromocional.objects.select_related('bloque__tienda').get(pk=operacion_id)
    if cambio.bloque.tienda.distribuidora_id!=did or cambio.operador_id!=fresh['operador_id']:
        raise ApiError('Operación fuera de alcance.',403)
    if cambio.estado=='confirmado':return cambio.bloque
    data=cambio.despues;revision=data['revision']-1
    result=api('operator-promotion-reference',method='POST',operator_token=token,data={
        'distribuidora':did,'bloque':str(cambio.bloque_id),'material':data['material_id'] or None,
        'activo':data['activo'],'revision':revision,'operacion':str(cambio.pk)})
    if result.get('ok') is not True or result.get('revision')!=revision+1:
        raise ApiError('No se confirmó la publicación en Urban Soft.')
    with transaction.atomic():
        Distribuidora.objects.select_for_update().get(pk=did,activa=True)
        cambio=CambioPromocional.objects.select_for_update().get(pk=cambio.pk)
        if cambio.estado=='confirmado':return cambio.bloque
        row=BloquePromocional.objects.get(pk=cambio.bloque_id)
        if row.revision!=revision:raise ValidationError('La revisión local cambió; requiere conciliación.')
        for k,v in data.items():setattr(row,k,v)
        row.save();cambio.estado='confirmado';cambio.save(update_fields=['estado'])
    return row

def fuente_vigente(row):
    if not row.origen_publicacion_id:return True
    product=row.origen_publicacion
    return (product.activa and product.distribuidora_id==row.tienda.distribuidora_id
        and any(m.get('tipo')==row.tipo and m.get('url')==row.url for m in product.multimedia))

def promociones_publicas(distribuidora):
    if not distribuidora or not getattr(settings,'MIDISTRI_MULTIMEDIA_ENABLED',False):return []
    rows=BloquePromocional.objects.filter(tienda__distribuidora=distribuidora,activo=True).select_related('origen_publicacion','tienda').order_by('orden','id')
    return [r for r in rows if fuente_vigente(r)][:10]
