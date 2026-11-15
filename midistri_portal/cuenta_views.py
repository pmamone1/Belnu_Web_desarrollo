"""Consulta privada de la cuenta del kiosco autenticado."""
from datetime import date
from decimal import Decimal, InvalidOperation
import re
from urllib.parse import urlencode

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET

from .client import ApiError, api
from .pagina_views import privada
from .remitos_views import REFERENCIA, TIPOS, validar_fecha
from .views import base, identificar

MIME_EXCEL = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


def _importe(valor):
    importe = Decimal(str(valor))
    if not importe.is_finite():
        raise ValueError
    return '$ ' + f'{importe:,.2f}'.translate(str.maketrans(',.', '.,'))


def _pagina(request, perfil, filtros, *, status=200, **datos):
    contexto = dict(base(request, perfil), en_cuenta=True, filtros=filtros, **datos)
    return privada(render(request, 'midistri_portal/estado_cuenta.html', contexto, status=status))


def _descarga(params, token, formato):
    if formato == 'excel':
        mime, extension, opciones = MIME_EXCEL, 'xlsx', {'binary_mime': MIME_EXCEL}
    else:
        mime, extension, opciones = 'application/pdf', 'pdf', {'binary': True}
    contenido = api('seller-account', params=dict(params, formato=formato), token=token, **opciones)
    respuesta = HttpResponse(contenido, content_type=mime)
    respuesta['Content-Disposition'] = f'attachment; filename="estado-cuenta.{extension}"'
    respuesta['X-Content-Type-Options'] = 'nosniff'
    return privada(respuesta)


@require_GET
def estado_cuenta(request):
    perfil = None
    filtros = {}
    try:
        perfil = identificar(request)
        if not perfil:
            return privada(redirect('midistri_catalogo'))
        if perfil.get('cuenta_disponible') is not True:
            return privada(HttpResponse('Estado de cuenta no disponible.', status=404, content_type='text/plain'))
        filtros = {clave: request.GET.get(clave, '') for clave in ('desde', 'hasta')}
        try:
            desde, hasta = validar_fecha(filtros['desde']), validar_fecha(filtros['hasta'])
            if desde and hasta and desde > hasta:
                raise ValueError
        except ValueError:
            return _pagina(request, perfil, filtros, status=400, error='Revisá el rango de fechas para volver a buscar.')
        params = {clave: valor for clave, valor in filtros.items() if valor}
        token = request.session['midistri_token']
        formato = request.GET.get('formato', '')
        if formato:
            if formato not in ('excel', 'pdf'):
                return _pagina(request, perfil, filtros, status=400, error='Formato de descarga inválido.')
            return _descarga(params, token, formato)
        pagina = request.GET.get('pagina', '1')
        if not re.fullmatch('[1-9][0-9]{0,8}', pagina):
            return privada(HttpResponse('Página inválida.', status=400, content_type='text/plain'))
        datos = api('seller-account', params=dict(params, pagina=pagina), token=token)
        if (datos['vendedor_id'], datos['distribuidora_id']) != (perfil['id'], perfil['distribuidora_id']):
            raise ValueError
        saldos = {k: _importe(datos[k]) for k in ('consignado', 'vencido', 'total', 'anterior_c', 'anterior_v')}
        saldos['anterior_total'] = _importe(Decimal(str(datos['anterior_c'])) + Decimal(str(datos['anterior_v'])))
        movimientos = []
        for f in datos['movimientos']:
            remitos = [(d['id'], TIPOS[d['tipo']] + (' · ' + d['referencia'] if d.get('referencia') else '')) for d in f['remitos']
                       if REFERENCIA.fullmatch(d['id']) and d['tipo'] in TIPOS]
            movimientos.append(dict(
                fecha=date.fromisoformat(f['fecha']), concepto=f['concepto'], referencia=f['referencia'],
                consignado=_importe(f['consignado']), vencido=_importe(f['vencido']),
                saldo_consignado=_importe(f['saldo_consignado']), saldo_vencido=_importe(f['saldo_vencido']),
                saldo_total=_importe(Decimal(str(f['saldo_consignado'])) + Decimal(str(f['saldo_vencido']))),
                remitos=remitos,
            ))
        contexto = dict(saldos, movimientos=movimientos, pagina=datos['pagina'],
                        anterior=datos['anterior'], siguiente=datos['siguiente'],
                        requiere_revision=datos['requiere_revision'], query_fechas=urlencode(params))
    except ApiError as exc:
        if exc.status in (401, 403, 404):
            return privada(HttpResponse('Estado de cuenta no disponible.', status=404, content_type='text/plain'))
        mensajes = {400: 'Revisá el rango de fechas para volver a buscar.',
                    409: 'Tu cuenta tiene movimientos que la distribuidora debe revisar.'}
        return _pagina(request, perfil, filtros, status=exc.status if exc.status in mensajes else 503,
                       error=mensajes.get(exc.status, 'No pudimos consultar tu cuenta. Volvé a intentarlo.'))
    except (ValueError, KeyError, InvalidOperation, TypeError):
        return _pagina(request, perfil, filtros, status=503, error='No pudimos consultar tu cuenta. Volvé a intentarlo.')
    return _pagina(request, perfil, filtros, **contexto)
