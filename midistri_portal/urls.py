from django.urls import path
from . import views
urlpatterns=[
path('',views.catalogo,name='midistri_catalogo'),
path('activar/<str:token>/',views.activar,name='midistri_activar'),
path('cantidad/',views.cantidad,name='midistri_cantidad'),
path('carrito/',views.carrito,name='midistri_carrito'),
path('enviar/',views.enviar,name='midistri_enviar'),
path('pedidos/',views.pedidos,name='midistri_pedidos'),
path('pedido/<uuid:ident>/',views.detalle,name='midistri_detalle'),
path('pedido/<uuid:ident>/repetir/',views.repetir,name='midistri_repetir'),
path('pedido/<uuid:ident>/reintentar/',views.reintentar,name='midistri_reintentar'),
path('pedido/<uuid:ident>/remito/',views.documento,name='midistri_remito'),
path('salir/',views.salir,name='midistri_salir'),
path('gestion/',views.gestion,name='midistri_portal_gestion'),
]
