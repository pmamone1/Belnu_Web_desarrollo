from .sesiones_operador import token_operador
from copy import deepcopy
from uuid import uuid4
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.contrib import messages
from django.shortcuts import render,redirect
from django.views.decorators.http import require_http_methods,require_GET
from . import pagina as p
from .pagina_forms import PaginaForm
from .models import Publicacion,VersionPagina
from .operadores_views import contexto_panel,fallo
from .client import ApiError,subir_material_tienda
from .presentacion import TEMAS
from types import SimpleNamespace

def privada(response):
    response['Cache-Control']='private, no-store'
    response['X-Robots-Tag']='noindex, nofollow'
    return response

def url(did):return '/portal/administrar/pagina/?distribuidora='+str(did)

def recursos(did):
    result=[]
    for product in Publicacion.objects.filter(distribuidora_id=did,activa=True).order_by('nombre'):
        media=product.multimedia or [dict(tipo='foto',url=i['url'] if isinstance(i,dict) else i) for i in product.imagenes]
        for index,m in enumerate(media[:30]):
            result.append(dict(clave=str(product.pk)+':'+str(index),producto=product.nombre,
                tipo=m['tipo'],url=m['url'],publicacion=product.pk))
    return result

def contenido_contexto(page,d,preview=False):
    data=page.datos if hasattr(page,'datos') else page
    presentation=dict(data['presentacion'])
    logo=presentation.get('logo')
    if preview and logo and '/midistri-media/' in logo:
        logo='/portal/administrar/promociones/material/'+str(d.pk)+'/'+logo.rstrip('/').rsplit('/',1)[-1]+'/'
    presentation['logo']=SimpleNamespace(url=logo) if logo else None
    presentation.update(tema=data['tema'],bienvenida=data['mensajes'].get('bienvenida',''),instrucciones=data['mensajes'].get('instrucciones',''))
    return dict(pagina=data,pagina_mensajes={k:v or p.MENSAJES[k] for k,v in data['mensajes'].items()},
        bloques=p.bloques_vigentes(data,d.pk,preview),presentacion=SimpleNamespace(**presentation))

def guardar_accion(request,page,ctx,token):
    data=deepcopy(page.datos);did=ctx['tienda']['id'];accion=request.POST.get('accion')
    if accion=='general':
        form=PaginaForm(request.POST)
        if not form.is_valid():raise ValidationError(form.errors.as_text())
        fields=form.cleaned_data
        data.update(diseno=fields['diseno'],tema=fields['tema'])
        data['mensajes']={k:fields[k] for k in p.MENSAJES}
        data['presentacion'].update(email=fields['email'],telefono=fields['telefono'])
        if request.POST.get('quitar_logo'):data['presentacion']['logo']=''
    elif accion in ('nuevo','editar','subir','bajar','ocultar','mostrar','duplicar','archivar','diapositiva'):
        bid=request.POST.get('bloque')
        block=next((b for b in data['bloques'] if b['id']==bid),None)
        if accion=='nuevo':
            tipo=request.POST.get('tipo')
            if tipo not in ('texto','banner','carrusel_fotos','carrusel_productos','video'):raise ValidationError('Elegí el tipo de bloque.')
            block=dict(id=str(uuid4()),tipo=tipo,titulo='Nuevo '+('banner' if tipo=='banner' else 'bloque'),texto='',activo=True,
                automatico=tipo=='banner',segundos=5,diapositivas=[])
            data['bloques'].insert(0,block)
        elif not block:raise ValidationError('Bloque no encontrado.')
        elif accion=='editar':
            block.update(titulo=request.POST.get('titulo',''),texto=request.POST.get('texto',''),enlace=request.POST.get('enlace',''),
                boton=request.POST.get('boton',''),automatico=request.POST.get('automatico')=='si',
                segundos=int(request.POST.get('segundos',5)),formato=request.POST.get('formato','horizontal'),ajuste=request.POST.get('ajuste','contain'))
            selected=request.POST.getlist('recurso')
            if selected:
                assets={a['clave']:a for a in recursos(did)}
                if any(k not in assets for k in selected):raise ValidationError('Una foto o video cambió. Recargá el editor.')
                block['diapositivas']=[dict(publicacion=assets[k]['publicacion'],tipo=assets[k]['tipo'],url=assets[k]['url'],
                    titulo='',texto='',enlace='',boton='') for k in selected]
        elif accion in ('subir','bajar'):
            index=data['bloques'].index(block);target=index+(-1 if accion=='subir' else 1)
            if 0<=target<len(data['bloques']):data['bloques'][index],data['bloques'][target]=data['bloques'][target],data['bloques'][index]
        elif accion=='duplicar':
            copy=deepcopy(block);copy['id']=str(uuid4());copy['titulo']=copy.get('titulo','')+' (copia)';copy['activo']=False
            data['bloques'].append(copy)
        elif accion=='archivar':
            if block['tipo']=='catalogo':raise ValidationError('El catálogo se conserva visible.')
            block['activo']=False
        elif accion=='diapositiva':
            index=int(request.POST['indice']);slides=block['diapositivas']
            slide=slides[index];direction=request.POST.get('direccion')
            if direction=='quitar':slides.pop(index)
            elif direction in ('subir','bajar'):
                target=index+(-1 if direction=='subir' else 1)
                if 0<=target<len(slides):slides[index],slides[target]=slides[target],slides[index]
            else:slide.update(titulo=request.POST.get('titulo',''),texto=request.POST.get('texto',''),enlace=request.POST.get('enlace',''),boton=request.POST.get('boton',''))
        else:block['activo']=accion=='mostrar'
    elif accion=='archivo':
        result=subir_material_tienda(request.FILES.get('archivo'),did,token,request.POST['operacion'])
        if request.POST.get('como_logo')=='si':
            if result['tipo']!='foto':raise ValidationError('El logo debe ser una imagen.')
            data['presentacion']['logo']=result['url']
        else:
            block=next((b for b in data['bloques'] if b['id']==request.POST.get('bloque')),None)
            if block is None:raise ValidationError('Elegí un bloque para el archivo.')
            block['diapositivas'].append(dict(material_id=result['id'],tipo=result['tipo'],url=result['url'],titulo='',texto='',enlace='',boton=''))
    else:raise ValidationError('Acción inválida.')
    return p.guardar_borrador(ctx['operador'],did,data,int(request.POST['revision']),request.POST['operacion'],token)

@require_http_methods(['GET','POST'])
def editor(request):
    try:
        ctx=contexto_panel(request,'midistri.tienda_configurar')
        did=ctx['tienda']['id'];token=token_operador(request);perfil=ctx['operador']
        page=p.borrador_tienda(perfil,did,token);error=''
        if request.method=='POST':
            try:
                action=request.POST.get('accion')
                if action=='publicar':
                    p.publicar_revision(perfil,did,request.POST.get('firma',''),token)
                    messages.success(request,'Versión completa publicada.')
                elif action=='descartar':
                    p.descartar_pendiente(perfil,did,request.POST['pendiente'],int(request.POST['revision']),request.POST.get('motivo',''),token)
                    messages.success(request,'Publicación pendiente descartada. El borrador queda disponible para corregir.')
                elif action=='restaurar':
                    p.restaurar(perfil,did,request.POST['version'],int(request.POST['revision']),token)
                    messages.success(request,'Versión recuperada en el borrador. Revisá y publicá.')
                else:
                    guardar_accion(request,page,ctx,token)
                    messages.success(request,'Borrador guardado. Todavía no publicado.')
                return redirect(url(did))
            except (ValidationError,ValueError,KeyError,IndexError,ApiError) as e:error=str(e)
            page.refresh_from_db()
        initial=dict(page.datos['mensajes'],**{k:page.datos['presentacion'].get(k,'') for k in ('email','telefono')})
        initial.update(diseno=page.datos['diseno'],tema=page.datos['tema'])
        ctx.update(titulo='Mi tienda · editor de página',page=page,form=PaginaForm(initial=initial),
            recursos=recursos(did),operacion=str(uuid4()),error_form=error,
            advertencias=['Bloque '+b.get('titulo',b['tipo'])+', diapositiva '+str(i+1)+': producto o material retirado. Reemplazala u ocultá el bloque.' for b in page.datos['bloques'] for i,slide in enumerate(b.get('diapositivas',[])) if slide.get('publicacion') and not p.vigente_slide(slide,did)],
            versiones=VersionPagina.objects.filter(tienda=page.tienda,estado='publicada').order_by('-creado')[:30])
        return privada(render(request,'midistri_portal/pagina_editor.html',ctx))
    except (ApiError,ValidationError) as e:return fallo(request,e if isinstance(e,ApiError) else ApiError(str(e),400))

@require_GET
def preview(request):
    try:
        ctx=contexto_panel(request,'midistri.tienda_configurar')
        did=ctx['tienda']['id'];token=token_operador(request);perfil=ctx['operador']
        page=p.borrador_tienda(perfil,did,token)
        firma=p.revisar_borrador(perfil,did,token)
        d=page.tienda.distribuidora
        products=Paginator(Publicacion.objects.filter(distribuidora=d,activa=True),24).get_page(request.GET.get('page'))
        for product in products:
            product.galeria=product.multimedia;product.foto_card=next((m['url'] for m in product.galeria if m['tipo']=='foto'),None)
            product.galeria_dom_id='galeria-'+str(product.producto_id);product.galeria_datos={'nombre':product.nombre,'items':product.galeria}
        ctx.update(contenido_contexto(page,d,True))
        ctx.update(distribuidora=d,productos=products,temas=TEMAS,titulo='Vista previa privada',firma=firma,
            revision=page.revision,preview=True,preview_movil=request.GET.get('pantalla')=='movil')
        return privada(render(request,'midistri_portal/catalogo.html',ctx))
    except (ApiError,ValidationError) as e:return fallo(request,e if isinstance(e,ApiError) else ApiError(str(e),409))
