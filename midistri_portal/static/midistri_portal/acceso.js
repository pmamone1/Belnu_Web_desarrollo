(function(){
'use strict';
let busy=false,lastAutomatic='';
const message=()=>document.getElementById('acceso-mensaje');
const codeInput=()=>document.querySelector('[name=codigo]');
function resetCode(){codeInput().value='';lastAutomatic='';}
function autoVerify(input){
    const form=input.closest('[data-codigo="verificar"]');
    if(!form||form.hidden||busy||! /^[0-9]{6}$/.test(input.value)||input.value===lastAutomatic)return;
    lastAutomatic=input.value;
    form.requestSubmit();
}
function pasteCode(text){
    const input=codeInput(),value=text.replace(/\s/g,'');
    if(busy||! /^[0-9]{6}$/.test(value))return false;
    input.value=value;input.focus();autoVerify(input);return true;
}
document.addEventListener('input',e=>{if(e.target.name==='codigo')autoVerify(e.target);});
document.addEventListener('paste',e=>{
    if(e.target.name!=='codigo'||!e.clipboardData)return;
    const text=e.clipboardData.getData('text');
    // Do not extract a code from arbitrary clipboard text.
    e.preventDefault();
    if(!pasteCode(text))message().textContent='Pegá solamente los seis números del código.';
});
document.addEventListener('submit',async e=>{
    const f=e.target;if(!f.dataset.codigo)return;e.preventDefault();if(busy)return;
    if(f.dataset.codigo==='verificar'&&! /^[0-9]{6}$/.test(codeInput().value))return;
    busy=true;
    if(f.dataset.codigo==='verificar')lastAutomatic=codeInput().value;
    const buttons=f.querySelectorAll('button');buttons.forEach(b=>{b.disabled=true;});
    message().textContent='Comprobando…';
    try{
        if(!window.MidistriTab||!MidistriTab.proof(true))throw Error('Habilitá el almacenamiento de esta pestaña para ingresar.');
        const r=await MidistriTab.request(f.action,{method:'POST',body:new FormData(f)});
        const data=await r.json();if(!r.ok)throw Error(data.error||'No pudimos completar el ingreso.');
        if(data.fase==='dentro'){location.assign(data.url);return;}
        document.getElementById('acceso-opciones').hidden=false;
        message().textContent=data.mensaje||'Elegí con qué perfil querés entrar.';
        if(data.fase==='codigo')resetCode();
        document.querySelectorAll('[data-codigo]').forEach(x=>{x.hidden=x.dataset.codigo!==(data.fase==='codigo'?'verificar':'seleccionar');});
        if(data.fase==='elegir'){
            const select=document.querySelector('[name=seleccion]');select.replaceChildren();
            data.identidades.forEach(x=>{
                const o=document.createElement('option');o.value=x.seleccion;
                o.textContent=(x.tipo==='administracion'?'Administración · ':'Vendedor · ')+x.nombre+' · '+x.distribuidora;select.append(o);
            });
        }
        const focus=document.querySelector('form:not([hidden]) input:not([type=hidden]),form:not([hidden]) select');if(focus)focus.focus();
    }catch(err){message().textContent=err.message;}
    finally{busy=false;buttons.forEach(b=>{b.disabled=false;});}
});
document.addEventListener('click',async e=>{
    if(busy)return;
    if(e.target.closest('[data-acceso-pegar]')){
        try{
            if(!navigator.clipboard||!navigator.clipboard.readText)throw Error();
            const text=await navigator.clipboard.readText();
            if(!pasteCode(text))message().textContent='Copiá solamente los seis números del código y volvé a pegar.';
        }catch(_){message().textContent='Pegá el código en el campo con Ctrl+V o la opción Pegar de tu teléfono.';codeInput().focus();}
    }
    if(e.target.closest('[data-acceso-cambiar]')){
        resetCode();document.querySelectorAll('[data-codigo]').forEach(f=>{f.hidden=f.dataset.codigo!=='iniciar';});
        document.getElementById('acceso-opciones').hidden=true;document.querySelector('[name=email]').focus();
    }
    if(e.target.closest('[data-acceso-reenviar]')){resetCode();document.querySelector('[data-codigo=iniciar]').requestSubmit();}
});
})();
