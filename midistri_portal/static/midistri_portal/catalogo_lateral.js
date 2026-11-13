/* Progressive enhancement: native filters remain open and usable without JS. */
(function(){
'use strict';
const media=window.matchMedia('(max-width:1023px)');
let panels=new Set();
function layout(panel){panel.open=!(media.matches||panel.closest('.preview-movil'));}
function initialize(){
    const current=new Set(document.querySelectorAll('[data-catalogo-panel]'));
    current.forEach(panel=>{if(!panels.has(panel))layout(panel);});
    panels=current; // Release detached panels after session body replacement.
}
function breakpoint(){panels.forEach(layout);}
if(media.addEventListener)media.addEventListener('change',breakpoint);
else media.addListener(breakpoint);
document.addEventListener('midistri:render',initialize);
initialize();
})();
