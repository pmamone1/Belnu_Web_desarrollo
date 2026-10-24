"""The same offer rule is used by catalogue, cart and promotions."""
def disponible(p):
    return bool(p.activa and p.precio>0 and p.pvp>0 and (p.imagenes or any(m.get('tipo')=='foto' and m.get('url') for m in p.multimedia)))

def elegibles(qs):
    from django.db.models import Q
    # Positive prices are SQL filtered; JSON availability stays portable across MariaDB/SQLite.
    candidates=qs.filter(activa=True,precio__gt=0,pvp__gt=0,distribuidora__activa=True)
    ids=[p.pk for p in candidates if disponible(p)]
    return candidates.filter(pk__in=ids)
