const assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),path=require('node:path');
const source=path.join(__dirname,'static/midistri_portal/recordado.js');
assert.ok(fs.existsSync(source),'Falta bootstrap de acceso recordado');
const pause=()=>new Promise(r=>setTimeout(r,5));
function app({known=false,offline=false,result={fase:'dentro',url:'/portal/'},pending=false}={}){
 const events={},calls=[],loads=[],notices=[],writes=[],storage=new Map();let remembered=known;
 if(pending)storage.set('midistri.dispositivo.olvido.v1','1');
 const element=()=>({children:[],append(...xs){this.children.push(...xs);},prepend(...xs){this.children.unshift(...xs);},replaceChildren(...xs){this.children=xs;},addEventListener(n,f){this[n]=f;},setAttribute(){},querySelector(){return null;}});
 const main=element();
 const document={body:{dataset:{recordar:known?'1':'1',recordarPresente:known?'1':'0'}},querySelector:q=>q==='main'?main:null,getElementById:()=>null,createElement:()=>element()};
 Object.defineProperty(document,'cookie',{get(){return 'csrftoken=csrf'+(pending?'; midistri_dispositivo_olvido=1':'');},set(v){writes.push(v);if(v.startsWith('midistri_dispositivo_olvido='))pending=!v.includes('Max-Age=0');}});
 const context={document,URL,URLSearchParams,FormData:class{constructor(){this.rows=new Map();}set(k,v){this.rows.set(k,v);}get(k){return this.rows.get(k);}},
 location:{pathname:'/portal/',href:'https://belnu.com.ar/portal/',origin:'https://belnu.com.ar',search:'',replace:u=>loads.push(u)},
 localStorage:{getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v),removeItem:k=>storage.delete(k)},
 addEventListener:(n,f)=>events[n]=f,console,setTimeout,clearTimeout,
 fetch:async(url,opts)=>{calls.push(url);if(offline)throw Error('offline');return {ok:true,status:200,json:async()=>url.includes('olvidar')?{ok:true}:result};},
 MidistriTab:{proof:()=>known?{id:'tab',proof:'private-tab-only'}:null,request:async(url,opts)=>context.fetch(url,opts),load:u=>loads.push(u),clear:()=>{remembered=false;}}};
 context.window=context;vm.createContext(context);vm.runInContext(fs.readFileSync(source,'utf8'),context);
 return {context,calls,loads,writes,storage,events,main,get remembered(){return remembered;}};
}
(async()=>{
 const fresh=app();await pause();assert.equal(fresh.calls.length,0,'public visitor should not request private profiles');
 fresh.context.MidistriRecordado.markLogout();assert.ok(fresh.writes.some(x=>x.includes('midistri_dispositivo_olvido=1')&&x.includes('Max-Age=34560000')));assert.equal(fresh.storage.get('midistri.dispositivo.olvido.v1'),'1');
 assert.ok(!JSON.stringify([...fresh.storage.values()]).includes('private-tab-only'),'no credential in persistent JS storage');
 const known=app({known:true});await pause();assert.equal(known.calls[0],'/portal/acceso/recordado/');assert.equal(new URL(known.loads[0],'https://belnu.com.ar').pathname,'/portal/');
 const off=app({known:true,pending:true,offline:true});await pause();assert.equal(off.calls[0],'/portal/acceso/olvidar/');assert.ok(!off.calls.includes('/portal/acceso/recordado/'));assert.equal(off.loads.length,0);assert.equal(off.storage.get('midistri.dispositivo.olvido.v1'),'1');
 const back=app({known:true,pending:true});await pause();assert.equal(back.calls[0],'/portal/acceso/olvidar/');assert.ok(!back.calls.includes('/portal/acceso/recordado/'));assert.equal(back.storage.has('midistri.dispositivo.olvido.v1'),false);
 const retry=app({known:true,offline:true});await pause();assert.equal(retry.loads.length,0);assert.equal(retry.storage.size,0,'failed restore must not mark logged out or erase trust');
 const parallel=app();parallel.events.storage({key:'midistri.dispositivo.olvido.v1',newValue:'1'});assert.equal(parallel.remembered,false);
 console.log('Recordado: automatic restore, private visitor, offline persistent logout, retry and cross-tab invalidation OK');
})().catch(e=>{console.error(e);process.exitCode=1;});
