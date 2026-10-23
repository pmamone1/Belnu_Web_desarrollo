(function(){'use strict';
if(location.pathname.startsWith('/portal/administrar/')||location.pathname.startsWith('/portal/gestion/'))return;
const KEY='midistri.tab.v1',PENDING='midistri.logout.pending.v1';let busy=false,closing=false;
function proof(create){try{let p=JSON.parse(sessionStorage.getItem(KEY)||'null');if(p&&/^[0-9a-f-]{36}$/.test(p.id)&&/^[0-9a-f]{64}$/.test(p.proof))return p;
if(!create)return null;const a=new Uint8Array(32);crypto.getRandomValues(a);p={id:crypto.randomUUID?crypto.randomUUID():([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g,c=>(c^crypto.getRandomValues(new Uint8Array(1))[0]&15>>c/4).toString(16)),proof:Array.from(a,x=>x.toString(16).padStart(2,'0')).join('')};sessionStorage.setItem(KEY,JSON.stringify(p));return p;}catch(e){return null;}}
function headers(p){return p?{'X-Midistri-Tab':p.id,'X-Midistri-Tab-Proof':p.proof}:{};}
function notice(text){let n=document.getElementById('midistri-session-status');if(!n){n=document.createElement('p');n.id='midistri-session-status';n.className='notice';n.role='status';document.querySelector('main').prepend(n);}n.textContent=text;}
async function raw(url,options,p){return fetch(url,Object.assign({credentials:'same-origin',redirect:'follow'},options,{headers:Object.assign({},options&&options.headers,headers(p))}));}
function cleared(){const main=document.createElement('main');const p=document.createElement('p');p.textContent='Cerraste el acceso en esta pestaña.';main.append(p);const a=document.createElement('a');a.href='/portal/';a.textContent='Volver al portal';main.append(a);document.body.replaceChildren(main);}
function pending(){try{return JSON.parse(sessionStorage.getItem(PENDING)||'null');}catch(e){return null;}}
function retryNotice(){notice('Cerraste el acceso en esta pestaña. Falta confirmar el cierre remoto. Se reintentará al volver la conexión.');const b=document.createElement('button');b.type='button';b.textContent='Reintentar cierre remoto';b.onclick=retryLogout;document.querySelector('main').append(b);}
async function retryLogout(){const item=pending();if(!item||closing)return;closing=true;try{
const data=new FormData();const cookie=document.cookie.split('; ').find(x=>x.startsWith('csrftoken='));data.set('csrfmiddlewaretoken',cookie?decodeURIComponent(cookie.slice(10)):item.csrf);
const r=await raw('/portal/salir/',{method:'POST',body:data,headers:{Accept:'application/json'}},item.proof);
if(!r.ok)throw Error('pending');sessionStorage.removeItem(PENDING);notice('Cierre remoto confirmado.');
}catch(e){retryNotice();}finally{closing=false;}}
async function navigate(url,options,logout,replace){const p=proof(false);if(busy)return;busy=true;if(logout){
sessionStorage.setItem(PENDING,JSON.stringify({proof:p,csrf:options.body.get?options.body.get('csrfmiddlewaretoken'):''}));
sessionStorage.removeItem(KEY);cleared();options=Object.assign({},options,{headers:{'Accept':'application/json'}});}
try{const r=await raw(url,options,p);const type=r.headers.get('Content-Type')||'';
if(type.includes('application/json')){const data=await r.json();if(logout&&r.ok){sessionStorage.removeItem(PENDING);location.replace('/portal/');return;}if(logout&&!r.ok){retryNotice();return;}if(!r.ok){if(r.status===403)sessionStorage.removeItem(KEY);notice(data.error||'No pudimos completar la operación.');return;}return;}
if(type.includes('application/pdf')){if(!r.ok){notice('No pudimos abrir el remito.');return;}const blob=URL.createObjectURL(await r.blob());const a=document.createElement('a');a.href=blob;a.download='remitos_pedido.pdf';a.click();setTimeout(()=>URL.revokeObjectURL(blob),60000);return;}
const html=await r.text();const page=new DOMParser().parseFromString(html,'text/html');page.querySelectorAll('script:not([type="application/json"])').forEach(x=>x.remove());document.title=page.title;document.body.replaceChildren(...page.body.childNodes);history[replace?'replaceState':'pushState']({},'',r.url);document.dispatchEvent(new CustomEvent('midistri:render'));if(r.status>=500)notice('No pudimos conectar. Tu pedido se conserva para reintentar.');
}catch(e){if(logout){retryNotice();return;}notice(logout?'Cerramos el acceso en esta pestaña. No pudimos confirmar el cierre remoto por falta de conexión.':'No pudimos conectar. Conservamos tu pedido; podés reintentar.');}
finally{busy=false;}}
addEventListener('online',retryLogout);if(pending())retryLogout();
window.MidistriTab={proof:proof,request:(url,options)=>raw(url,options,proof(true))};
document.addEventListener('click',e=>{const a=e.target.closest('a');if(!a||a.target==='_blank'||a.download||e.ctrlKey||e.metaKey||e.shiftKey||e.altKey)return;const url=new URL(a.href,location.href);if(url.origin!==location.origin||!url.pathname.startsWith('/portal/')||url.pathname.startsWith('/portal/administrar/')||url.pathname.startsWith('/portal/acceso/')||url.hash)return;if(!proof(false))return;e.preventDefault();navigate(url.href);});
document.addEventListener('submit',e=>{const f=e.target;if(f.dataset.codigo||!f.action)return;const url=new URL(f.action,location.href);if(url.origin!==location.origin||!url.pathname.startsWith('/portal/')||url.pathname.startsWith('/portal/administrar/')||url.pathname.startsWith('/portal/acceso/')||!proof(false))return;e.preventDefault();if(f.method.toLowerCase()==='get'){const u=new URL(f.action);u.search=new URLSearchParams(new FormData(f));navigate(u.href);}else navigate(f.action,{method:'POST',body:new FormData(f)},url.pathname==='/portal/salir/');});
addEventListener('popstate',()=>{if(proof(false))navigate(location.href,undefined,false,true);});
if(!location.pathname.startsWith('/portal/acceso/')&&!location.pathname.startsWith('/portal/activar/')&&proof(false))navigate(location.href,undefined,false,true);
})();