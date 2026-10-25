"""Shipped brand choices; no operator-provided SVG or arbitrary icon path."""
from django.templatetags.static import static
MARCAS=(('bolsa','Bolsa de compras'),('carrito','Carrito online'),('tienda','Tu tienda'),('paquete','Pedido listo'),('ofertas','Ofertas'),('kiosco','Kiosco digital'),('camion','Camión de distribución'),('furgon','Furgón de reparto'),('logistica','Ruta logística'))
def url_marca(key):
    return static('midistri_portal/marcas/'+(key if key in dict(MARCAS) else 'bolsa')+'.svg')
def opciones():
    return [dict(id=k,nombre=n,url=url_marca(k)) for k,n in MARCAS]
