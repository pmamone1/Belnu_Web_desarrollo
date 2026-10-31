"""Read-only public catalog selection, stable in a navigation session."""
from hashlib import sha256
from random import Random,SystemRandom
from urllib.parse import urlsplit
from .models import Publicacion
from .catalogo_rotacion import sesion_estado,BANNER_KEY


def candidatos(did):
    result={}
    for product in Publicacion.objects.filter(distribuidora_id=did,distribuidora__activa=True,activa=True,precio__gt=0,pvp__gt=0).order_by('pk'):
        photos=[m.get('url') for m in product.multimedia if m.get('tipo')=='foto']
        photos += [m.get('url') if isinstance(m,dict) else m for m in product.imagenes]
        for url in photos:
            if not isinstance(url,str):continue
            parsed=urlsplit(url)
            if parsed.scheme=='https' and parsed.hostname and not parsed.username and not parsed.password:
                result[product.pk]=(product,url);break
    return result


def slides_automaticos(block,did,session=None,preview=False,rng=None,pool=None):
    amount=block.get('cantidad',6)
    if type(amount) is not int or not 1<=amount<=20:return []
    pool=candidatos(did) if pool is None else pool
    key=str(did)+':'+block['id']+':'+str(amount)
    store=sesion_estado(session) if session is not None and not preview else None
    cache=dict(store.get(BANNER_KEY,{}) or {}) if store is not None else {}
    ids=cache.get(key)
    if ids is None:
        chooser=rng or (Random(int(sha256(key.encode()).hexdigest(),16)) if preview else SystemRandom())
        ids=chooser.sample(list(pool),min(amount,len(pool)))
        if store is not None:
            cache[key]=ids
            cache=dict(list(cache.items())[-20:]);store[BANNER_KEY]=cache
    slides=[]
    for pk in ids:
        if pk not in pool:continue
        product,url=pool[pk]
        slides.append({'publicacion':pk,'producto_id':product.producto_id,'producto':product,'tipo':'foto','url':url,
            'titulo':product.nombre,'texto':'','enlace':'','boton':''})
    return slides
