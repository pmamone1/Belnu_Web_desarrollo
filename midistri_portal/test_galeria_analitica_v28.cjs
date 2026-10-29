const vm=require('node:vm'),fs=require('node:fs'),assert=require('node:assert/strict');
let events=[],images=[];
class Element{
 constructor(tag){this.tag=tag;this.children=[];this.dataset={};this.handlers={};this.className='';this.open=false;this.isConnected=true;this.classList={add(){},remove(){}};if(tag==='img')images.push(this);}
 append(...n){n.forEach(x=>{x.parent=this;this.children.push(x);});} replaceChildren(...n){this.children=[];this.append(...n);} get firstChild(){return this.children[0];}
 addEventListener(k,f){(this.handlers[k]??=[]).push(f);} fire(k){for(const f of this.handlers[k]||[])f({target:this});}
 remove(){if(this.parent)this.parent.children=this.parent.children.filter(c=>c!==this);} setAttribute(){} removeAttribute(){} focus(){} pause(){} load(){} showModal(){this.open=true;} close(){this.open=false;}
 contains(n){return n===this||this.children.some(c=>c.contains(n));}
 querySelector(s){return this.querySelectorAll(s)[0];} querySelectorAll(s){let result=[];for(const c of this.children){if(s.startsWith('.')?c.className===s.slice(1):s==='video'?c.tag==='video':s==='[data-indice]'?c.dataset.indice!==undefined:false)result.push(c);result.push(...c.querySelectorAll(s));}return result;}
}
const body=new Element('body');const doc={body,activeElement:null,createElement:t=>new Element(t),getElementById:id=>({textContent:JSON.stringify({nombre:id,items:[{tipo:'foto',url:'/foto.png'}]})}),addEventListener(){},dispatchEvent:e=>events.push(e.detail)};
const window={};vm.runInNewContext(fs.readFileSync('midistri_portal/static/midistri_portal/galeria.js','utf8'),{document:doc,window,CustomEvent:class{constructor(n,o){this.detail=o.detail;}}});
window.abrirGaleria(1,0);let old=images.at(-1);window.cerrarGaleria();window.abrirGaleria(2,0);old.fire('load');assert.equal(events.filter(e=>e.tipo==='foto_ampliada').length,0,'Una foto vieja oculta no puede contarse como foto del producto nuevo');images.at(-1).fire('load');assert.equal(events.filter(e=>e.tipo==='foto_ampliada').length,1);assert.equal(events.at(-1).producto,2);console.log('OK galería: carga tardía oculta excluida; foto visible atribuida correctamente');
