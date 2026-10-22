from decimal import Decimal
from hashlib import sha256
import json
from uuid import uuid4, UUID
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.http import Http404, HttpResponse
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
            messages.error(request,'Tu acceso venció o fue desactivado. Pedí un nuevo enlace a tu distribuidora.')
            return None
        raise


def base(request,perfil=None,distribuidora=None):
    return {'perfil':perfil,'distribuidora':distribuidora,'titulo':'MiDistri - Pedidos Online'+
        (' - '+perfil['distribuidora'] if perfil else (' - '+distribuidora.nombre if distribuidora else '')),
        'cart_count':sum(request.session.get('midistri_cart',{}).values()),
        'sync':Sincronizacion.objects.filter(pk=1).first()}


def error_page(request,e):
    return render(request,'midistri_portal/error.html',dict(base(request),error=str(e)),status=503)


@require_http_methods(['GET','POST'])
def activar(request,token):
    if request.method=='POST':
        try:result=api('activate',method='POST',data={'token':token})
        except ApiError as e:return render(request,'midistri_portal/activar.html',dict(base(request),error=str(e)),status=400 if e.status<500 else 503)
        operator=request.session.pop('midistri_operador_token',None)
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
    q=request.GET.get('q','')[:100]
    if q:products=products.filter(nombre__icontains=q)
    from django.core.paginator import Paginator
    page=Paginator(products,24).get_page(request.GET.get('page'))
    for product in page:
        product.cantidad_carrito=request.session.get('midistri_cart',{}).get(str(product.producto_id),0)
    context=base(request,perfil,d);context.update(distribuidoras=ds,productos=page,q=q)
    return render(request,'midistri_portal/catalogo.html',context)


def productos_carrito(request,perfil):
    cart=request.session.get('midistri_cart',{})
    products={str(p.producto_id):p for p in Publicacion.objects.filter(activa=True,distribuidora_id=perfil['distribuidora_id'],distribuidora__activa=True,producto_id__in=cart)}
    rows=[]
    for pid,qty in cart.items():
        if pid in products:
            p=products[pid];rows.append({'producto':p,'cantidad':qty,'importe':p.precio*qty})
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
        result=pedido_valido(result,request.midistri_perfil,ident=pedido.pk)
        pedido.respuesta=result;pedido.estado=result['estado'];pedido.error=''
        messages.success(request,'Recibimos tu pedido N.º '+str(pedido.pk)+' — '+result['vendedor'])
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
        validos=[pedido_valido(row,perfil) for row in data['pedidos']]
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
    items=pedido.respuesta.get('items',pedido.datos.get('items',[]))
    ctx=base(request,perfil);ctx.update(pedido=pedido,items=items,total=sum((Decimal(i['precio'])*i['cantidad'] for i in items),Decimal('0')))
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
    request.session.flush()
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
