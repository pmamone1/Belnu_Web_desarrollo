from decimal import Decimal,InvalidOperation
from django import template
register=template.Library()
@register.filter
def precio_ar(value):
    try:
        number=Decimal(str(value))
        if not number.is_finite():return '—'
        return format(number,',.2f').translate(str.maketrans({',':'.','.':','}))
    except (ValueError,TypeError,InvalidOperation):return '—'

@register.filter
def accion_analitica(value):
    from ..analitica_informes import ETIQUETAS
    return ETIQUETAS.get(value,value)

@register.filter
def fecha_arg(value):
    from django.utils.dateparse import parse_datetime
    from django.utils import timezone
    import pytz
    try:return timezone.localtime(parse_datetime(value),pytz.timezone('America/Argentina/Buenos_Aires')).strftime('%d/%m/%Y %H:%M:%S')
    except (TypeError,ValueError,AttributeError):return 'Fecha no disponible'
