"""Consulta privada de la cuenta del kiosco autenticado."""
from datetime import date
from decimal import Decimal, InvalidOperation
import re

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET

from .client import ApiError, api
from .pagina_views import privada
from .remitos_views import REFERENCIA, TIPOS
from .views import base, identificar


def _importe(valor):
    importe = Decimal(str(valor))
    if not importe.is_finite():
        raise ValueError
    return '$ ' + f'{importe:,.2f}'.translate(str.maketrans(',.', '.,'))


@require_GET
def estado_cuenta(request):
    contexto = None
    try:
        perfil = identificar(request)
        if not perfil:
            return privada(redirect('midistri_catalogo'))
        if perfil.get('cuenta_disponible') is not True:
            return privada(HttpResponse('Estado de cuenta no disponible.', status=404, content_type='text/plain'))
        pagina = request.GET.get('pagina', '1')
        if not re.fullmatch('[1-9][0-9]{0,8}', pagina):
            return privada(HttpResponse('Página inválida.', status=400, content_type='text/plain'))
        contexto = dict(base(request, perfil), en_cuenta=True)
        datos = api('seller-account', params={'pagina': pagina}, token=request.session['midistri_token'])
        if (datos['vendedor_id'], datos['distribuidora_id']) != (perfil['id'], perfil['distribuidora_id']):
            raise ValueError
        saldos = {k: _importe(datos[k]) for k in ('consignado', 'vencido', 'total', 'anterior_c', 'anterior_v')}
        movimientos = []
        for f in datos['movimientos']:
            remitos = [(d['id'], TIPOS[d['tipo']]) for d in f['remitos']
                       if REFERENCIA.fullmatch(d['id']) and d['tipo'] in TIPOS]
            movimientos.append(dict(
                fecha=date.fromisoformat(f['fecha']), concepto=f['concepto'], referencia=f['referencia'],
                consignado=_importe(f['consignado']), vencido=_importe(f['vencido']),
                saldo_consignado=_importe(f['saldo_consignado']), saldo_vencido=_importe(f['saldo_vencido']),
                remitos=remitos,
            ))
        contexto.update(saldos, movimientos=movimientos, pagina=datos['pagina'],
                        anterior=datos['anterior'], siguiente=datos['siguiente'],
                        aviso=datos['aviso_traslado'], requiere_revision=datos['requiere_revision'])
    except ApiError as exc:
        if exc.status in (401, 403, 404):
            return privada(HttpResponse('Estado de cuenta no disponible.', status=404, content_type='text/plain'))
        contexto = contexto or base(request)
        contexto['error'] = ('Tu cuenta tiene movimientos que la distribuidora debe revisar.'
                            if exc.status == 409 else 'No pudimos consultar tu cuenta. Volvé a intentarlo.')
        return privada(render(request, 'midistri_portal/estado_cuenta.html', contexto,
                             status=409 if exc.status == 409 else 503))
    except (ValueError, KeyError, InvalidOperation, TypeError):
        contexto = contexto or base(request)
        contexto['error'] = 'No pudimos consultar tu cuenta. Volvé a intentarlo.'
        return privada(render(request, 'midistri_portal/estado_cuenta.html', contexto, status=503))
    return privada(render(request, 'midistri_portal/estado_cuenta.html', contexto))
