const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
const source=fs.readFileSync(require('node:path').join(__dirname,'../midistri_portal/static/midistri_portal/promociones.js'),'utf8');
function render(stored,initial){
 const selector={value:initial,dataset:{temaTienda:'20'},addEventListener(){}};
 const document={readyState:'complete',body:{dataset:{}},querySelector(){return selector;},addEventListener(){}};
 vm.runInNewContext(source,{document,localStorage:{getItem(){return stored;}}});
 return document.body.dataset.tema;
}
assert.equal(render('terracota','azul'),'claro');
assert.equal(render('violeta_pastel','verde'),'claro');
assert.equal(render('ambar_pastel','nocturno'),'claro');
assert.equal(render('nocturno','azul'),'nocturno');
assert.equal(render(null,'verde'),'verde');
console.log('5 escenarios de preferencias: OK');
