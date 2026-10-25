/* A pending promise is progress, never an invented percentage. */
(function(g){'use strict';
class EditorProgreso{
 constructor(root){this.root=root;this.busy=false;}
 async run(text,work){
  if(this.busy)return;
  this.busy=true;this.root.setAttribute('aria-busy','true');
  const buttons=Array.from(this.root.querySelectorAll('dialog button')),previous=buttons.map(b=>b.disabled);
  buttons.forEach(b=>b.disabled=true);
  this.root.querySelectorAll('[data-editor-progreso-texto]').forEach(el=>el.textContent=text);
  this.root.querySelectorAll('[data-editor-progreso]').forEach(el=>el.hidden=false);
  try{return await work();}finally{
   this.busy=false;this.root.setAttribute('aria-busy','false');
   this.root.querySelectorAll('[data-editor-progreso]').forEach(el=>el.hidden=true);
   buttons.forEach((b,i)=>b.disabled=previous[i]);
  }
 }
}
g.EditorProgreso=EditorProgreso;
})(globalThis);
