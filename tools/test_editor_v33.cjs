const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {createRequire}=require('node:module'),deps=createRequire('C:/Users/pmamo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/package.json');
const {chromium}=deps('playwright'),out=path.join(__dirname,'../tmp/qa_editor33');
(async()=>{const browser=await chromium.launch({headless:true});try{
const page=await browser.newPage({viewport:{width:1440,height:1050}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.goto('http://127.0.0.1:63433/portal/administrar/pagina/');await page.getByText('Borrador listo · cambios sin publicar').waitFor();
await page.getByRole('button',{name:/Bloque «Promoción retirada»/}).click();assert.equal(await page.locator('#editor-seleccion').inputValue(),'retirado');
await page.getByRole('button',{name:'Eliminar bloque',exact:true}).click();assert.equal(await page.locator('#editor-bloques').getByRole('button',{name:'Promoción retirada',exact:true}).count(),0);
await page.getByRole('button',{name:'↶ Deshacer'}).click();await page.locator('#editor-bloques').getByRole('button',{name:'Promoción retirada',exact:true}).waitFor();
await page.getByRole('button',{name:'↷ Rehacer'}).click();assert.equal(await page.locator('#editor-bloques').getByRole('button',{name:'Promoción retirada',exact:true}).count(),0);
await page.getByLabel('Título del sitio · Tamaño de letra',{exact:true}).fill('40');await page.getByLabel('Título del sitio · Tipo de letra',{exact:true}).selectOption('georgia');
await page.getByLabel('Subtítulo · Tamaño de letra',{exact:true}).fill('16');
await page.waitForFunction(()=>document.querySelector('#editor-preview').contentDocument.querySelector('[data-mensaje="titulo"]').style.fontSize==='40px');
assert.equal(await page.locator('#editor-preview').evaluate(f=>f.contentDocument.querySelector('[data-mensaje="subtitulo"]').style.fontSize),'16px');
assert.equal(await page.locator('#editor-preview').evaluate(f=>f.contentDocument.querySelector('header').textContent.includes('Acceso Distribuidor')),false);
await page.locator('#editor-seleccion').selectOption('catalogo');assert.equal(await page.getByRole('button',{name:'Eliminar bloque',exact:true}).isDisabled(),true);
await page.screenshot({path:path.join(out,'editor-pc.png'),fullPage:false});
for(const width of [1440,390,320]){await page.setViewportSize({width,height:900});await page.goto('http://127.0.0.1:63433/portal/pedidos/');
const button=page.locator('[data-pedido-toggle]').nth(1);assert.equal(await button.getAttribute('aria-expanded'),'false');await button.click();assert.equal(await button.getAttribute('aria-expanded'),'true');
const panel=page.locator('#pedido-00000000-0000-0000-0000-000000000002');assert.equal(await panel.isVisible(),true);await panel.getByText('SKU: T1',{exact:true}).waitFor();
assert.deepEqual(await panel.locator('.pedido-productos tbody tr td').allTextContents(),['TermoSKU: T1','10','6','4']);
assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true);
await page.screenshot({path:path.join(out,'pedidos-'+width+'.png'),fullPage:true});await button.click();assert.equal(await panel.isVisible(),false);
}
assert.deepEqual(errors,[]);console.log('UI_OK: eliminar/deshacer/rehacer, catálogo protegido, estilos independientes, aviso retirado, tabla y despliegue PC/390/320; sin errores JS.');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exit(1);});
