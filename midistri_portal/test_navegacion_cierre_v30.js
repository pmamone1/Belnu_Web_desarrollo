const assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),path=require('node:path');
(async()=>{
const storage=new Map([['midistri.tab.v1',JSON.stringify({id:'12345678-1234-4321-abcd-123456789012',proof:'a'.repeat(64)})]]);let resolveBody,replaced=[],calls=0;const domEvents={};
const element=()=>({append(){},prepend(){},replaceChildren(){}});const main=element();
const document={cookie:'csrftoken=qa',body:{dataset:{recordar:'1'},replaceChildren:(...xs)=>replaced.push(xs)},createElement:element,getElementById:()=>null,querySelector:()=>main,addEventListener:(n,f)=>domEvents[n]=f,dispatchEvent(){}};
const ctx={document,URL,Uint8Array,console,FormData:class{get(){return 'csrf';}},crypto:require('node:crypto').webcrypto,sessionStorage:{getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v),removeItem:k=>storage.delete(k)},
 location:{pathname:'/portal/',origin:'https://belnu.com.ar',href:'https://belnu.com.ar/portal/',replace(){}},addEventListener(){},setTimeout,clearTimeout,history:{replaceState(){}},CustomEvent:class{},DOMParser:class{parseFromString(){return {title:'Private',body:{childNodes:['PRIVATE_ORDER_HISTORY']},querySelectorAll:()=>[]};}},
 fetch:async(url)=>{calls++;if(url.includes('/salir/'))return {ok:true,headers:{get:()=> 'application/json'},json:async()=>({ok:true})};return {ok:true,status:200,url:'https://belnu.com.ar/portal/pedidos/',headers:{get:()=> 'text/html'},text:()=>new Promise(r=>resolveBody=r)};}};ctx.window=ctx;vm.createContext(ctx);vm.runInContext(fs.readFileSync(path.join(__dirname,'static/midistri_portal/sesion.js'),'utf8'),ctx);
const load=ctx.MidistriTab.load('/portal/pedidos/');await new Promise(r=>setTimeout(r,5));
if(process.argv.includes('--logout-busy')){domEvents.submit({target:{action:'https://belnu.com.ar/portal/salir/',method:'post',dataset:{}},preventDefault(){}});await new Promise(r=>setTimeout(r,5));assert.equal(calls,2,'logout must run while navigation is busy');}else ctx.MidistriTab.clear();
resolveBody('PRIVATE_ORDER_HISTORY');await load;
assert.ok(!JSON.stringify(replaced).includes('PRIVATE_ORDER_HISTORY'),'late private response must not repaint after logout');
console.log('Pending private HTML discarded after device/tab clear: OK');
})().catch(e=>{console.error(e);process.exitCode=1;});
