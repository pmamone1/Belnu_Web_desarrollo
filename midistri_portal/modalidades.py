"""Optional commercial terms received from Urban; never infer them from a remito."""
from datetime import date, datetime

from .client import ApiError


def modalidades_validas(rows, pedidos):
    try:
        if not isinstance(rows, list): raise ValueError
        if not rows: return []
        if not isinstance(pedidos, list) or any(type(pk) is not int or pk < 1 for pk in pedidos): raise ValueError
        allowed = set(pedidos); seen = set(); clean = []
        fields = {'pedido_id', 'modalidad', 'plazo_dias', 'fecha_confirmacion',
                  'vencimientos', 'devoluciones_permitidas'}
        for row in rows:
            if not isinstance(row, dict) or set(row) != fields: raise ValueError
            pk = row['pedido_id']; mode = row['modalidad']; days = row['plazo_dias']
            if type(pk) is not int or pk not in allowed or pk in seen: raise ValueError
            seen.add(pk)
            if mode not in ('firme', 'consignado') or type(days) is not int: raise ValueError
            if days not in ((0,) if mode == 'firme' else (7, 14, 21, 30)): raise ValueError
            returns = row['devoluciones_permitidas']
            if type(returns) is not bool or returns != (mode == 'consignado'): raise ValueError
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
                          'devoluciones_permitidas': returns})
        return clean
    except (KeyError, TypeError, ValueError, OverflowError):
        raise ApiError('Modalidad del pedido inválida. Conservamos la última información guardada.') from None


def modalidades_presentacion(data):
    return [{'modalidad': row['modalidad'], 'plazo_dias': row['plazo_dias'],
             'vencimientos': [date.fromisoformat(entry['fecha_devolucion']) for entry in row['vencimientos']]}
            for row in data.get('modalidades_pedidos', [])]
