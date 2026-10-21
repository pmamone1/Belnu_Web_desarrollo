from django.conf import settings
from email import message
from django.shortcuts import render, redirect
from django.http import JsonResponse
from carts.models import CartItem
from .forms import OrderForm
from datetime import datetime
from .models import Order, OrderProduct
import json
from store.models import Product, Variation
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from accounts.models import UserProfile
from django.contrib.sites.shortcuts import get_current_site
import smtplib
import ssl
from email.message import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.contrib import messages, auth
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.sites.shortcuts import get_current_site
import urllib 

import environ
env = environ.Env()
environ.Env.read_env()


# Create your views here.

def place_order(request, total=0, quantity=0):
    
    # busca el usuarrio
    current_user = request.user
    # busca los items que eligio el usuario
    cart_items = CartItem.objects.filter(user=current_user)
    #cuenta la cantidad de items del carrito
    cart_count = cart_items.count()

    #si el carro esta vacio se redirige al store
    if cart_count <= 0:
        print("cart_count="+ str(cart_count))
        return redirect('store')

    #inicializa el valor del total a 0
    grand_total = 0
    total=0
    quantity=0
    # saca el total del pedido mas la cantidad de ejemplares
    for cart_item in cart_items:
        quantity += cart_item.quantity
        for item in cart_item.variations.all():
            total += ((item.precio_ed + cart_item.product.recargo_interior) * cart_item.quantity)
        

    # guarda el total del pedido
    grand_total = total
            
    print("entro en el checkout")
    user = request.user
    # busca el profile en la bd
    userProfile = UserProfile.objects.get(user=current_user)
    #asigna el numero de vendedor y nombre
    numero_vendedor = userProfile.numero_vendedor
    nombre_vendedor = userProfile.nombre_vendedor
    
    #yr=int(datetime.date.today().strftime('%Y'))
    #mt=int(datetime.date.today().strftime('%m'))
    #dt=int(datetime.date.today().strftime('%d'))
    
    #d = datetime(yr,mt,dt)
    d=datetime.now()
    current_date = d.strftime("%Y%m%d%H%M%S")
        
    # arma el numero de pedido
    order_number = current_date+"_"+str(numero_vendedor)
    
    if request.method == 'POST':
        print("entro en el post")
        form = OrderForm(request.POST)
        
        # Guarda el pedido en la base de datos
        data = Order()
        data.user = current_user
        data.numero_vendedor = numero_vendedor
        data.nombre_vendedor = nombre_vendedor
        data.order_number = order_number  
        data.first_name = current_user.first_name
        data.last_name = current_user.last_name
        data.phone = current_user.phone_number
        data.email = current_user.email
            
        data.order_total = grand_total
        
        data.ip = request.META.get('REMOTE_ADDR')
        data.save()
        print("guardamos la orden!")

        # Mover todos los carrito items hacia la tabla order product
        order = Order.objects.filter(user=request.user, is_ordered=False, order_number=order_number).first()
        
        cart_items = CartItem.objects.filter(user=request.user)
        total=0
        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order = order
            orderproduct.profile = userProfile            
            orderproduct.user = user
            orderproduct.product = item.product
            orderproduct.quantity = item.quantity
            orderproduct.ordered = True
            orderproduct.numero_pedido = order_number
            for i in item.variations.all():
                total += ((i.precio_ed + cart_item.product.recargo_interior) * item.quantity)
                
            orderproduct.product_price = total
            orderproduct.save()
            
            ############################
            print("el item id="+str(item.id))
            cart_item = CartItem.objects.get(id=item.id)
            product_variation = cart_item.variations.all()
            orderproduct = OrderProduct.objects.get(id=orderproduct.id)
            orderproduct.variation.set(product_variation)
            print(product_variation)
            
            
            
            orderproduct.save()

            # bajar del stock los ejemplares vendidos
            for variation in product_variation:
                variation.stock -= item.quantity
                if variation.stock < 0:
                    messages.warning(request, "No hay suficientes ejemplares para el producto: " + variation.subtitulo)
                    return redirect('cart')
                    
                else:
                    variation.save()   
                print("bajamos del stock el producto")
        grand_total = total
        CartItem.objects.filter(user=request.user).delete()
        data.is_ordered = True
        data.status ="Accepted"
        #urllib.parse.unquote('/El%20Ni%C3%B1o/')
        nombre= urllib.parse.unquote(current_user.first_name + "," + current_user.last_name)
        data.save()
        print("borramos el carrito y se guardo todo!")
        context = {
            'user': user,
            'user_id': str(user.id),
            'user_email': user.email,
            'grand_total': grand_total,
            'numero_vendedor': numero_vendedor,
            'nombre_vendedor': nombre_vendedor,
            'nombre_completo': nombre,
            'numero_pedido': order_number,
            'status': 'Pendiente',
            'fecha': str(data.created_at),
        }
        return redirect('order_complete', user_id=str(user.id),user_email=user.email, user=user, grand_total=grand_total, numero_vendedor=numero_vendedor, nombre_vendedor=nombre_vendedor, nombre_completo=nombre, numero_pedido=order_number, status=data.status, fecha=data.created_at)   
            
       
       
       
    context = {
            'cart_items': cart_items,
            'grand_total': grand_total,
            'numero_vendedor': numero_vendedor,
            'nombre_vendedor': nombre_vendedor,
            'fecha_pedido': datetime.now().strftime("%Y-%m-%d"),
            'order_number': order_number,
            'total_items':quantity,
            'user': current_user,
        }
    return render(request,'store/checkout.html',context)



def order_complete(request,user,user_id,user_email,numero_vendedor,grand_total,nombre_vendedor,nombre_completo,numero_pedido,status,fecha):
    domain = get_current_site(request).domain
    current = 'https://' + str(domain)
    
    #nombre_completo = user.full_name
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST='smtp.belnu.com.ar'
    EMAIL_PORT=465
    EMAIL_USE_TLS=True
    EMAIL_HOST_USER = settings.EMAIL_HOST_USER
    EMAIL_HOST_PASSWORD = settings.EMAIL_HOST_PASSWORD
    try:
        order = Order.objects.get(order_number=numero_pedido, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
    except:
        pass
    #print(ordered_products)
    #print(ordered_products.count())
    
    context = {
            'ordered_products': ordered_products,
            'grand_total': str(grand_total),
            'numero_vendedor': numero_vendedor,
            'nombre_vendedor': nombre_vendedor,
            'numero_pedido': numero_pedido,
            'status': 'Pendiente',
            'domain': current,
            'order_id': order.id,
        }
    current_site = get_current_site(request)
    current = 'https://' + str(current_site)
    # Configuracion de los mails
    email_sender = EMAIL_HOST_USER
    email_password = EMAIL_HOST_PASSWORD
    
    email_receiver = user_email

    # configuramos el mail 
    nombre= urllib.parse.unquote(nombre_completo)
    
    subject = 'Su pedido fue procesado con exito! - Gracias por hacer tus pedidos en Belnu Pedidos Web!'
    body = render_to_string('orders/order_complete_email.html', {
    'user': user,
    'domain': current,
    'nombre_completo': nombre,
    'numero_pedido': numero_pedido,
    'status': 'Pendiente',
    'nombre_vendedor': nombre_vendedor,
    'numero_vendedor': numero_vendedor,
    'grand_total': grand_total,
    'order_id': order.id,
    })

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    # Add SSL (layer of security)
    context_ssl = ssl.create_default_context()

    # Log in and send the email
    with smtplib.SMTP_SSL('belnu.com.ar', 465,context=context_ssl) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
        messages.success(request, 'Tu pedido fue procesado con exito!')        
    return render(request,'orders/order_recieved_email.html',context)

def order_recived_email(request,ordered_products,grand_total,numero_vendedor,nombre_vendedor,numero_pedido,status):
    context = {
            'ordered_products': ordered_products,
            'grand_total': grand_total,
            'numero_vendedor': numero_vendedor,
            'nombre_vendedor': nombre_vendedor,
            'numero_pedido': numero_pedido,
            'status': 'Pendiente',
        }
    return render(request,'orders/order_recived_email.html',context)
