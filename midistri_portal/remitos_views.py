from datetime import date
import re

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET

from .client import ApiError, api
from .pagina_views import privada
from .views import base, identificar

TIPOS = {
    'carga': 'Carga de consignaciones',
    'preparar_devolucion': 'Preparación de devolución',
    'devolucion': 'Devolución',
    'venta': 'Venta',
    'pedido': 'Pedido',
}
REFERENCIA = re.compile(r'(?:salida|carga-lote|pedido)-[1-9][0-9]{0,18}\Z')


def validar_fecha(valor):
    if valor and (not re.fullmatch('[0-9]{4}-[0-9]{2}-[0-9]{2}', valor)
                  or date.fromisoformat(valor).isoformat() != valor):
        raise ValueError
    return valor


@require_GET
def lista(request):
    try:
        perfil = identificar(request)
    except ApiError:
        return privada(render(request, 'midistri_portal/mis_remitos.html',
            dict(base(request), tipos=TIPOS.items(), error='No pudimos comprobar tu acceso. Volvé a intentarlo.'), status=503))
    if not perfil:
        return redirect('midistri_catalogo')

    filtros = {k: request.GET.get(k, '')[:32] for k in ('tipo', 'desde', 'hasta')}
    contexto = dict(base(request, perfil), filtros=filtros, tipos=TIPOS.items(), en_remitos=True)
    try:
        desde, hasta = validar_fecha(filtros['desde']), validar_fecha(filtros['hasta'])
        if desde and hasta and desde > hasta:
            raise ValueError
        if filtros['tipo'] and filtros['tipo'] not in TIPOS:
            raise ValueError
        pagina = request.GET.get('pagina', '1')
        if not re.fullmatch('[1-9][0-9]{0,8}', pagina):
            raise ValueError
        respuesta = api('seller-remittances', params=dict(filtros, pagina=pagina),
                        token=request.session['midistri_token'])
        filas = []
        for fila in respuesta['remitos']:
            if fila['tipo'] not in TIPOS or not REFERENCIA.fullmatch(fila['id']):
                raise ValueError
            filas.append(dict(fila, fecha=date.fromisoformat(fila['fecha']), tipo_label=TIPOS[fila['tipo']]))
        contexto.update(remitos=filas, pagina=respuesta['pagina'],
                        anterior=respuesta['anterior'], siguiente=respuesta['siguiente'])
    except ApiError as exc:
        contexto['error'] = ('Actualizá el acceso a MiDistri para consultar tus remitos.' if exc.status in (401, 403)
                             else 'No pudimos consultar tus remitos. Volvé a intentarlo.')
    except (TypeError, KeyError, ValueError):
        contexto['error'] = 'Revisá el tipo y el rango de fechas para volver a buscar.'
    return privada(render(request, 'midistri_portal/mis_remitos.html', contexto))


@require_GET
def archivo(request, referencia):
    if not REFERENCIA.fullmatch(referencia):
        return privada(HttpResponse('Remito no disponible.', status=404, content_type='text/plain'))
    token = request.session.get('midistri_token')
    if not token:
        return privada(HttpResponse('Ingresá con el perfil de tu kiosco.', status=403, content_type='text/plain'))
    try:
        contenido = api('seller-remittance/' + referencia, token=token, binary=True)
    except ApiError as exc:
        estado = exc.status if exc.status in (403, 404, 409) else 503
        return privada(HttpResponse('Este remito no está disponible. Volvé a Mis remitos.',
                                    status=estado, content_type='text/plain'))
    respuesta = HttpResponse(contenido, content_type='application/pdf')
    disposicion = 'attachment' if request.GET.get('descargar') == '1' else 'inline'
    respuesta['Content-Disposition'] = '{}; filename="remito-{}.pdf"'.format(disposicion, referencia)
    respuesta['X-Content-Type-Options'] = 'nosniff'
    return privada(respuesta)
