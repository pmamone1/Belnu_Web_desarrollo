from uuid import uuid4
from django import forms
from django.contrib import messages
from django.shortcuts import render,redirect
from django.views.decorators.http import require_http_methods
from .operadores_views import contexto_panel,fallo
from .client import api,ApiError


class ComercialForm(forms.Form):
    nombre_comercial=forms.CharField(max_length=150,required=False,label='Nombre comercial visible')
    email_respuesta=forms.EmailField(max_length=254,required=False,label='Email de respuesta y consultas')
    asunto_acceso=forms.CharField(max_length=150,required=False,label='Asunto predeterminado de la campaña')
    texto_acceso=forms.CharField(max_length=3000,required=False,label='Mensaje predeterminado',widget=forms.Textarea)
    texto_entrega=forms.CharField(max_length=500,required=False,label='Información opcional de entrega',widget=forms.Textarea)


def validar_config(data,did):
    form=ComercialForm(data)
    if (data.get('version')!=1 or type(data.get('distribuidora_id')) is not int or data['distribuidora_id']!=did
        or type(data.get('revision')) is not int or data['revision']<0 or not form.is_valid()):raise ApiError('Configuración comercial inválida.')
    return dict(form.cleaned_data,revision=data['revision'])


def guardar_configuracion_urban(perfil,token,datos,revision,operacion_id):
    did=datos['distribuidora']
    return validar_config(api('operator-store-settings-save',method='POST',operator_token=token,
        data={'distribuidora':did,'datos':{k:datos.get(k,'') for k in ComercialForm.base_fields},
              'revision':revision,'operacion':operacion_id}),did)


@require_http_methods(['GET','POST'])
def configuracion(request):
    try:
        ctx=contexto_panel(request,'midistri.tienda_configurar');did=ctx['tienda']['id']
        token=request.session['midistri_operador_token'];current={};form=None
        if request.method=='POST':
            form=ComercialForm(request.POST)
            if form.is_valid():
                try:revision=int(request.POST.get('revision',''))
                except ValueError:raise ApiError('Revisión inválida.',400)
                guardar_configuracion_urban(ctx['operador'],token,dict(form.cleaned_data,distribuidora=did),revision,request.POST.get('operacion',''))
                messages.success(request,'Nombre comercial y mensajes guardados en Urban Soft. No se envió ninguna campaña.')
                return redirect('/portal/administrar/comunicacion/?distribuidora='+str(did))
        current=validar_config(api('operator-store-settings',method='POST',operator_token=token,data={'distribuidora':did}),did)
        ctx.update(form=form or ComercialForm(initial=current),revision=current['revision'],operacion=str(uuid4()))
        return render(request,'midistri_portal/operador_comunicacion.html',ctx)
    except ApiError as e:return fallo(request,e)
