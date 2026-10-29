(function(){'use strict';
const KEY='midistri.analitica.cola.v1';let context=null,queue=[],busy=false,timer=null,failures=0;
function read(){try{const n=document.querySelector('#analitica-contexto');return n?JSON.parse(n.textContent):null;}catch(_){return null;}}
function save(){try{sessionStorage.setItem(KEY,JSON.stringify({actor:context&&context.actor,eventos:queue.slice(-100)}));}catch(_){}}
function sync(){const next=read();if(!next||!context||next.actor!==context.actor){queue=[];failures=0;}context=next;if(!next){save();return;}
try{const old=JSON.parse(sessionStorage.getItem(KEY)||'null');if(old&&old.actor===next.actor&&Array.isArray(old.eventos)&&!queue.length)queue=old.eventos.slice(-100);}catch(_){}save();}
function schedule(){if(!timer&&!busy&&context&&queue.length&&failures<3)timer=setTimeout(flush,250);}
function request(url,opts){return window.MidistriTab?window.MidistriTab.request(url,opts):fetch(url,Object.assign({credentials:'same-origin'},opts));}
function csrf(){const n=document.querySelector('[name=csrfmiddlewaretoken]');return n?n.value:'';}
function emit(data){if(!context)return;if(!['producto_consulta','foto_ampliada','video_mp4','video_enlace'].includes(data.tipo))return;
let id;try{id=crypto.randomUUID?crypto.randomUUID():'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g,c=>{const n=crypto.getRandomValues(new Uint8Array(1))[0]&15;return (c==='x'?n:(n&3|8)).toString(16);});}catch(_){return;}
const row={id:id,tipo:data.tipo,producto:data.producto};if(data.recurso!==undefined)row.recurso=data.recurso;
queue.push(row);queue=queue.slice(-100);failures=0;save();schedule();}
async function flush(){timer=null;if(busy||!context||!queue.length||failures>=3)return;busy=true;const batch=queue.slice(0,20),owner=context.actor;
try{let response=await request('/portal/actividad/eventos/',{method:'POST',headers:{'Content-Type':'application/json','X-CSRFToken':csrf()},body:JSON.stringify({firma:context.firma,eventos:batch}),keepalive:true});
if(response.status===409){const data=await response.json();if(data.renovar){const r=await request('/portal/actividad/contexto/',{});if(!r.ok)throw Error('contexto');const updated=(await r.json()).contexto;if(!updated||updated.actor!==owner)throw Error('actor');context=updated;failures++;return;}}
if(!response.ok&&response.status>=500||response.status===429)throw Error('red');
const ids=new Set(batch.map(e=>e.id));queue=queue.filter(e=>!ids.has(e.id));failures=0;
}catch(_){failures++;}finally{busy=false;save();schedule();}}
window.MidistriAnalytics={emit:emit};document.addEventListener('midistri:analytics',e=>emit(e.detail||{}));
document.addEventListener('midistri:render',()=>{sync();schedule();});window.addEventListener('online',()=>{failures=0;schedule();});window.addEventListener('pagehide',()=>{if(!busy)flush();});sync();schedule();
}());
