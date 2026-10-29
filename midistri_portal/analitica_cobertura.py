"""Positive identity evidence and explicit gaps; no fabricated historical actions."""
from datetime import datetime
from pathlib import Path
import os
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from .models import EvidenciaAnalitica,IncidenciaAnalitica,SesionVendedorPortal,ControlAnalitica,IntervaloAnalitico,Distribuidora

def marcador():
    return Path(getattr(settings,'BASE_DIR',Path(__file__).resolve().parents[1]))/'tmp'/'midistri_analitica_fallo.json'

def acreditar(vendedor,distribuidora):
    try:
        with transaction.atomic():
            if ControlAnalitica.objects.filter(pk=1).exists():EvidenciaAnalitica.objects.get_or_create(distribuidora_id=distribuidora,vendedor_id=vendedor)
    except Exception:marcar_fallo(distribuidora)

def guardar_previos():
    for d,v in SesionVendedorPortal.objects.values_list('distribuidora_id','vendedor_id').distinct().iterator():
        EvidenciaAnalitica.objects.get_or_create(distribuidora_id=d,vendedor_id=v)

def marcar_fallo(distribuidora):
    now=timezone.now()
    try:
        with transaction.atomic():IncidenciaAnalitica.objects.create(distribuidora_id=distribuidora,desde=now,hasta=now)
    except Exception:
        # If the database itself is unavailable, retain one private, conservative
        # marker until the DB can persist a gap. No identity or credential is stored.
        try:
            path=marcador();path.parent.mkdir(parents=True,exist_ok=True)
            fd=os.open(str(path),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
            with os.fdopen(fd,'w') as stream:stream.write(now.isoformat())
        except (OSError,ValueError):pass

def fallo_pendiente():
    path=marcador()
    if not path.exists():return None
    try:
        value=parse_datetime(path.read_text(encoding='ascii').strip())
        if value is None or timezone.is_naive(value):raise ValueError
        return value
    except (OSError,ValueError):return datetime(2000,1,1,tzinfo=timezone.utc)

def conciliar_fallo():
    start=fallo_pendiente()
    if start is None:return
    now=timezone.now()
    for d in Distribuidora.objects.filter(activa=True).values_list('pk',flat=True):IncidenciaAnalitica.objects.get_or_create(distribuidora_id=d,desde=start,defaults={'hasta':now})
    def limpiar():
        try:marcador().unlink()
        except OSError:pass
    transaction.on_commit(limpiar)

def congelar(ids,corte):
    intervals=list(IntervaloAnalitico.objects.filter(distribuidora_id__in=ids,desde__lte=corte).order_by('desde').values('distribuidora_id','desde','hasta'))
    gaps=list(IncidenciaAnalitica.objects.filter(distribuidora_id__in=ids,desde__lte=corte).values('distribuidora_id','desde','hasta'))
    pending=fallo_pendiente()
    if pending and pending<=corte:gaps.extend(dict(distribuidora_id=d,desde=pending,hasta=corte) for d in ids)
    # Legacy sessions are positive evidence only, never detailed action history.
    evidence=set(EvidenciaAnalitica.objects.filter(distribuidora_id__in=ids,acreditada__lte=corte).values_list('distribuidora_id','vendedor_id'))
    evidence.update(SesionVendedorPortal.objects.filter(distribuidora_id__in=ids,actividad__lte=corte).values_list('distribuidora_id','vendedor_id'))
    for rows in (intervals,gaps):
        for r in rows:
            for field in ('desde','hasta'):r[field]=r[field].isoformat() if r[field] else None
    return dict(intervalos=intervals,incidencias=gaps,evidencia=[list(k) for k in sorted(evidence)])

def cobertura(intervals,gaps,did,start,end):
    if start>=end:return 'sin_medicion'
    pieces=sorted((max(parse_datetime(r['desde']),start),min(parse_datetime(r['hasta']) if r['hasta'] else end,end)) for r in intervals if r['distribuidora_id']==did)
    pieces=[(a,b) for a,b in pieces if a<b]
    if not pieces:return 'sin_medicion'
    cursor=start
    for a,b in pieces:
        if a>cursor:return 'parcial'
        cursor=max(cursor,b)
    if cursor<end:return 'parcial'
    if any(r['distribuidora_id']==did and parse_datetime(r['desde'])<end and parse_datetime(r['hasta'])>=start for r in gaps):return 'parcial'
    return 'completa'
