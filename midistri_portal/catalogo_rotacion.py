"""Stable per-navigation merchandising; stores IDs, never prices or permissions."""
from random import SystemRandom

ORDEN_KEY='midistri_catalogo_orden'
BANNER_KEY='midistri_banners_automaticos'

def sesion_estado(session):
    # Public pages have no authenticated tab row. Keep only public merchandising
    # in the browser session; authenticated pages use their private tab data.
    if hasattr(session,'original') and session.row is None:return session.original
    return session

def posicion_ventas(product):
    values=product.indicadores or {}
    value=values.get('orden_ventas',values.get('ranking'))
    return value if type(value) is int and value>0 else None

def ordenar_mezcla(products,rng=None):
    rng=rng or SystemRandom();products=list(products)
    ranked=sorted((p for p in products if posicion_ventas(p) is not None),key=lambda p:(posicion_ventas(p),p.pk))
    top=ranked[:10];topids={p.pk for p in top};rest=[p for p in products if p.pk not in topids]
    rng.shuffle(top);rng.shuffle(rest);result=[]
    while top or rest:
        if top:result.append(top.pop())
        if rest:result.append(rest.pop())
    return result

def orden_sesion(request,did,products,perfil=None,rng=None):
    session=sesion_estado(request.session)
    key=str(did)+':'+str((perfil or {}).get('id','publico'))
    state=session.get(ORDEN_KEY)
    if not isinstance(state,dict) or state.get('perfil')!=key or state.get('version')!=1:
        state={'version':1,'perfil':key,'ids':[p.pk for p in ordenar_mezcla(products,rng)]}
        session[ORDEN_KEY]=state
    return list(state['ids'])
