const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {createRequire}=require('node:module'),deps=createRequire('C:/Users/pmamo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/package.json');
const {chromium}=deps('playwright'),out=path.join(__dirname,'../tmp/qa_navegacion31');
(async()=>{const browser=await chromium.launch({headless:true});try{
for(const width of [1440,390,320]){const p=await browser.newPage({viewport:{width,height:850}});await p.route('**/*',r=>r.abort());
for(const n of [1,2,12]){await p.setContent(fs.readFileSync(path.join(out,'pagina'+n+'.html'),'utf8'));
assert.equal(await p.locator('header form.logout').count(),0,'header must not show logout');
assert.equal(await p.getByRole('link',{name:'Cambiar perfil',exact:true}).count(),1);
const nav=p.getByRole('navigation',{name:'Páginas del catálogo',exact:true});assert.equal(await nav.count(),1);
await nav.scrollIntoViewIfNeeded();const m=await nav.evaluate(el=>({width:el.getBoundingClientRect().width,overflow:document.documentElement.scrollWidth>innerWidth,
 links:[...el.querySelectorAll('a')].map(a=>({height:a.getBoundingClientRect().height,font:parseFloat(getComputedStyle(a).fontSize),href:a.getAttribute('href')}))}));
assert.equal(m.overflow,false,'no horizontal overflow at '+width+' page '+n+' '+JSON.stringify(m));assert.equal(m.links.length,n===2?2:1);
for(const link of m.links){assert.ok(link.height>=48);if(width===1440)assert.ok(link.font>=18);
const u=new URL(link.href,'https://local.test/portal/');assert.equal(u.searchParams.get('q'),'coní & chocolate');assert.equal(u.searchParams.get('categoria'),'Alimentos y Bebidas');assert.equal(u.searchParams.get('orden'),'precio_desc');}
await p.screenshot({path:path.join(out,'catalogo-'+width+'-p'+n+'.png')});
}await p.close();}console.log('Catalog UI OK: no logout, retained profiles, large pager, filters, pages1/2/12, desktop1440/mobile390/320');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
