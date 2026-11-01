/* Progressive enhancement: native filters remain open and usable without JS. */
(function(){
'use strict';
const media=window.matchMedia('(max-width:1023px)');
let panels=new Set(),cart=null,cartObserver=null;
function layout(panel){panel.open=!(media.matches||panel.closest('.preview-movil'));}
function cartSpace(){
    const rect=cart&&cart.isConnected?cart.getBoundingClientRect():null;
    const height=rect&&rect.height?Math.max(0,window.innerHeight-rect.top):0;
    document.documentElement.style.setProperty('--catalogo-carrito-alto',height+'px');
}
function initialize(){
    const current=new Set(document.querySelectorAll('[data-catalogo-panel]'));
    current.forEach(panel=>{if(!panels.has(panel))layout(panel);});
    panels=current; // Release detached panels after session body replacement.
    const nextCart=document.querySelector('body>.sticky');
    if(cart!==nextCart){
        if(cartObserver)cartObserver.disconnect();
        cart=nextCart;
        if(cart&&window.ResizeObserver){
            cartObserver=new ResizeObserver(cartSpace);
            cartObserver.observe(cart,{box:'border-box'});
        }
    }
    cartSpace();
}
function breakpoint(){panels.forEach(layout);cartSpace();}
if(media.addEventListener)media.addEventListener('change',breakpoint);
else media.addListener(breakpoint);
window.addEventListener('resize',cartSpace);
document.addEventListener('midistri:render',initialize);
initialize();
})();
