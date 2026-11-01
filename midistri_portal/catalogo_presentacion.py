"""Presentation-only catalogue controls, shared by public and private preview."""
from urllib.parse import urlencode
OPCIONES=(24,48,96,192)

def tamano_pagina(value):
    return int(value) if str(value) in {str(n) for n in OPCIONES} else 48

def navegacion(context):
    page=context['productos'];d=context.get('distribuidora')
    filters={k:context.get(k,'') for k in ('q','categoria','subcategoria','orden')}
    filters.update(distribuidora=d.pk if d else '',page_size=context.get('page_size',48))
    def link(number):return '?'+urlencode(dict(filters,page=number))+'#productos'
    context.update(page_sizes=OPCIONES,page_size=filters['page_size'],catalogo_anterior=link(page.previous_page_number()) if page.has_previous() else '',catalogo_siguiente=link(page.next_page_number()) if page.has_next() else '',catalogo_limpiar='?'+urlencode(dict(distribuidora=filters['distribuidora'],q='',categoria='',subcategoria='',orden='recomendados',page_size=filters['page_size']))+'#productos')
    return context

def preview(context,d,page_number=1):
    from django.core.paginator import Paginator
    from .catalogo_elegible import elegibles
    from .models import Publicacion
    from .busqueda import clasificar
    products=list(elegibles(Publicacion.objects.filter(distribuidora=d)).order_by('nombre','pk'))
    classification=[clasificar(p) for p in products]
    page=Paginator(products,48).get_page(page_number)
    for product in page:
        product.categorias_catalogo,product.subcategoria_catalogo=clasificar(product)
        product.galeria=product.multimedia;product.foto_card=next((m['url'] for m in product.galeria if m['tipo']=='foto'),None)
        product.galeria_dom_id='galeria-'+str(product.producto_id);product.galeria_datos={'nombre':product.nombre,'items':product.galeria}
    context.update(distribuidora=d,productos=page,page_size=48,q='',categoria='',subcategoria='',orden='recomendados',ranking_disponible=True,categorias=sorted({c for cats,sub in classification for c in cats},key=str.casefold),subcategorias=sorted({sub for cats,sub in classification if sub},key=str.casefold))
    return navegacion(context)
