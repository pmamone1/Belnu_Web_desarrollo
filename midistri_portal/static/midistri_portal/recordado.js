(function(){'use strict';
if(location.pathname.startsWith('/portal/administrar/')||location.pathname.startsWith('/portal/gestion/'))return;
const MARK='midistri.dispositivo.olvido.v1',COOKIE='midistri_dispositivo_olvido',enabled=!!(document.body.dataset&&document.body.dataset.recordar==='1');
let busy=false,generation=0;
function saved(){try{return localStorage.getItem(MARK)==='1';}catch(_){return false;}}
function pending(){return saved()||document.cookie.split('; ').some(x=>x===COOKIE+'=1');}
function markLogout(){generation++;document.cookie=COOKIE+'=1; Max-Age=34560000; Path=/portal/; Secure; SameSite=Lax';try{localStorage.setItem(MARK,'1');}catch(_){}}
function completeLogout(){document.cookie=COOKIE+'=; Max-Age=0; Path=/portal/; Secure; SameSite=Lax';try{localStorage.removeItem(MARK);}catch(_){}}
function form(values){const f=new FormData();const csrf=document.cookie.split('; ').find(x=>x.startsWith('csrftoken='));if(csrf)f.set('csrfmiddlewaretoken',decodeURIComponent(csrf.slice(10)));Object.entries(values||{}).forEach(([k,v])=>f.set(k,v));return f;}
function notice(text,retry,loading){let node=document.getElementById('midistri-recordado-status');if(!node){node=document.createElement('section');node.id='midistri-recordado-status';node.role='status';document.querySelector('main').prepend(node);}node.replaceChildren();node.setAttribute('aria-busy',loading?'true':'false');const p=document.createElement('p');p.textContent=text;if(loading){p.className='recordado-espera';const spinner=document.createElement('span');spinner.className='recordado-spinner';spinner.setAttribute('aria-hidden','true');p.prepend(spinner);}node.append(p);if(retry){const b=document.createElement('button');b.type='button';b.textContent='Reintentar';b.onclick=()=>bootstrap();node.append(b);}}
async function forgetPending(){if(window.MidistriTab)MidistriTab.clear();try{const r=await fetch('/portal/acceso/olvidar/',{method:'POST',credentials:'same-origin',body:form(),headers:{Accept:'application/json'}});if(!r.ok)throw Error();completeLogout();notice('Saliste de MiDistri en este dispositivo.');}catch(_){notice('Saliste. Falta confirmar el olvido del dispositivo cuando vuelva la conexion.',true);}}
function choose(identities){const box=document.createElement('section');box.id='midistri-recordado-status';const title=document.createElement('h2');title.textContent='Elegi con que perfil entrar';const explanation=document.createElement('p');explanation.textContent='Este dispositivo ya esta reconocido. No necesitas otro codigo.';const f=document.createElement('form'),label=document.createElement('label'),select=document.createElement('select');label.textContent='Vendedor';select.name='perfil_recordado';identities.forEach(i=>{const o=document.createElement('option');o.value=i.seleccion;o.textContent=i.nombre+' · '+i.distribuidora;select.append(o);});label.append(select);const b=document.createElement('button');b.type='submit';b.textContent='Continuar';f.append(label,b);f.addEventListener('submit',e=>{e.preventDefault();e.stopPropagation();bootstrap(select.value);});const other=document.createElement('a');other.href='/portal/acceso/?otro=1';other.textContent='Entrar con otro Email';box.append(title,explanation,f,other);document.querySelector('main').replaceChildren(box);}
async function bootstrap(selected){if(busy)return;const known=document.body.dataset&&document.body.dataset.recordarPresente==='1';const query=new URLSearchParams(location.search||'');
if(pending()){busy=true;await forgetPending();busy=false;return;}
if(!enabled||query.get('otro')==='1'||!window.MidistriTab||(!known&&!MidistriTab.proof(false)))return;
busy=true;const version=generation;notice('Comprobando tu acceso recordado…',false,true);
try{MidistriTab.proof(true);const r=await MidistriTab.request('/portal/acceso/recordado/',{method:'POST',body:form(Object.assign(query.get('perfiles')==='1'?{elegir:'1'}:{},selected?{seleccion:selected}:{})),headers:{Accept:'application/json'}});const data=await r.json();if(version!==generation||pending())return;
if(data.fase==='pestana_obsoleta'){MidistriTab.clear();notice(data.error,true);return;}
if(!r.ok){if(r.status===401||r.status===403){MidistriTab.clear();notice('El acceso ya no esta disponible. Ingresa con tu Email.');const a=document.createElement('a');a.href='/portal/acceso/?otro=1';a.textContent='Entrar con mi Email';document.querySelector('main').append(a);return;}throw Error(data.error||'No pudimos comprobar el acceso.');}
if(data.fase==='elegir'){choose(data.identidades);return;}
if(data.fase==='dentro'){const target=location.pathname.startsWith('/portal/acceso/')?'/portal/':location.href;MidistriTab.load(target);return;}
if(data.fase==='sin_recuerdo'&&MidistriTab.proof(false)){const node=document.getElementById('midistri-recordado-status');if(node)node.remove();if(!location.pathname.startsWith('/portal/acceso/'))MidistriTab.load(location.href);}
}catch(e){if(version===generation&&!pending())notice(e.message||'No pudimos comprobar el acceso. Tu identificacion se conserva para reintentar.',true);}finally{busy=false;}}
window.MidistriRecordado={enabled,markLogout,completeLogout,loginCompleted:completeLogout,pending,bootstrap};
addEventListener('online',()=>{if(pending())bootstrap();});
addEventListener('storage',e=>{if(e.key===MARK&&e.newValue==='1'){generation++;if(window.MidistriTab)MidistriTab.clear();notice('Saliste de MiDistri en otra pestana de este dispositivo.');}});
bootstrap();
})();
