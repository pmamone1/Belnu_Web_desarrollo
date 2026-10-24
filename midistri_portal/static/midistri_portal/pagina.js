/* One cancellable transition and timer per banner, including tab-session navigation. */
(function () {
'use strict';
var reduced=window.matchMedia('(prefers-reduced-motion: reduce)'),disposers=[];
function init(){
 disposers.forEach(function(dispose){dispose();});disposers=[];
 document.querySelectorAll('[data-banner]').forEach(function(root){
  var slides=Array.from(root.querySelectorAll('[data-slide]'));
  if(!slides.length)return;
  var index=0,timer=null,animations=[],generation=0,listeners=[];
  var automatic=root.dataset.automatico==='si',paused=reduced.matches,focused=false,hovered=false;
  var button=root.querySelector('[data-banner-pausa]'),count=root.querySelector('[data-banner-contador]');
  function on(target,event,fn,options){target.addEventListener(event,fn,options);listeners.push(function(){target.removeEventListener(event,fn,options);});}
  function stop(){if(timer){clearInterval(timer);timer=null;}}
  function cancel(){generation++;animations.forEach(function(a){a.cancel();});animations=[];}
  function settle(){slides.forEach(function(s,i){s.hidden=i!==index;s.inert=i!==index;s.setAttribute('aria-hidden',String(i!==index));});}
  function show(n,animate){
   var old=index;cancel();index=(n+slides.length)%slides.length;
   slides.forEach(function(s,i){
    s.hidden=i!==index;s.inert=i!==index;s.setAttribute('aria-hidden',String(i!==index));
    if(i!==index)s.querySelectorAll('video').forEach(function(v){v.pause();});
   });
   if(count)count.textContent=(index+1)+' / '+slides.length;
   if(!animate||old===index||reduced.matches||!slides[index].animate)return;
   var outgoing=slides[old],incoming=slides[index],token=generation;
   outgoing.hidden=false; // inert and aria-hidden: outgoing links never remain interactive.
   animations=[
    outgoing.animate([{opacity:1},{opacity:0}],{duration:600,easing:'cubic-bezier(.22,.61,.36,1)'}),
    incoming.animate([{opacity:0},{opacity:1}],{duration:600,easing:'cubic-bezier(.22,.61,.36,1)'})
   ];
   Promise.all(animations.map(function(a){return a.finished.catch(function(){});})).then(function(){if(token===generation){settle();animations=[];}});
  }
  function state(){
   stop();
   if(button){button.textContent=paused?'Reanudar':'Pausar';button.setAttribute('aria-pressed',String(paused));}
   if(slides.length>1&&root.isConnected&&automatic&&!paused&&!focused&&!hovered&&!document.hidden)
    timer=setInterval(function(){show(index+1,true);},Math.max(3,Math.min(15,Number(root.dataset.segundos)||5))*1000);
  }
  function manual(n){paused=true;show(n,true);state();}
  var prev=root.querySelector('[data-banner-prev]'),next=root.querySelector('[data-banner-next]');
  if(prev)on(prev,'click',function(){manual(index-1);});
  if(next)on(next,'click',function(){manual(index+1);});
  if(button)on(button,'click',function(){paused=!paused;state();});
  on(root,'keydown',function(e){
   if(e.target.matches('input,textarea,select,video')||slides.length<2)return;
   if(e.key==='ArrowRight'){e.preventDefault();manual(index+1);}
   if(e.key==='ArrowLeft'){e.preventDefault();manual(index-1);}
  });
  on(root,'focusin',function(){focused=true;state();});
  on(root,'focusout',function(e){if(!root.contains(e.relatedTarget)){focused=false;state();}});
  on(root,'mouseenter',function(){hovered=true;state();});
  on(root,'mouseleave',function(){hovered=false;state();});
  on(root,'pointerdown',stop);
  var startX=null;
  on(root,'touchstart',function(e){startX=e.touches[0].clientX;stop();},{passive:true});
  on(root,'touchend',function(e){if(startX!==null){var dx=e.changedTouches[0].clientX-startX;if(Math.abs(dx)>40)manual(index+(dx<0?1:-1));startX=null;}state();},{passive:true});
  on(root,'play',function(){paused=true;state();},true);
  on(document,'visibilitychange',function(){if(document.hidden){cancel();settle();}state();});
  function motion(e){if(e.matches){paused=true;cancel();settle();state();}}
  if(reduced.addEventListener)on(reduced,'change',motion);
  else {reduced.addListener(motion);listeners.push(function(){reduced.removeListener(motion);});}
  disposers.push(function(){stop();cancel();settle();listeners.forEach(function(remove){remove();});});
  show(0,false);state();
 });
}
document.addEventListener('midistri:render',init);
init();
})();
