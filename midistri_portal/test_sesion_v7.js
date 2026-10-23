/* Offline logout: keep only a pending revocation, never restore active identity. */
const assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),path=require('node:path');
(async()=>{
const values=new Map(),events={},domEvents={};let online=false,calls=[],replaced=[];
const proof={id:'12345678-1234-4321-abcd-123456789012',proof:'a'.repeat(64)};
values.set('midistri.tab.v1',JSON.stringify(proof));
const element=()=>({append(){},prepend(){},replaceChildren(){},classList:{add(){}}});
const notice=element();notice.textContent='';
const document={cookie:'csrftoken=synthetic',getElementById:()=>notice,createElement:element,body:element(),
querySelector:()=>element(),addEventListener:(n,f)=>domEvents[n]=f};
const context={document,URL,Uint8Array,FormData:class {constructor(){ }set(){}},crypto:require('node:crypto').webcrypto,
sessionStorage:{getItem:k=>values.get(k)||null,setItem:(k,v)=>values.set(k,v),removeItem:k=>values.delete(k)},
location:{pathname:'/portal/acceso/',origin:'https://belnu.com.ar',href:'https://belnu.com.ar/portal/acceso/',replace:u=>replaced.push(u)},
addEventListener:(n,f)=>events[n]=f,setTimeout,clearTimeout,history:{},CustomEvent:class{},console,
fetch:async(url,options)=>{calls.push({url,options});if(!online)throw Error('offline');return {ok:true,status:200,headers:{get:()=> 'application/json'},json:async()=>({ok:true,url:'/portal/'})};}};
context.window=context;vm.createContext(context);
vm.runInContext(fs.readFileSync(path.join(__dirname,'static/midistri_portal/sesion.js'),'utf8'),context);
const form={action:'https://belnu.com.ar/portal/salir/',method:'post',dataset:{}};
domEvents.submit({target:form,preventDefault(){}});
await new Promise(r=>setTimeout(r,10));
assert.equal(values.has('midistri.tab.v1'),false);
assert.equal(values.has('midistri.logout.pending.v1'),true,'must preserve pending revocation');
online=true;assert.equal(typeof events.online,'function');events.online();
await new Promise(r=>setTimeout(r,10));
assert.equal(values.has('midistri.logout.pending.v1'),false);
assert.equal(values.has('midistri.tab.v1'),false);
assert.equal(calls.at(-1).options.headers['X-Midistri-Tab-Proof'],proof.proof);
console.log('Offline logout and online revocation: OK');
})().catch(e=>{console.error(e);process.exitCode=1;});
