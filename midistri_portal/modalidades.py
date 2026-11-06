"""Optional commercial terms received from Urban; never infer them from a remito."""
from datetime import date, datetime

from .client import ApiError


def modalidades_validas(rows, pedidos, productos=None):
    try:
        if not isinstance(rows, list): raise ValueError
        if not rows: return []
        if not isinstance(pedidos, list) or any(type(pk) is not int or pk < 1 for pk in pedidos): raise ValueError
        allowed = set(pedidos); seen = set(); clean = []
        fields = {'pedido_id', 'modalidad', 'plazo_dias', 'fecha_confirmacion',
                  'vencimientos', 'devoluciones_permitidas'}
        for row in rows:
            if not isinstance(row, dict) or set(row) not in (fields, fields | {'gestion', 'fecha_debito', 'devolucion_productos'}): raise ValueError
            propia = 'gestion' in row
            pk = row['pedido_id']; mode = row['modalidad']; days = row['plazo_dias']
            if type(pk) is not int or pk not in allowed or pk in seen: raise ValueError
            seen.add(pk)
            if mode not in ('firme', 'consignado') or type(days) is not int: raise ValueError
            if days not in ((0,) if mode == 'firme' else (7, 14, 21, 30)): raise ValueError
            returns = row['devoluciones_permitidas']
            if type(returns) is not bool: raise ValueError
            if not propia and returns != (mode == 'consignado'): raise ValueError
            extension = validar_propia(row, productos) if propia else {}
            confirmed = row['fecha_confirmacion']
            if not isinstance(confirmed, str) or len(confirmed) > 50 or 'T' not in confirmed: raise ValueError
            # Python 3.7 accepts offsets but not the equivalent ISO UTC suffix Z.
            stamp = datetime.fromisoformat(confirmed[:-1] + '+00:00' if confirmed.endswith('Z') else confirmed)
            if stamp.tzinfo is None or stamp.utcoffset() is None: raise ValueError
            due = row['vencimientos']; clean_due = []; seen_due = set()
            if not isinstance(due, list) or (mode == 'firme' and due): raise ValueError
            for entry in due:
                if not isinstance(entry, dict) or set(entry) != {'salida_id', 'fecha_devolucion'}: raise ValueError
                sid = entry['salida_id']; value = entry['fecha_devolucion']
                if type(sid) is not int or sid < 1 or sid in seen_due: raise ValueError
                seen_due.add(sid)
                if not isinstance(value, str) or len(value) != 10 or date.fromisoformat(value).isoformat() != value: raise ValueError
                # Existing open consignments may have a due date before confirmation.
                clean_due.append({'salida_id': sid, 'fecha_devolucion': value})
            clean.append({'pedido_id': pk, 'modalidad': mode, 'plazo_dias': days,
                          'fecha_confirmacion': confirmed, 'vencimientos': clean_due,
                          'devoluciones_permitidas': returns, **extension})
        return clean
    except (KeyError, TypeError, ValueError, OverflowError):
        raise ApiError('Modalidad del pedido inválida. Conservamos la última información guardada.') from None


def validar_propia(row, productos):
    if row['gestion'] != 'pedido' or row['modalidad'] != 'consignado' or row['vencimientos'] != []: raise ValueError
    debit = row['fecha_debito']
    if not isinstance(debit, str) or len(debit) != 10 or date.fromisoformat(debit).isoformat() != debit: raise ValueError
    rows = row['devolucion_productos']
    if not isinstance(rows, list) or not 1 <= len(rows) <= 200: raise ValueError
    if not isinstance(productos, list): raise ValueError
    allowed = set(productos); seen = set(); clean = []
    for entry in rows:
        if not isinstance(entry, dict) or set(entry) != {'producto_id', 'admite_devolucion'}: raise ValueError
        pid = entry['producto_id']; returns = entry['admite_devolucion']
        if type(pid) is not int or pid < 1 or pid not in allowed or pid in seen or type(returns) is not bool: raise ValueError
        seen.add(pid)
        clean.append({'producto_id': pid, 'admite_devolucion': returns})
    if row['devoluciones_permitidas'] != any(entry['admite_devolucion'] for entry in clean): raise ValueError
    return {'gestion': 'pedido', 'fecha_debito': debit, 'devolucion_productos': clean}


def modalidades_presentacion(data):
    result = []
    for row in data.get('modalidades_pedidos', []):
        item = {'modalidad': row['modalidad'], 'plazo_dias': row['plazo_dias'],
                'vencimientos': [date.fromisoformat(entry['fecha_devolucion']) for entry in row['vencimientos']]}
        if row.get('gestion') == 'pedido':
            item.update(gestion='pedido', fecha_debito=date.fromisoformat(row['fecha_debito']))
        result.append(item)
    return result


def devoluciones_presentacion(data):
    """Only annotate products with explicit own-order metadata; never infer from masters."""
    result = {}
    for row in data.get('modalidades_pedidos', []):
        if row.get('gestion') != 'pedido': continue
        for entry in row['devolucion_productos']:
            result.setdefault(entry['producto_id'], set()).add(entry['admite_devolucion'])
    return {pid: ('Admite devolución' if flags == {True} else
                  'No admite devolución' if flags == {False} else
                  'La devolución depende de cada parte del pedido') for pid, flags in result.items()}
