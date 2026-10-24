from django import forms
from .pagina import DISENOS,MENSAJES
from .presentacion import TEMAS

class PaginaForm(forms.Form):
    diseno=forms.ChoiceField(choices=DISENOS,label='Diseño de la página')
    tema=forms.ChoiceField(choices=TEMAS,label='Color predeterminado')
    email=forms.EmailField(required=False,label='Email de contacto')
    telefono=forms.CharField(max_length=40,required=False,label='Teléfono')
    titulo=forms.CharField(max_length=1000,required=False,label='Título del catálogo')
    subtitulo=forms.CharField(max_length=1000,required=False,label='Subtítulo')
    bienvenida=forms.CharField(max_length=1000,required=False,widget=forms.Textarea(attrs={'rows':2}))
    instrucciones=forms.CharField(max_length=1000,required=False,widget=forms.Textarea(attrs={'rows':2}))
    carrito=forms.CharField(max_length=1000,required=False,widget=forms.Textarea(attrs={'rows':2}),label='Aviso del carrito')
    recibido=forms.CharField(max_length=1000,required=False,label='Mensaje de pedido recibido')
    contacto=forms.CharField(max_length=1000,required=False,label='Pie de contacto')
    boton_pedido=forms.CharField(max_length=1000,required=False,label='Texto del botón del pedido')
