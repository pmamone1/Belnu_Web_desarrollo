"""Optional per-message styles. No user supplied CSS or HTML is accepted."""
import re
from django.core.exceptions import ValidationError
from .editor_estilos import FONTS
CLAVES=('encabezado','nav_catalogo','titulo','subtitulo','bienvenida','instrucciones','carrito','recibido','contacto','boton_pedido')

def validar_mensajes(data):
    if not isinstance(data,dict) or set(data)-set(CLAVES):raise ValidationError('Estilos de mensajes inválidos.')
    out={}
    for key,style in data.items():
        if not isinstance(style,dict) or set(style)-{'tamano','fuente','color','fondo'}:raise ValidationError('Estilo de mensaje inválido: '+key)
        clean={}
        for name,value in style.items():
            if name=='tamano':
                if type(value) is not int or not 14<=value<=56:raise ValidationError('Tamaño de mensaje fuera de límite.')
            elif name=='fuente':
                if not isinstance(value,str) or value not in FONTS:raise ValidationError('Fuente de mensaje inválida.')
            elif not isinstance(value,str) or not re.fullmatch(r'#[0-9a-fA-F]{6}',value):raise ValidationError('Color de mensaje inválido.')
            clean[name]=value
        if clean:out[key]=clean
    return out

def css_mensaje(data,key):
    style=validar_mensajes(data).get(key,{})
    names={'tamano':'font-size','fuente':'font-family','color':'color','fondo':'background-color'}
    return ';'.join(names[k]+':'+(str(v)+'px' if k=='tamano' else FONTS[v] if k=='fuente' else v) for k,v in style.items())
