(function(){'use strict';
if(location.pathname.startsWith('/portal/administrar/')||location.pathname.startsWith('/portal/gestion/'))return;
const MARK='midistri.dispositivo.olvido.v1',COOKIE='midistri_dispositivo_olvido',enabled=!!(document.body.dataset&&document.body.dataset.recordar==='1');
let busy=false,generation=0;
function saved(){try{return localStorage.getItem(MARK)==='1';}catch(_){return false;}}
function pending(){return saved()||document.cookie.split('; ').some(x=>x===COOKIE+'=1');}
function markLogout(){generation++;document.cookie=COOKIE+'=1; Max-Age=34560000; Path=/portal/; Secure; SameSite=Lax';try{localStorage.setItem(MARK,'1');}catch(_){}}
function completeLogout(){document.cookie=COOKIE+'=; Max-Age=0; Path=/portal/; Secure; SameSite=Lax';try{localStorage.removeItem(MARK);}catch(_){}}
function form(values){
    const data=new FormData();
    const token=document.querySelector('#midistri-recordado-csrf [name=csrfmiddlewaretoken]');
    if(token)data.set('csrfmiddlewaretoken',token.value);
    else{
        const csrf=document.cookie.split('; ').find(x=>x.startsWith('csrftoken='));
        if(csrf)data.set('csrfmiddlewaretoken',decodeURIComponent(csrf.slice(10)));
    }
    Object.entries(values||{}).forEach(([key,value])=>data.set(key,value));
    return data;
}
function notice(text,retry,loading){let node=document.getElementById('midistri-recordado-status');if(!node){node=document.createElement('section');node.id='midistri-recordado-status';node.role='status';document.querySelector('main').prepend(node);}node.replaceChildren();node.setAttribute('aria-busy',loading?'true':'false');const p=document.createElement('p');p.textContent=text;if(loading){p.className='recordado-espera';const spinner=document.createElement('span');spinner.className='recordado-spinner';spinner.setAttribute('aria-hidden','true');p.prepend(spinner);}node.append(p);if(retry){const b=document.createElement('button');b.type='button';b.textContent='Reintentar';b.onclick=()=>bootstrap();node.append(b);}}
async function forgetPending(){if(window.MidistriTab)MidistriTab.clear();try{const r=await fetch('/portal/acceso/olvidar/',{method:'POST',credentials:'same-origin',body:form(),headers:{Accept:'application/json'}});if(!r.ok)throw Error();completeLogout();notice('Saliste de MiDistri en este dispositivo.');}catch(_){notice('Saliste. Falta confirmar el olvido del dispositivo cuando vuelva la conexion.',true);}}
function choose(identities, switching){
    const box=document.createElement('section');
    box.id='midistri-recordado-status';
    const title=document.createElement('h2');
    title.textContent=switching?'Cambiar perfil':'Elegí con qué perfil entrar';
    const explanation=document.createElement('p');
    explanation.textContent=identities.length===1
        ?'Hay un solo perfil recordado. Si te falta un kiosco, volvé a verificar tu Email.'
        :'Elegí el kiosco que querés usar en esta pestaña.';
    const form=document.createElement('form');
    const label=document.createElement('label');
    const select=document.createElement('select');
    label.textContent='Kiosco';
    select.name='perfil_recordado';
    identities.forEach((identity,index)=>{
        const option=document.createElement('option');
        option.value=identity.seleccion;
        const duplicate=identities.some((item,n)=>n!==index&&item.nombre===identity.nombre);
        option.textContent=identity.nombre+(duplicate?' · Perfil '+(index+1):'');
        select.append(option);
    });
    label.append(select);
    const button=document.createElement('button');
    button.type='submit';
    button.textContent='Continuar';
    form.append(label,button);
    form.addEventListener('submit',event=>{
        event.preventDefault();
        event.stopPropagation();
        bootstrap(select.value);
    });
    const other=document.createElement('a');
    other.href='/portal/acceso/?perfiles=1&otro=1';
    other.textContent='Verificar mi Email';
    box.append(title,explanation,form,other);
    if(switching){
        const back=document.createElement('a');
        back.href='/portal/';
        back.textContent='Volver al catálogo';
        const actions=document.createElement('p');
        actions.append(back);
        box.append(actions);
    }
    document.querySelector('main').replaceChildren(box);
    select.focus();
}
async function bootstrap(selected){if(busy)return;const known=document.body.dataset&&document.body.dataset.recordarPresente==='1';const query=new URLSearchParams(location.search||'');const switching=query.get('perfiles')==='1';
if(pending()){busy=true;await forgetPending();busy=false;return;}
if(!enabled||query.get('otro')==='1'||!window.MidistriTab||(!known&&(switching||!MidistriTab.proof(false))))return;
busy=true;const version=generation;notice('Comprobando tu acceso recordado…',false,true);
try{MidistriTab.proof(true);const r=await MidistriTab.request('/portal/acceso/recordado/',{method:'POST',body:form(Object.assign(switching?{elegir:'1'}:{},selected?{seleccion:selected}:{})),headers:{Accept:'application/json'}});const data=await r.json();if(version!==generation||pending())return;
if(data.fase==='pestana_obsoleta'){MidistriTab.clear();notice(data.error,true);return;}
if(!r.ok){if(r.status===401||r.status===403){MidistriTab.clear();notice('El acceso ya no esta disponible. Ingresa con tu Email.');const a=document.createElement('a');a.href='/portal/acceso/?otro=1';a.textContent='Entrar con mi Email';document.querySelector('main').append(a);return;}throw Error(data.error||'No pudimos comprobar el acceso.');}
if(data.fase==='elegir'){choose(data.identidades,switching);return;}
if(data.fase==='dentro'){const target=location.pathname.startsWith('/portal/acceso/')?'/portal/':location.href;MidistriTab.load(target);return;}
if(data.fase==='sin_recuerdo'&&MidistriTab.proof(false)){const node=document.getElementById('midistri-recordado-status');if(node)node.remove();if(!location.pathname.startsWith('/portal/acceso/'))MidistriTab.load(location.href);}
}catch(e){if(version===generation&&!pending())notice(e.message||'No pudimos comprobar el acceso. Tu identificacion se conserva para reintentar.',true);}finally{busy=false;}}
window.MidistriRecordado={enabled,markLogout,completeLogout,loginCompleted:completeLogout,pending,bootstrap};
addEventListener('online',()=>{if(pending())bootstrap();});
addEventListener('storage',e=>{if(e.key===MARK&&e.newValue==='1'){generation++;if(window.MidistriTab)MidistriTab.clear();notice('Saliste de MiDistri en otra pestana de este dispositivo.');}});
bootstrap();
})();
