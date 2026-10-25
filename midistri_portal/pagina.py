"""One private draft and immutable publication versions per store."""
from copy import deepcopy
from hashlib import sha256
from uuid import UUID
import json
from types import SimpleNamespace
from django.core import signing
from django.core.exceptions import ValidationError
from django.db import transaction
from .client import api,ApiError
from .operadores import perfil_valido,tienda_permitida
from .models import Tienda,Distribuidora,Publicacion
from .pagina_models import PaginaTienda,VersionPagina,EdicionPagina
from .promociones import enlace_https
SALT='midistri.pagina.v1'
DISENOS=[('compacto','Catálogo compacto'),('fotos','Fotos grandes'),('promociones','Promociones'),('lista','Lista rápida')]
MENSAJES={
 'encabezado':'',
 'nav_catalogo':'Catálogo','nav_distribuidor':'Acceso Distribuidor',
 'titulo':'Elegí los productos para tu Kiosco!',
 'subtitulo':'Portal para realizar pedidos. La distribuidora confirma disponibilidad.',
 'bienvenida':'','instrucciones':'','carrito':'Este pedido queda sujeto a disponibilidad y aceptación por parte de la distribuidora.',
 'recibido':'Recibimos tu pedido','contacto':'','boton_pedido':'Ver mi pedido',
}
TIPOS=('texto','banner','carrusel_fotos','carrusel_productos','video','contacto','catalogo')

def huella(data):
    return sha256(json.dumps(data,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()

def inicial(tienda):
    blocks=[]
    for row in tienda.bloquepromocional_set.filter(activo=True).order_by('orden','id'):
        slide={'titulo':'','texto':'','enlace':'','boton':'','tipo':row.tipo,'url':row.url}
        if row.origen_publicacion_id:slide['publicacion']=row.origen_publicacion_id
        if row.material_id:slide['material_id']=row.material_id
        blocks.append({'id':str(row.pk),'tipo':'texto' if row.tipo=='texto' else ('video' if row.tipo!='foto' else 'banner'),
            'titulo':row.titulo,'texto':row.texto,'enlace':row.enlace,'activo':True,
            'segundos':5,'automatico':False,'diapositivas':[] if row.tipo=='texto' else [slide]})
    blocks += [{'id':'bienvenida','tipo':'texto','mensaje':'bienvenida','activo':True},
        {'id':'catalogo','tipo':'catalogo','activo':True},{'id':'contacto','tipo':'contacto','activo':True}]
    return {'version':1,'inicial_anterior':True,'diseno':'compacto','tema':tienda.tema if tienda.tema in ('claro','nocturno','azul','verde') else 'claro',
        'presentacion':{'logo':tienda.logo.url if tienda.logo else '', 'email':tienda.distribuidora.email_respuesta or tienda.email,'telefono':tienda.telefono},
        'mensajes':dict(MENSAJES,bienvenida=tienda.bienvenida,instrucciones=tienda.instrucciones),
        'bloques':blocks}

def vigente_slide(slide,did):
    if slide.get('publicacion'):
        product=Publicacion.objects.filter(pk=slide['publicacion'],distribuidora_id=did,activa=True,distribuidora__activa=True).first()
        from .catalogo_elegible import disponible
        if not product or not disponible(product):return None
        options=product.multimedia+[{ 'tipo':'foto','url':i['url'] if isinstance(i,dict) else i} for i in product.imagenes]
        if not any(m.get('tipo')==slide['tipo'] and m.get('url')==slide['url'] for m in options):return None
        return dict(slide,producto_id=product.producto_id,producto=product)
    return dict(slide)

def texto(value,limit=1000):
    if not isinstance(value,str) or len(value)>limit:raise ValidationError('Texto demasiado largo o inválido.')
    return value.strip()

def validar_pagina(data,did,fuentes=True):
    try:
        if not isinstance(data,dict) or data.get('version')!=1:raise ValueError
        if data['diseno'] not in dict(DISENOS) or data['tema'] not in ('claro','nocturno','azul','verde'):raise ValueError
        messages={k:texto(data.get('mensajes',{}).get(k,''),150 if k=='encabezado' else 80 if k.startswith('nav_') else 1000) for k in MENSAJES}
        presentation=data.get('presentacion',{})
        presentation={k:texto(presentation.get(k,''),500) for k in ('logo','email','telefono')}
        from .marcas import MARCAS
        for key in ('marca','favicon_marca'):
            value=data.get('presentacion',{}).get(key,'bolsa' if key=='marca' else '')
            if not isinstance(value,str) or value not in dict(MARCAS) and not (key=='favicon_marca' and value==''):raise ValueError
            presentation[key]=value
        if presentation['logo']:
            existing=Tienda.objects.filter(distribuidora_id=did).first()
            legacy=existing.logo.url if existing and existing.logo else ''
            if presentation['logo']!=legacy:enlace_https(presentation['logo'])
        from django.core.validators import validate_email
        if presentation['email']:validate_email(presentation['email'])
        raw=data['bloques']
        if not isinstance(raw,list) or len(raw)>40:raise ValueError
        if sum(b.get('activo') is True and b.get('tipo') not in ('catalogo','contacto') and not b.get('mensaje') for b in raw)>10:raise ValueError
        blocks=[];seen=set();catalogs=0
        for b in raw:
            bid=texto(b['id'],40)
            if bid in seen or not bid or b['tipo'] not in TIPOS or type(b['activo']) is not bool:raise ValueError
            seen.add(bid)
            x={'id':bid,'tipo':b['tipo'],'activo':b['activo'],'titulo':texto(b.get('titulo',''),150),'texto':texto(b.get('texto','')),
                'enlace':enlace_https(texto(b.get('enlace',''),500)),'boton':texto(b.get('boton',''),80),
                'automatico':b.get('automatico',b['tipo']=='banner'),'segundos':b.get('segundos',5),
                'formato':b.get('formato','horizontal'),'ajuste':b.get('ajuste','contain')}
            if type(x['automatico']) is not bool or type(x['segundos']) is not int or not 3<=x['segundos']<=15:raise ValueError
            if x['formato'] not in ('horizontal','cuadrado') or x['ajuste'] not in ('contain','cover'):raise ValueError
            if 'estilo' in b:
                from .editor_estilos import validar_estilo
                x['estilo']=validar_estilo(b['estilo'])
                if b['tipo'] in ('catalogo','contacto'):x['estilo']['zona']='centro'
            if b.get('mensaje'):
                if b['mensaje'] not in ('bienvenida','instrucciones'):raise ValueError
                x['mensaje']=b['mensaje']
            if b['tipo']=='catalogo':
                catalogs+=1;x['activo']=True
            slides=b.get('diapositivas',[])
            if not isinstance(slides,list) or len(slides)>20:raise ValueError
            x['diapositivas']=[]
            for src in slides:
                slide={k:texto(src.get(k,''),500 if k in ('url','enlace') else 150 if k=='titulo' else 1000) for k in ('titulo','texto','url','enlace','boton')}
                slide.update(tipo=src['tipo'])
                if slide['tipo'] not in ('foto','mp4','youtube','vimeo'):raise ValueError
                enlace_https(slide['url']);enlace_https(slide['enlace'])
                if src.get('publicacion'):
                    if type(src['publicacion']) is not int:raise ValueError
                    slide['publicacion']=src['publicacion']
                    if fuentes and x['activo'] and not vigente_slide(slide,did):raise ValidationError('Producto o material retirado. Reemplazalo u ocultá el bloque.')
                elif src.get('material_id'):
                    slide['material_id']=str(UUID(src['material_id']))
                    from urllib.parse import urlsplit
                    from django.conf import settings
                    u=urlsplit(settings.URBAN_API_BASE)
                    if slide['url']!=u.scheme+'://'+u.netloc+'/midistri-media/'+slide['material_id']+'/':raise ValueError
                elif slide['tipo'] in ('youtube','vimeo'):
                    from .multimedia_contract import validar_multimedia
                    from django.conf import settings
                    validar_multimedia([dict(id=str(UUID(int=0)),tipo=slide['tipo'],url=slide['url'],principal=False,orden=0)],settings.URBAN_API_BASE)
                else:raise ValueError
                x['diapositivas'].append(slide)
            blocks.append(x)
        if catalogs!=1:raise ValidationError('Debe haber exactamente un catálogo visible.')
        return {'version':1,'diseno':data['diseno'],'tema':data['tema'],'mensajes':messages,'presentacion':presentation,'bloques':blocks}
    except (KeyError,TypeError,ValueError,AttributeError):
        raise ValidationError('Página inválida: hasta10 bloques activos,20 fotos por carrusel y rotación entre3 y15 segundos.') from None

def autorizar(perfil,did,token):
    fresh=perfil_valido(api('operator-profile',operator_token=token))
    if fresh['operador_id']!=perfil['operador_id'] or 'midistri.tienda_configurar' not in fresh['permisos']:raise ApiError('Sin permiso para editar esta tienda.',403)
    return fresh,tienda_permitida(fresh,did)

def _pagina(did):
    # Active distributor lock serializes creation as well as edits on PostgreSQL/MariaDB.
    d=Distribuidora.objects.select_for_update().filter(pk=did,activa=True).first()
    if d is None:raise ApiError('Sincronizá el catálogo para habilitar esta tienda antes de editar su página.',409)
    t,_=Tienda.objects.get_or_create(distribuidora=d)
    row=PaginaTienda.objects.filter(tienda=t).first()
    if row:
        row.datos=validar_pagina(row.datos,did,fuentes=False)
        return row
    data=inicial(t)
    v=VersionPagina.objects.create(tienda=t,revision=0,datos=data,huella=huella(data),estado='publicada')
    return PaginaTienda.objects.create(tienda=t,datos=validar_pagina(data,did,fuentes=False),publicada=v)

def borrador_tienda(perfil,did,token):
    _,did=autorizar(perfil,did,token)
    with transaction.atomic():return _pagina(did)

def guardar_borrador(perfil,did,data,revision,operacion,token,metadata=None):
    fresh,did=autorizar(perfil,did,token)
    if type(revision) is not int or revision<0:raise ValidationError('Revisión inválida.')
    clean=validar_pagina(data,did);fp=huella(clean);oid=UUID(str(operacion))
    with transaction.atomic():
        page=_pagina(did)
        old=EdicionPagina.objects.filter(pk=oid).first()
        if old:
            if old.pagina_id!=page.pk or old.operador_id!=fresh['operador_id'] or old.huella!=fp:raise ValidationError('La operación ya corresponde a otra edición.')
            return page
        if page.pendiente_id:raise ValidationError('Hay una publicación por confirmar. Reintentá antes de editar.')
        if page.revision!=revision:raise ValidationError('El borrador cambió. Recargá para no perder cambios.')
        page.datos=clean;page.revision+=1;page.save(update_fields=['datos','revision'])
        EdicionPagina.objects.create(id=oid,pagina=page,operador_id=fresh['operador_id'],revision=page.revision,huella=fp,datos=dict(clean,_subida=metadata) if metadata else clean)
        return page

def payload_remoto(page,oid):
    materials=[];sources=[]
    for b in page.datos['bloques']:
        if not b['activo']:continue
        for s in b.get('diapositivas',[]):
            if s.get('material_id'):materials.append(s['material_id'])
            elif s.get('publicacion'):
                item=vigente_slide(s,page.tienda.distribuidora_id)
                if not item:raise ValidationError('Una fuente cambió. Revisá los materiales.')
                sources.append({k:item[k] for k in ('producto_id','tipo','url')})
    logo=page.datos['presentacion'].get('logo','')
    if '/midistri-media/' in logo:
        try:materials.append(str(UUID(logo.rstrip('/').rsplit('/',1)[-1])))
        except ValueError:raise ValidationError('Logo inválido.')
    return dict(distribuidora=page.tienda.distribuidora_id,operacion=str(oid),huella=huella(page.datos),
        materiales=sorted(set(materials)),fuentes=sources)

def revisar_borrador(perfil,did,token):
    page=borrador_tienda(perfil,did,token)
    validar_pagina(page.datos,did)
    oid=page.pendiente_id or UUID(int=0) # validation does not record a remote operation
    result=api('operator-page-validate',method='POST',operator_token=token,data=payload_remoto(page,oid))
    if result.get('ok') is not True or result.get('huella')!=huella(page.datos):raise ApiError('No se confirmó la revisión de fuentes.')
    from uuid import uuid4
    return signing.dumps({'did':did,'operador':perfil['operador_id'],'revision':page.revision,
        'huella':huella(page.datos),'operacion':str(page.pendiente_id or uuid4())},salt=SALT)

def publicar_revision(perfil,did,firma,token):
    fresh,did=autorizar(perfil,did,token)
    try:review=signing.loads(firma,salt=SALT,max_age=1800)
    except signing.BadSignature:raise ValidationError('La vista previa venció. Revisá nuevamente.') from None
    if review['did']!=did or review['operador']!=fresh['operador_id']:raise ApiError('Vista previa fuera de alcance.',403)
    with transaction.atomic():
        page=_pagina(did);oid=UUID(review['operacion'])
        previous=VersionPagina.objects.filter(pk=oid).first()
        if previous and (previous.tienda_id!=page.tienda_id or previous.operador_id!=fresh['operador_id']):raise ApiError('Operación fuera de alcance.',403)
        if previous and previous.estado=='publicada':return previous
        if previous and previous.estado!='pendiente':raise ValidationError('Esta intención se descartó. Revisá una nueva versión.')
        if page.revision!=review['revision'] or huella(page.datos)!=review['huella']:raise ValidationError('Cambió el borrador. Revisá antes de publicar.')
        if page.pendiente_id and page.pendiente_id!=oid:raise ValidationError('Reintentá la publicación pendiente.')
        clean=validar_pagina(page.datos,did)
        version=previous or VersionPagina.objects.create(id=oid,tienda=page.tienda,revision=page.revision,
            datos=clean,huella=review['huella'],operador_id=fresh['operador_id'])
        page.pendiente=version;page.save(update_fields=['pendiente'])
        payload=payload_remoto(page,oid)
    # Intent is durable before the remote gate. An uncertain reply never changes the public page.
    try:
        result=api('operator-page-publish',method='POST',operator_token=token,data=payload)
    except ApiError as error:
        if 400<=error.status<500:
            with transaction.atomic():
                current=_pagina(did)
                if current.pendiente_id==oid:
                    current.pendiente=None;current.revision+=1
                    current.save(update_fields=['pendiente','revision'])
                    VersionPagina.objects.filter(pk=oid,estado='pendiente').update(estado='rechazada')
        raise
    if result.get('ok') is not True or result.get('huella')!=version.huella:raise ApiError('Publicación sin confirmar; reintentá la misma versión.')
    with transaction.atomic():
        page=_pagina(did)
        if page.pendiente_id!=oid:raise ValidationError('Publicación pendiente cambió; requiere revisión.')
        page.publicada=version;page.pendiente=None;page.save(update_fields=['publicada','pendiente'])
        version.estado='publicada';version.save(update_fields=['estado'])
    return version

def pagina_publica(distribuidora):
    if not distribuidora:return dict(version=1,diseno='compacto',tema='claro',mensajes=dict(MENSAJES),presentacion={},bloques=[])
    row=PaginaTienda.objects.filter(tienda__distribuidora=distribuidora).select_related('publicada').first()
    if row and row.publicada_id:return deepcopy(row.publicada.datos)
    t=Tienda.objects.filter(distribuidora=distribuidora).first()
    if t:return inicial(t)
    return dict(version=1,diseno='compacto',tema='claro',mensajes=dict(MENSAJES),presentacion={},bloques=[{'id':'catalogo','tipo':'catalogo','activo':True}])

def bloques_vigentes(data,did,preview=False):
    from django.conf import settings
    output=[]
    for b in data.get('bloques',[]):
        if not b.get('activo'):continue
        if not preview and not getattr(settings,'MIDISTRI_MULTIMEDIA_ENABLED',False) and b['tipo'] not in ('catalogo','contacto') and not b.get('mensaje'):continue
        x=deepcopy(b);slides=[]
        from .editor_estilos import validar_estilo,estilo_css
        x['estilo']=validar_estilo(b.get('estilo',{}));x['css']=estilo_css(x['estilo'])
        for s in b.get('diapositivas',[]):
            item=vigente_slide(s,did)
            if not item:continue
            if preview and item.get('material_id'):
                item['url']='/portal/administrar/promociones/material/'+str(did)+'/'+item['material_id']+'/'
            slides.append(item)
        x['diapositivas']=slides
        if b['tipo'] in ('banner','carrusel_fotos','carrusel_productos','video') and not slides:continue
        output.append(x)
    return output

def restaurar(perfil,did,version_id,revision,token):
    v=VersionPagina.objects.filter(pk=version_id,tienda__distribuidora_id=did,estado='publicada').first()
    if v is None:raise ApiError('Versión fuera de alcance.',403)
    from uuid import uuid4
    data=deepcopy(v.datos)
    for block in data['bloques']:
        slides=block.get('diapositivas',[])
        block['diapositivas']=[s for s in slides if vigente_slide(s,did)]
        if slides and not block['diapositivas']:block['activo']=False
    return guardar_borrador(perfil,did,data,revision,str(uuid4()),token)

def descartar_pendiente(perfil,did,ident,revision,motivo,token):
    fresh,did=autorizar(perfil,did,token)
    reason=texto(motivo,500)
    if not reason:raise ValidationError('Indicá por qué descartás la publicación pendiente.')
    with transaction.atomic():
        page=_pagina(did)
        if page.pendiente_id!=UUID(str(ident)) or page.revision!=revision:raise ValidationError('La publicación cambió. Recargá el editor.')
        version=page.pendiente
        version.estado='descartada';version.save(update_fields=['estado'])
        page.pendiente=None;page.revision+=1;page.save(update_fields=['pendiente','revision'])
        from uuid import uuid4
        EdicionPagina.objects.create(id=uuid4(),pagina=page,operador_id=fresh['operador_id'],revision=page.revision,
            huella=huella(page.datos),datos={'accion':'descartar_intento','version':str(version.pk),'motivo':reason})
        return page
