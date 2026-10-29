const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const file=path.join(__dirname,'static/midistri_portal/analitica.js');assert.ok(fs.existsSync(file),'Falta captura JS');
async function run(){
 let context={firma:'signed',actor:'vendor1'},requests=[],timers=[],store={},uuid=0,offline=false;
 const handlers={};const document={querySelector:(s)=>s==='#analitica-contexto'?{textContent:JSON.stringify(context)}:s==='[name=csrfmiddlewaretoken]'?{value:'csrf'}:null,addEventListener:(n,f)=>{handlers[n]=f;}};
 const window={addEventListener:(n,f)=>{handlers[n]=f;},MidistriTab:{request:async(url,opts)=>{requests.push({url,body:opts.body});if(offline)throw Error('offline');return {ok:true,status:200,json:async()=>({})};}}};
 const sandbox={window,document,sessionStorage:{getItem:k=>store[k]||null,setItem:(k,v)=>{store[k]=v;}},crypto:{randomUUID:()=>String(++uuid).padStart(8,'0')+'-0000-4000-8000-000000000000'},setTimeout:f=>{timers.push(f);return timers.length;},clearTimeout:()=>{},fetch:()=>{throw Error('No debe usar fetch directo si hay sesión de pestaña');},console};
 vm.runInNewContext(fs.readFileSync(file,'utf8'),sandbox);
 for(let i=0;i<25;i++)window.MidistriAnalytics.emit({tipo:'foto_ampliada',producto:1,recurso:0});
 while(timers.length)await timers.shift()();
 assert.equal(requests.length,2);assert.equal(JSON.parse(requests[0].body).eventos.length,20);assert.equal(JSON.parse(requests[1].body).eventos.length,5);
 requests=[];offline=true;window.MidistriAnalytics.emit({tipo:'producto_consulta',producto:2});while(timers.length)await timers.shift()();
 assert.equal(requests.length,3,'Reintento acotado a3');assert.deepEqual(requests.map(r=>JSON.parse(r.body).eventos[0].id),Array(3).fill(JSON.parse(requests[0].body).eventos[0].id));
 offline=false;context={firma:'new',actor:'vendor2'};handlers['midistri:render']();requests=[];while(timers.length)await timers.shift()();
 assert.equal(requests.length,0,'No enviar la cola de otro vendedor');
 context=null;handlers['midistri:render']();window.MidistriAnalytics.emit({tipo:'producto_consulta',producto:3});while(timers.length)await timers.shift()();assert.equal(requests.length,0);
 console.log('OK: lotes20/5, reintentos únicos/acotados, actor y anónimo aislados');
}
run().catch(e=>{console.error(e);process.exitCode=1;});
