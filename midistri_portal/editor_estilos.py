"""Structured styles only: never accept raw HTML, CSS declarations or script URLs."""
import re
from django.core.exceptions import ValidationError
DEFAULT={'alto_pc':240,'alto_movil':160,'tamano':28,'fuente':'sistema','color':'#173e31','fondo':'#ffffff','boton_color':'#236447','boton_texto':'#ffffff','alineacion':'izquierda','zona':'centro','movil':'integrado','espacio':16,'radio':12,'transicion':'fundido','composicion':'columnas'}
LIMITS={'alto_pc':(120,480),'alto_movil':(100,280),'tamano':(14,56),'espacio':(0,40),'radio':(0,32)}
CHOICES={'fuente':('sistema','arial','georgia','verdana','monospace'),'alineacion':('izquierda','centro','derecha'),'zona':('centro','izquierda','derecha'),'movil':('integrado','oculto'),'transicion':('fundido','deslizamiento'),'composicion':('columnas','libre')}
FONTS={'sistema':'system-ui,sans-serif','arial':'Arial,sans-serif','georgia':'Georgia,serif','verdana':'Verdana,sans-serif','monospace':'monospace'}

def validar_estilo(data):
    if not isinstance(data,dict) or set(data)-set(DEFAULT)-{'capas'}:raise ValidationError('Estilo inválido.')
    out=dict(DEFAULT,**data)
    for k,(lo,hi) in LIMITS.items():
        if type(out[k]) is not int or not lo<=out[k]<=hi:raise ValidationError('Dimensión fuera de límite: '+k)
    for k,choices in CHOICES.items():
        if out[k] not in choices:raise ValidationError('Opción de estilo inválida: '+k)
    for k in ('color','fondo','boton_color','boton_texto'):
        if not isinstance(out[k],str) or not re.fullmatch(r'#[0-9a-fA-F]{6}',out[k]):raise ValidationError('Color inválido.')
    layers=data.get('capas',{})
    if not isinstance(layers,dict) or set(layers)-{'titulo','texto','boton','imagen'}:raise ValidationError('Capas inválidas.')
    out['capas']={}
    defaults={'titulo':(55,8,42),'texto':(55,32,42),'boton':(55,74,42),'imagen':(0,0,52)}
    for name,initial in defaults.items():
        v=layers.get(name,dict(zip(('x','y','ancho'),initial)))
        if not isinstance(v,dict) or set(v)!={'x','y','ancho'}:raise ValidationError('Posición inválida.')
        if any(type(n) is not int or not 0<=n<=100 for n in v.values()) or not 10<=v['ancho']<=100 or v['x']+v['ancho']>100 or v['y']>85:raise ValidationError('La capa sale del banner.')
        out['capas'][name]=dict(v)
    return out

def estilo_css(data):
    d=validar_estilo(data)
    css=['--alto-pc:%spx'%d['alto_pc'],'--alto-movil:%spx'%d['alto_movil'],'--promo-tamano:%spx'%d['tamano'],'--promo-fuente:'+FONTS[d['fuente']],'--promo-color:'+d['color'],'--promo-fondo:'+d['fondo'],'--promo-boton:'+d['boton_color'],'--promo-boton-texto:'+d['boton_texto'],'--promo-espacio:%spx'%d['espacio'],'--promo-radio:%spx'%d['radio'],'--promo-alinear:'+{'izquierda':'left','centro':'center','derecha':'right'}[d['alineacion']]]
    for name,values in d['capas'].items():
        css += ['--%s-%s:%s%%'%(name,k,v) for k,v in values.items()]
    return ';'.join(css)
