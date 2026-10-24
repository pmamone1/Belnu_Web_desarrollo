const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm');
function harness(){
 const listeners={},calls=[],messages={textContent:''};let resolve,clipboardReads=0;
 const input={name:'codigo',value:'',focus(){},closest:()=>forms.verificar};
 const select={replaceChildren(){this.options=[];},options:[],append(x){this.options.push(x);},focus(){}};
 const forms={};
 for(const phase of ['iniciar','verificar','seleccionar']){
  const buttons=[{disabled:false},{disabled:false}];
  forms[phase]={dataset:{codigo:phase},hidden:phase!=='verificar',action:'/'+phase,buttons,
   querySelector(s){if(s==='button')return buttons[0];if(s.includes('codigo'))return input;return null;},
   querySelectorAll(s){return s==='button'?buttons:[];},
   checkValidity(){return phase!=='verificar'||/^[0-9]{6}$/.test(input.value);},
   requestSubmit(){return fire('submit',{target:this,preventDefault(){}});}};
 }
 const options={hidden:false};
 const doc={addEventListener(n,f){(listeners[n]??=[]).push(f);},getElementById(id){return id==='acceso-mensaje'?messages:options;},
 querySelectorAll(){return Object.values(forms);},querySelector(s){if(s.includes('name=codigo'))return input;if(s.includes('name=seleccion'))return select;if(s.includes('data-codigo=iniciar'))return forms.iniciar;return {focus(){}};},
 createElement(){return {};}};
 const clipboard={async readText(){clipboardReads++;return '123 456';}};
 const tab={proof:()=>true,request:async(url,options)=>{calls.push(url);return await new Promise(r=>resolve=r);}};
 const ctx={document:doc,window:{MidistriTab:tab,isSecureContext:true},MidistriTab:tab,navigator:{clipboard},location:{assign(u){ctx.destination=u;}},FormData:class{},setTimeout,clearTimeout,console};
 vm.runInNewContext(fs.readFileSync('midistri_portal/static/midistri_portal/acceso.js','utf8'),ctx);
 async function fire(name,e){for(const fn of listeners[name]||[])await fn(e);await Promise.resolve();}
 async function settle(data={fase:'dentro',url:'/portal/'},ok=true){resolve({ok,json:async()=>data});await new Promise(r=>setImmediate(r));}
 return {calls,input,forms,messages,select,clipboard,ctx,fire,settle,reads:()=>clipboardReads};
}
test('autofill completo verifica una sola vez mientras esta en curso',async()=>{
 const h=harness();h.input.value='123456';await h.fire('input',{target:h.input});
 assert.deepEqual(h.calls,['/verificar']);await h.fire('input',{target:h.input});
 h.forms.verificar.requestSubmit();assert.equal(h.calls.length,1);await h.settle();assert.equal(h.ctx.destination,'/portal/');
});
test('pegado con espacios normaliza y verifica',async()=>{
 const h=harness();await h.fire('paste',{target:h.input,clipboardData:{getData:()=> '123 456\n'},preventDefault(){}});
 assert.equal(h.input.value,'123456');assert.equal(h.calls.length,1);await h.settle();
});
test('no extrae codigos de texto arbitrario ni lee clipboard al enfocar',async()=>{
 const h=harness();let prevented=false;await h.fire('paste',{target:h.input,clipboardData:{getData:()=> '123456 texto externo'},preventDefault(){prevented=true;}});assert.equal(prevented,true);
 await h.fire('focusin',{target:h.input});assert.equal(h.calls.length,0);assert.equal(h.reads(),0);
});
test('codigo incompleto no envia',async()=>{const h=harness();h.input.value='12345';await h.fire('input',{target:h.input});assert.equal(h.calls.length,0);});
test('boton pegar requiere click y conserva alternativa manual',async()=>{
 const h=harness();await h.fire('click',{target:{closest(s){return s==='[data-acceso-pegar]'?{}:null;}}});
 assert.equal(h.reads(),1);assert.equal(h.input.value,'123456');assert.equal(h.calls.length,1);await h.settle();
});
test('clipboard rechazado informa como pegar y no envia',async()=>{
 const h=harness();h.clipboard.readText=async()=>{throw Error('denegado');};
 await h.fire('click',{target:{closest(s){return s==='[data-acceso-pegar]'?{}:null;}}});
 assert.equal(h.calls.length,0);assert.match(h.messages.textContent,/peg|Peg/);
});
test('error no reintenta el mismo codigo automaticamente; permite editar',async()=>{
 const h=harness();h.input.value='123456';await h.fire('input',{target:h.input});assert.equal(h.calls.length,1);
 await h.settle({error:'Codigo incorrecto'},false);await h.fire('input',{target:h.input});assert.equal(h.calls.length,1);
 h.input.value='654321';await h.fire('input',{target:h.input});assert.equal(h.calls.length,2);await h.settle();
});
test('varios perfiles requieren seleccion, no ingresan automaticamente',async()=>{
 const h=harness();h.input.value='123456';await h.fire('input',{target:h.input});assert.equal(h.calls.length,1);
 await h.settle({fase:'elegir',identidades:[{seleccion:'uno',nombre:'Kiosco',distribuidora:'Tienda',tipo:'vendedor'}]});
 assert.equal(h.forms.seleccionar.hidden,false);assert.equal(h.select.options.length,1);assert.equal(h.ctx.destination,undefined);assert.equal(h.calls.length,1);
});

test('reenviar reinicia el codigo y no conserva autoenvio anterior',async()=>{
 const h=harness();h.input.value='123456';await h.fire('input',{target:h.input});await h.settle({error:'Incorrecto'},false);
 await h.fire('click',{target:{closest(s){return s==='[data-acceso-reenviar]'?{}:null;}}});
 assert.equal(h.input.value,'');assert.equal(h.calls.length,2);await h.settle({fase:'codigo'});
 h.input.value='123456';await h.fire('input',{target:h.input});assert.equal(h.calls.length,3);await h.settle();
});
