const {chromium}=require('playwright');
const path=require('node:path'),assert=require('node:assert/strict');
let browser;
(async()=>{
 const root=path.resolve(__dirname,'..');
 browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.route('https://**/*',r=>r.request().url().startsWith('https://foto.invalid/')?r.fulfill({contentType:'image/svg+xml',body:'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800"><rect width="1200" height="800" fill="#e7eee7"/><rect x="440" y="100" width="320" height="510" rx="50" fill="#237861"/><text x="600" y="720" text-anchor="middle" font-size="45" fill="#174d3e">Novedades para tu kiosco</text></svg>'}):r.abort());
 const file=l=>'file:///'+path.join(root,'tmp/qa_v12',l+'.html').replace(/\\/g,'/');
 for(const layout of ['compacto','fotos','promociones','lista','anterior']){
  await page.goto(file(layout));await page.emulateMedia({reducedMotion:'reduce'});
  for(const width of [1440,390]){
   await page.setViewportSize({width,height:1000});
   const box=await page.locator('[data-banner]').first().boundingBox();
   assert(box,'banner in '+layout);
   assert(Math.abs(box.width-width)<=2,'full width '+layout+' '+width+' got '+box.width);
   assert(Math.abs(box.x)<=2,'left edge '+layout);
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'no overflow '+layout);
   const image=await page.locator('[data-banner] [data-slide]:not([hidden]) img').first().boundingBox();
   assert(image.height>=(width===390?300:480),'large image '+layout);
   await page.screenshot({path:path.join(root,'tmp/qa_v12',layout+'-'+width+'.png'),fullPage:true});
  }
 }
 await page.setViewportSize({width:1440,height:1000});await page.goto(file('preview'));
 const preview=await page.locator('[data-banner]').first().boundingBox();
 assert(preview.width<=430,'preview stays mobile width');
 assert.equal(await page.locator('[data-banner]').nth(1).locator('button').count(),0,'single photo no navigation');
 assert.deepEqual(errors,[]);
 await browser.close();console.log('Panorama QA OK: four layouts, previous page, mobile preview, large photos, no overflow.');
})().catch(async e=>{console.error(e);if(browser)await browser.close();process.exit(1);});
