"""Contrato público de disponibilidad de una publicación."""
import re

from django.utils.dateparse import parse_datetime

_CAMPOS = {'origen', 'disponible', 'actualizado', 'stock_local_disponible'}
_FECHA = re.compile(
    r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}'
    r'(?::[0-9]{2}(?:[.,][0-9]{1,12})?)?'
    r'(?:Z|[+-](?:[01][0-9]|2[0-3]):?[0-5][0-9])'
)


def fecha_proveedor(value):
    if not isinstance(value, str) or not _FECHA.fullmatch(value):
        raise ValueError('Fecha de proveedor inválida.')
    fecha = parse_datetime(value)
    if fecha is None or fecha.utcoffset() is None:
        raise ValueError('Fecha de proveedor inválida.')
    return fecha


def validar_abastecimiento(value):
    if not isinstance(value, dict):
        raise ValueError('Abastecimiento inválido.')
    if not value:
        return {}
    if set(value) != _CAMPOS or value['origen'] != 'proveedor' or type(value['disponible']) is not bool:
        raise ValueError('Abastecimiento inválido.')
    stock = value['stock_local_disponible']
    if type(stock) is not int or not 0 <= stock <= 10**9:
        raise ValueError('Abastecimiento inválido.')
    if value['actualizado'] is not None:
        fecha_proveedor(value['actualizado'])
    return dict(value)
