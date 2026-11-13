import re


MENSAJES_ANTERIORES = {
    'subtitulo': {
        'Portal para realizar pedidos. La distribuidora confirma disponibilidad.':
            'Hacé pedidos online. Te confirmamos la disponibilidad.',
    },
    'carrito': {
        'Este pedido queda sujeto a disponibilidad y aceptación por parte de la distribuidora.':
            'El pedido queda sujeto a confirmación y disponibilidad.',
    },
    'presentacion_carrito': {
        'Hacé tus pedidos directo a tu distribuidora. La mercadería es consignada y tus pedidos tienen derecho a devolución, salvo casos especiales.':
            'Hacé tus pedidos online, en un solo lugar. La mercadería es consignada y tus pedidos tienen derecho a devolución, salvo casos especiales.',
    },
}


def mensaje_visible(clave, texto):
    return MENSAJES_ANTERIORES.get(clave, {}).get(texto, texto)


def encabezado_visible(texto, distribuidora, nombre_perfil=''):
    # Sólo se adapta el encabezado público; el borrador y el histórico quedan intactos.
    nombres = {n.strip() for n in (distribuidora.nombre, distribuidora.nombre_comercial, nombre_perfil) if n}
    for nombre in sorted(nombres, key=len, reverse=True):
        patron = r'\s*[-–—]\s*'.join(re.escape(p) for p in re.split(r'\s+[-–—]\s+', nombre))
        texto = re.sub(r'(?<!\w)(?:(?:dist\.|distribuidora)\s+)?' + patron + r'(?!\w)', '', texto,
                       flags=re.IGNORECASE)
    codigos = {m.group(1) for nombre in nombres
               for m in [re.match(r'^(\d+)\s*[-–—]', nombre)] if m}
    for codigo in codigos:
        texto = re.sub(r'(?<!\w)(?:dist\.|distribuidora)\s*' + codigo + r'(?!\w)', '', texto,
                       flags=re.IGNORECASE)
    return texto.strip(' ·–—-|:/')
