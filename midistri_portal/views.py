from decimal import Decimal
from hashlib import sha256
import json
from uuid import uuid4, UUID
from urllib.parse import urlencode
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect,render
from django.views.decorators.http import require_GET,require_POST,require_http_methods
from .client import api,ApiError
from .contract import perfil_valido, pedido_valido
from .models import Distribuidora,Publicacion,PedidoLocal,Sincronizacion
from .services import sincronizar


def identificar(request):
    token=request.session.get('midistri_token')
    if not token:return None
    try:
        perfil=perfil_valido(api('profile',token=token))
        if not all(k in perfil for k in ('id','nombre','linea','distribuidora_id','distribuidora')):raise ApiError('Respuesta inválida.')
        request.midistri_perfil=perfil
        return perfil
    except ApiError as e:
        if e.status in (401,403):
            for key in ('midistri_token','midistri_cart','midistri_cart_id'):request.session.pop(key,None)
            messages.error(request,'Tu acceso fue desactivado. Entrá nuevamente con tu Email y código.' if getattr(request,'midistri_codigo_enabled',False) else 'Tu acceso venció o fue desactivado. Pedí un nuevo enlace a tu distribuidora.')
            return None
        raise


def base(request,perfil=None,distribuidora=None):
    from .pagina import pagina_publica,MENSAJES
    from .pagina_views import contenido_contexto
    if distribuidora is None and perfil:
        distribuidora=Distribuidora.objects.filter(pk=perfil['distribuidora_id'],activa=True).first()
    saved=request.session.get('midistri_catalogo_filtros',{})
    context={'catalogo_url':'/portal/?'+urlencode(saved),'perfil':perfil,'distribuidora':distribuidora,'titulo':'MiDistri - Pedidos Online'+
        (' - '+perfil['distribuidora'] if perfil else (' - '+(distribuidora.nombre_comercial or distribuidora.nombre) if distribuidora else '')),
        'cart_count':sum(request.session.get('midistri_cart',{}).values()),
        'sync':Sincronizacion.objects.filter(pk=1).first()}
    if distribuidora:context.update(contenido_contexto(pagina_publica(distribuidora),distribuidora))
    return context


def error_page(request,e):
    return render(request,'midistri_portal/error.html',dict(base(request),error=str(e)),status=503)


@require_http_methods(['GET','POST'])
def activar(request,token):
    if request.method=='POST':
        if getattr(request,'midistri_codigo_enabled',False):
            from .sesion_pestana import datos_prueba
            datos_prueba(request)
        try:result=api('activate',method='POST',data={'token':token})
        except ApiError as e:return render(request,'midistri_portal/activar.html',dict(base(request),error=str(e)),status=400 if e.status<500 else 503)
        if getattr(request,'midistri_codigo_enabled',False):
            from .sesion_pestana import crear_sesion_pestana
            ident,proof=datos_prueba(request)
            return JsonResponse(crear_sesion_pestana(request,result['perfil'],result['session_token'],ident,proof))
        operator=None if getattr(request,'midistri_codigo_enabled',False) else request.session.pop('midistri_operador_token',None)
        if operator:
            try:api('operator-logout',method='POST',operator_token=operator)
            except ApiError:pass
        request.session.cycle_key()
        request.session['midistri_token']=result['session_token']
        request.session['midistri_cart']={};request.session.pop('midistri_cart_id',None)
        request.session.set_expiry(90*24*60*60)
        messages.success(request,'Hola, '+result['perfil']['nombre']+'. Ya podés hacer tu pedido.')
        return redirect('midistri_catalogo')
    return render(request,'midistri_portal/activar.html',base(request))


@require_GET
def catalogo(request):
    try:perfil=identificar(request)
    except ApiError as e:return error_page(request,e)
    ds=Distribuidora.objects.filter(activa=True).order_by('nombre')
    selected=perfil['distribuidora_id'] if perfil else request.GET.get('distribuidora')
    d=ds.filter(pk=selected).first() if str(selected or '').isdigit() else None
    products=Publicacion.objects.filter(activa=True,distribuidora=d,distribuidora__activa=True)
    saved=request.session.get('midistri_catalogo_filtros',{})
    if str(saved.get('distribuidora'))!=str(getattr(d,'pk',None)):saved={}
    q=request.GET.get('q',saved.get('q',''))[:100]
    categoria=request.GET.get('categoria',saved.get('categoria',''))[:200]
    categorias=list(products.exclude(categoria='').order_by('categoria').values_list('categoria',flat=True).distinct())
    if categoria=='__sin_categoria__':products=products.filter(categoria='')
    elif categoria:products=products.filter(categoria=categoria)
    request.session['midistri_catalogo_filtros']={'distribuidora':d.pk if d else '', 'q':q,'categoria':categoria}
    if q:products=products.filter(nombre__icontains=q)
    from django.core.paginator import Paginator
    page=Paginator(products,24).get_page(request.GET.get('page'))
    for product in page:
        product.cantidad_carrito=request.session.get('midistri_cart',{}).get(str(product.producto_id),0)
        product.galeria=product.multimedia if getattr(settings,'MIDISTRI_MULTIMEDIA_ENABLED',False) else []
        product.foto_card=next((i['url'] for i in product.galeria if i['tipo']=='foto'),None)
        product.galeria_dom_id='galeria-'+str(product.producto_id)
        product.galeria_datos={'nombre':product.nombre,'items':product.galeria}
    from .presentacion import presentacion_publica,TEMAS
    from .promociones import promociones_publicas
    context=base(request,perfil,d);context.update(distribuidoras=ds,productos=page,q=q,categorias=categorias,categoria=categoria,presentacion=presentacion_publica(d),promociones=promociones_publicas(d),temas=TEMAS)
    from .pagina import pagina_publica,MENSAJES
    from .pagina_views import contenido_contexto
    context.update(contenido_contexto(pagina_publica(d),d) if d else {
        'pagina':{'diseno':'compacto'},'pagina_mensajes':MENSAJES,
        'bloques':[{'tipo':'catalogo','activo':True}]})
    template='midistri_portal/catalogo_inicial.html' if context.get('pagina',{}).get('inicial_anterior') else 'midistri_portal/catalogo.html'
    return render(request,template,context)


def foto_producto(producto):
    if producto is None:return ''
    if getattr(settings,'MIDISTRI_MULTIMEDIA_ENABLED',False):
        foto=next((i['url'] for i in producto.multimedia if i['tipo']=='foto'),None)
        if foto:return foto
    return producto.imagenes[0] if producto.imagenes else ''


def productos_carrito(request,perfil):
    cart=request.session.get('midistri_cart',{})
    products={str(p.producto_id):p for p in Publicacion.objects.filter(activa=True,distribuidora_id=perfil['distribuidora_id'],distribuidora__activa=True,producto_id__in=cart)}
    rows=[]
    for pid,qty in cart.items():
        if pid in products:
            p=products[pid];rows.append({'producto':p,'cantidad':qty,'importe':p.precio*qty,'foto':foto_producto(p)})
    return rows,len(rows)!=len(cart)


@require_POST
def cantidad(request):
    try:perfil=identificar(request)
    except ApiError as e:return error_page(request,e)
    if not perfil:return redirect('midistri_catalogo')
    try:
        pid=int(request.POST['producto']);qty=int(request.POST['cantidad'])
        if not 0<=qty<=9999:raise ValueError
        if qty:
            Publicacion.objects.get(producto_id=pid,distribuidora_id=perfil['distribuidora_id'],activa=True,distribuidora__activa=True)
    except (ValueError,KeyError,Publicacion.DoesNotExist):
        messages.error(request,'Producto o cantidad no válidos.');return redirect('midistri_catalogo')
    cart=request.session.get('midistri_cart',{})
    if qty:cart[str(pid)]=qty
    else:cart.pop(str(pid),None)
    if len(cart)>200:messages.error(request,'Máximo 200 productos por pedido.');return redirect('midistri_carrito')
    request.session['midistri_cart']=cart
    request.session.pop('midistri_revision',None)
    request.session['midistri_cart_id']=str(uuid4())
    messages.success(request,'Pedido actualizado.')
    return redirect('midistri_carrito' if request.POST.get('origen')=='carrito' else 'midistri_catalogo')


def firma_revision(rows,perfil):
    data=[perfil['id'],perfil['distribuidora_id'],sorted((r['producto'].producto_id,r['cantidad'],str(r['producto'].precio),str(r['producto'].pvp)) for r in rows)]
    return sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()


@require_GET
def carrito(request):
    try:perfil=identificar(request)
    except ApiError as e:return error_page(request,e)
    if not perfil:return redirect('midistri_catalogo')
    rows,missing=productos_carrito(request,perfil)
    if missing:messages.warning(request,'Hay productos retirados del catálogo. Revisá el pedido antes de enviarlo.')
    if 'midistri_cart_id' not in request.session:request.session['midistri_cart_id']=str(uuid4())
    revision=firma_revision(rows,perfil)
    request.session['midistri_revision']=revision
    present={str(r['producto'].producto_id) for r in rows}
    retirados=[pid for pid in request.session.get('midistri_cart',{}) if pid not in present]
    ctx=base(request,perfil);ctx.update(rows=rows,missing=missing,retirados=retirados,revision=revision,total=sum((r['importe'] for r in rows),Decimal('0')))
    return render(request,'midistri_portal/carrito.html',ctx)


def transmitir(request,pedido):
    try:
        result=api('orders',method='POST',data=pedido.datos,token=request.session['midistri_token'])
        result=pedido_valido(result,request.midistri_perfil,ident=pedido.pk,anterior=pedido.respuesta)
        pedido.respuesta=result;pedido.estado=result['estado'];pedido.error=''
        from .pagina import pagina_publica,MENSAJES
        titulo=pagina_publica(pedido.distribuidora)['mensajes'].get('recibido') or MENSAJES['recibido']
        messages.success(request,titulo+' · '+pedido.referencia_publica+' — '+result['vendedor'])
    except ApiError as e:
        pedido.error=str(e)[:300]
        pedido.estado='revisar' if e.status==409 else 'pendiente'
        messages.warning(request,pedido.error)
    pedido.save(update_fields=['respuesta','estado','error'])


@require_POST
def enviar(request):
    try:perfil=identificar(request)
    except ApiError as e:return error_page(request,e)
    if not perfil:return redirect('midistri_catalogo')
    ident=request.session.get('midistri_cart_id')
    if not ident:return redirect('midistri_carrito')
    # Reuse an existing attempt even after the first POST already cleared the cart.
    existing=PedidoLocal.objects.filter(pk=ident,vendedor_id=perfil['id'],distribuidora_id=perfil['distribuidora_id']).first()
    if existing:
        if existing.estado=='pendiente':transmitir(request,existing)
        return redirect('midistri_detalle',ident=existing.pk)
    rows,missing=productos_carrito(request,perfil)
    if not rows or missing:
        messages.error(request,'Revisá el carrito antes de enviar.');return redirect('midistri_carrito')
    revision=firma_revision(rows,perfil)
    if revision!=request.session.get('midistri_revision') or revision!=request.POST.get('revision'):
        messages.error(request,'Cambió el precio o el detalle desde tu revisión. Revisá el pedido y confirmá nuevamente.')
        return redirect('midistri_carrito')
    obs=request.POST.get('observaciones','')
    if len(obs)>1000:messages.error(request,'La observación admite hasta 1000 caracteres.');return redirect('midistri_carrito')
    payload={'id':ident,'items':[{'producto_id':r['producto'].producto_id,'cantidad':r['cantidad'],
        'precio':str(r['producto'].precio),'pvp':str(r['producto'].pvp),'nombre':r['producto'].nombre,'codigo':r['producto'].codigo} for r in rows],'observaciones':obs}
    pedido,created=PedidoLocal.objects.get_or_create(pk=ident,defaults={'vendedor_id':perfil['id'],
        'distribuidora_id':perfil['distribuidora_id'],'datos':payload})
    if pedido.vendedor_id!=perfil['id'] or pedido.distribuidora_id!=perfil['distribuidora_id']:raise Http404
    transmitir(request,pedido)
    request.session['midistri_cart']={}
    # Keep the id until the next edit to make double submission idempotent.
    return redirect('midistri_detalle',ident=pedido.pk)


def propio(perfil,ident):
    row=PedidoLocal.objects.filter(pk=ident,vendedor_id=perfil['id'],distribuidora_id=perfil['distribuidora_id']).first()
    if row is None:raise Http404
    return row


@require_GET
def pedidos(request):
    try:
        perfil=identificar(request)
        if not perfil:return redirect('midistri_catalogo')
        data=api('orders',token=request.session['midistri_token'])
        if not isinstance(data.get('pedidos'),list) or len(data['pedidos'])>100:raise ApiError('Respuesta de pedidos inválida.')
        validos=[pedido_valido(row,perfil,anterior=(PedidoLocal.objects.filter(pk=row.get('id'),vendedor_id=perfil['id'],distribuidora_id=perfil['distribuidora_id']).values_list('respuesta',flat=True).first() or {})) for row in data['pedidos']]
        for row in validos:
            defaults={'respuesta':row,'estado':row['estado'],'error':''}
            old=PedidoLocal.objects.filter(pk=row['id']).first()
            if old and (old.vendedor_id!=perfil['id'] or old.distribuidora_id!=perfil['distribuidora_id']):raise ApiError('Pedido fuera de alcance.',403)
            PedidoLocal.objects.update_or_create(pk=row['id'],defaults=dict(defaults,vendedor_id=perfil['id'],distribuidora_id=perfil['distribuidora_id']))
    except ApiError as e:
        if not locals().get('perfil'):return error_page(request,e)
        messages.warning(request,'No pudimos actualizar los estados. Mostramos la última información guardada.')
    ctx=base(request,perfil);ctx['pedidos']=PedidoLocal.objects.filter(vendedor_id=perfil['id'],distribuidora_id=perfil['distribuidora_id']).order_by('-creado')[:100]
    return render(request,'midistri_portal/pedidos.html',ctx)


@require_GET
def detalle(request,ident):
    try:perfil=identificar(request)
    except ApiError as e:return error_page(request,e)
    if not perfil:return redirect('midistri_catalogo')
    pedido=propio(perfil,ident)
    stale=False
    if pedido.estado not in ('pendiente','revisar'):
        try:
            try:data=api('order/'+str(ident),token=request.session['midistri_token'])
            except ApiError as e:
                if e.status not in (404,405):raise
                listing=api('orders',token=request.session['midistri_token'])
                data=next((x for x in listing.get('pedidos',[]) if x.get('id')==str(ident)),None)
                if data is None:raise ApiError('El pedido no está disponible para actualizar.',404)
            result=pedido_valido(data,perfil,ident,anterior=pedido.respuesta)
            from django.utils import timezone
            result['_consultado_en']=timezone.now().isoformat()
            pedido.respuesta=result;pedido.estado=result['estado'];pedido.error=''
            pedido.save(update_fields=['respuesta','estado','error'])
        except ApiError:
            stale=True
    items=pedido.respuesta.get('items',pedido.datos.get('items',[]))
    attention=pedido.respuesta.get('atencion')
    shown=[];byid={i['producto_id']:i for i in attention['items']} if attention else {}
    # Photos are display-only catalog data; quantities and prices keep their order snapshot.
    photos={p.producto_id:foto_producto(p) for p in Publicacion.objects.filter(
        distribuidora_id=perfil['distribuidora_id'],producto_id__in=[i['producto_id'] for i in items])}
    for item in items:
        row=dict(item,**{k:v for k,v in byid.get(item['producto_id'],{}).items() if k!='producto_id'})
        row['foto']=photos.get(item['producto_id'],'')
        shown.append(row)
    total=Decimal(attention['total_preparado']) if attention and attention['estado']!='pendiente' else sum((Decimal(i['precio'])*i['cantidad'] for i in items),Decimal('0'))
    ctx=base(request,perfil);ctx.update(pedido=pedido,items=shown,total=total,atencion=attention,stale=stale,consultado_en=pedido.respuesta.get('_consultado_en'))
    return render(request,'midistri_portal/detalle.html',ctx)


@require_POST
def repetir(request,ident):
    try:perfil=identificar(request)
    except ApiError as e:return error_page(request,e)
    if not perfil:return redirect('midistri_catalogo')
    pedido=propio(perfil,ident)
    if pedido.estado=='pendiente':
        messages.warning(request,'Primero reintentá el envío para confirmar si la distribuidora ya lo recibió.')
        return redirect('midistri_detalle',ident=pedido.pk)
    items=pedido.respuesta.get('items',pedido.datos.get('items',[]))
    available=set(Publicacion.objects.filter(distribuidora_id=perfil['distribuidora_id'],activa=True,distribuidora__activa=True).values_list('producto_id',flat=True))
    request.session['midistri_cart']={str(i['producto_id']):i['cantidad'] for i in items if i['producto_id'] in available}
    request.session['midistri_cart_id']=str(uuid4())
    messages.info(request,'Revisá cantidades y precios actuales. Los productos retirados ya no se incluyen. Todavía no enviamos el nuevo pedido.')
    return redirect('midistri_carrito')


@require_POST
def reintentar(request,ident):
    try:perfil=identificar(request)
    except ApiError as e:return error_page(request,e)
    if not perfil:return redirect('midistri_catalogo')
    pedido=propio(perfil,ident)
    if pedido.estado=='pendiente' and pedido.datos:transmitir(request,pedido)
    return redirect('midistri_detalle',ident=pedido.pk)


@require_GET
def documento(request,ident):
    try:
        perfil=identificar(request)
        if not perfil:return redirect('midistri_catalogo')
        propio(perfil,ident)
        content=api('document/'+str(ident),token=request.session['midistri_token'],binary=True)
    except ApiError as e:return error_page(request,e)
    response=HttpResponse(content,content_type='application/pdf');response['Content-Disposition']='attachment; filename="remitos_pedido.pdf"';return response


@require_POST
def salir(request):
    token=request.session.get('midistri_token')
    if token:
        try:api('logout',method='POST',token=token)
        except ApiError:pass
    if getattr(request,'midistri_tab',None):
        from .sesion_pestana import cerrar_sesion_pestana
        cerrar_sesion_pestana(request)
        if 'application/json' in request.headers.get('Accept',''):return JsonResponse({'ok':True,'url':'/portal/'})
    else:request.session.flush()
    return redirect('midistri_catalogo')


@require_http_methods(['GET','POST'])
def gestion(request):
    if not request.user.is_authenticated or not request.user.is_active or not request.user.is_staff:
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.get_full_path(),login_url='/accounts/login/')
    if request.method=='POST':
        try:
            count=sincronizar();messages.success(request,'Catálogo actualizado: '+str(count)+' publicaciones.')
        except (ApiError,ValueError) as e:messages.error(request,str(e))
        return redirect('midistri_portal_gestion')
    return render(request,'midistri_portal/gestion.html',base(request))
