(function(){'use strict';
let dialog=null,items=[],index=0,origin=null,title='';
function stop(){if(dialog)dialog.querySelectorAll('video').forEach(v=>{v.pause();v.removeAttribute('src');v.load();});}
function close(){if(!dialog)return;stop();if(dialog.open)dialog.close();dialog.remove();dialog=null;document.body.classList.remove('galeria-abierta');if(origin&&origin.isConnected)origin.focus();}
function el(tag,text){const n=document.createElement(tag);if(text)n.textContent=text;return n;}
function show(n){stop();index=(n+items.length)%items.length;const item=items[index],stage=dialog.querySelector('.galeria-stage');stage.replaceChildren();
if(item.tipo==='foto'){const image=el('img');image.src=item.url;image.alt=item.descripcion||title;image.onerror=()=>{stage.replaceChildren(el('p','No pudimos cargar esta foto. Probá otro recurso.'));};stage.append(image);}
else if(item.tipo==='mp4'){const video=el('video');video.controls=true;video.preload='metadata';video.playsInline=true;video.src=item.url;video.onerror=()=>stage.append(el('p','No pudimos cargar este video.'));stage.append(video);}
else {const a=el('a','Abrir video en '+item.tipo);a.href=item.url;a.target='_blank';a.rel='noopener noreferrer';a.className='button';stage.append(a);}
dialog.querySelector('.galeria-counter').textContent=(index+1)+' de '+items.length+' · '+(item.descripcion||title);
dialog.querySelectorAll('[data-indice]').forEach(b=>b.setAttribute('aria-current',Number(b.dataset.indice)===index?'true':'false'));}
function open(id,indice,trigger){const source=document.getElementById('galeria-'+id);if(!source)return;
let data;try{data=JSON.parse(source.textContent);}catch(e){return;}if(!Array.isArray(data.items)||!data.items.length)return;
close();origin=trigger||document.activeElement;items=data.items;title=data.nombre;dialog=el('dialog');dialog.className='producto-galeria';dialog.setAttribute('aria-label','Fotos y videos de '+title);
const head=el('div');head.className='galeria-cabecera';head.append(el('h2',title));const exit=el('button','Cerrar ×');exit.type='button';exit.addEventListener('click',close);head.append(exit);dialog.append(head);
const stage=el('div');stage.className='galeria-stage';dialog.append(stage);const status=el('p');status.className='galeria-counter';status.setAttribute('aria-live','polite');dialog.append(status);
const controls=el('div');controls.className='galeria-controles';[['Anterior',-1],['Siguiente',1]].forEach(pair=>{const b=el('button',pair[0]);b.type='button';b.disabled=items.length<2;b.addEventListener('click',()=>show(index+pair[1]));controls.append(b);});dialog.append(controls);
const thumbs=el('div');thumbs.className='galeria-miniaturas';items.forEach((item,i)=>{const b=el('button');b.type='button';b.dataset.indice=i;b.setAttribute('aria-label','Ver recurso '+(i+1));if(item.tipo==='foto'){const img=el('img');img.src=item.url;img.alt='';img.loading='lazy';b.append(img);}else b.textContent='▶ Video '+(i+1);b.addEventListener('click',()=>show(i));thumbs.append(b);});dialog.append(thumbs);
dialog.addEventListener('cancel',e=>{e.preventDefault();close();});dialog.addEventListener('click',e=>{if(e.target===dialog)close();});
dialog.addEventListener('keydown',e=>{if(e.key==='ArrowRight'){e.preventDefault();show(index+1);}if(e.key==='ArrowLeft'){e.preventDefault();show(index-1);}if(e.key==='Escape'){e.preventDefault();close();}
if(e.key==='Tab'){const focus=[...dialog.querySelectorAll('button:not(:disabled),a[href],video[controls]')];if(e.shiftKey&&document.activeElement===focus[0]){e.preventDefault();focus[focus.length-1].focus();}else if(!e.shiftKey&&document.activeElement===focus[focus.length-1]){e.preventDefault();focus[0].focus();}}});
document.body.append(dialog);document.body.classList.add('galeria-abierta');if(dialog.showModal)dialog.showModal();else {dialog.setAttribute('open','');dialog.setAttribute('role','dialog');dialog.setAttribute('aria-modal','true');}show(indice||0);exit.focus();}
document.addEventListener('click',e=>{const a=e.target.closest('[data-galeria]');if(!a||e.ctrlKey||e.metaKey||e.shiftKey||e.altKey)return;e.preventDefault();open(a.dataset.galeria,0,a);});
document.addEventListener('midistri:render',()=>{stop();dialog=null;document.body.classList.remove('galeria-abierta');});
window.abrirGaleria=open;window.cerrarGaleria=close;
})();