/* Store banners: one source of rotation, user controls always win. */
(function () {
'use strict';
var reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
var disposers=[];
function init(){
    disposers.forEach(function(dispose){dispose();});disposers=[];
    document.querySelectorAll('[data-banner]').forEach(function (root) {
    var slides=Array.from(root.querySelectorAll('[data-slide]'));
    if(slides.length<2)return;
    var index=0,timer=null,automatic=root.dataset.automatico==='si';
    var paused=reduced.matches,focused=false,hovered=false;
    var button=root.querySelector('[data-banner-pausa]'),count=root.querySelector('[data-banner-contador]');
    function stop(){if(timer){clearInterval(timer);timer=null;}}
    function show(n){
        slides[index].querySelectorAll('video').forEach(function(v){v.pause();});
        index=(n+slides.length)%slides.length;
        slides.forEach(function(s,i){s.hidden=i!==index;});
        if(count)count.textContent=(index+1)+' / '+slides.length;
    }
    function state(){
        stop();
        if(button){button.textContent=paused?'Reanudar':'Pausar';button.setAttribute('aria-pressed',String(paused));}
        if(root.isConnected&&automatic&&!paused&&!focused&&!hovered&&!document.hidden)
            timer=setInterval(function(){show(index+1);},Math.max(3,Math.min(15,Number(root.dataset.segundos)||5))*1000);
    }
    function manual(n){paused=true;show(n);state();}
    root.querySelector('[data-banner-prev]').addEventListener('click',function(){manual(index-1);});
    root.querySelector('[data-banner-next]').addEventListener('click',function(){manual(index+1);});
    if(button)button.addEventListener('click',function(){paused=!paused;state();});
    root.addEventListener('keydown',function(e){
        if(e.target.matches('input,textarea,select,video'))return;
        if(e.key==='ArrowRight'){e.preventDefault();manual(index+1);}
        if(e.key==='ArrowLeft'){e.preventDefault();manual(index-1);}
    });
    root.addEventListener('focusin',function(){focused=true;state();});
    root.addEventListener('focusout',function(e){if(!root.contains(e.relatedTarget)){focused=false;state();}});
    root.addEventListener('mouseenter',function(){hovered=true;state();});
    root.addEventListener('mouseleave',function(){hovered=false;state();});
    root.addEventListener('pointerdown',function(){stop();});
    var startX=null;
    root.addEventListener('touchstart',function(e){startX=e.touches[0].clientX;stop();},{passive:true});
    root.addEventListener('touchend',function(e){if(startX!==null){var dx=e.changedTouches[0].clientX-startX;if(Math.abs(dx)>40)manual(index+(dx<0?1:-1));startX=null;}},{passive:true});
    root.addEventListener('play',function(){paused=true;state();},true);
    document.addEventListener('visibilitychange',state);
    function motion(e){if(e.matches){paused=true;state();}}
    if(reduced.addEventListener)reduced.addEventListener('change',motion);else reduced.addListener(motion);
    disposers.push(function(){
        stop();document.removeEventListener('visibilitychange',state);
        if(reduced.removeEventListener)reduced.removeEventListener('change',motion);else reduced.removeListener(motion);
    });
    show(0);state();
    });
}
document.addEventListener('midistri:render',init);
init();
})();
