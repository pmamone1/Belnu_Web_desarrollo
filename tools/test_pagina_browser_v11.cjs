const {chromium}=require('playwright');
const path=require('node:path');
const fs=require('node:fs');
const assert=require('node:assert/strict');
let browser;
(async()=>{
 const root=path.resolve(__dirname,'..');
 browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const context=await browser.newContext({viewport:{width:1280,height:900}});
 const errors=[];
 const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
 await page.route('https://**/*',r=>r.request().url().startsWith('https://foto.invalid/')?r.fulfill({contentType:'image/svg+xml',body:'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="450"><rect width="800" height="450" fill="#dae7e7"/><rect x="320" y="80" width="160" height="280" rx="35" fill="#2d6972"/><text x="400" y="410" text-anchor="middle" font-size="30" fill="#173e4b">Producto de ejemplo</text></svg>'}):r.abort());
 function file(layout){return 'file:///'+path.join(root,'tmp/qa_v11',layout+'.html').replace(/\\/g,'/');}
 await page.goto(file('promociones'));
 const banner=page.locator('[data-banner]').first();
 assert.equal(await banner.locator('[data-slide]:visible').getAttribute('aria-label'),'1 de 3');
 await page.waitForTimeout(3300);
 assert.equal(await banner.locator('[data-slide]:visible').getAttribute('aria-label'),'2 de 3');
 await banner.focus();const frozen=await banner.locator('[data-slide]:visible').getAttribute('aria-label');
 await page.waitForTimeout(3300);
 assert.equal(await banner.locator('[data-slide]:visible').getAttribute('aria-label'),frozen);
 await banner.press('ArrowRight');
 assert.equal(await banner.locator('[data-banner-pausa]').textContent(),'Reanudar');
 assert.equal(await page.locator('[data-banner]').nth(1).locator('[data-banner-next]').count(),0);
 await page.evaluate(()=>{document.body.replaceChildren(...new DOMParser().parseFromString(document.body.innerHTML,'text/html').body.childNodes);document.dispatchEvent(new CustomEvent('midistri:render'));});
 await page.locator('[data-banner-next]').first().click();
 assert.equal(await page.locator('[data-banner]').first().locator('[data-slide]:visible').getAttribute('aria-label'),'2 de 3','banner after seller navigation');
 await page.emulateMedia({reducedMotion:'reduce'});await page.reload();
 assert.equal(await page.locator('[data-banner-pausa]').first().textContent(),'Reanudar');
 for(const layout of ['compacto','fotos','promociones','lista']){
   await page.goto(file(layout));await page.screenshot({path:path.join(root,'tmp/qa_v11',layout+'-pc.png'),fullPage:true});
   await page.setViewportSize({width:390,height:844});
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),true,'overflow '+layout);
   await page.screenshot({path:path.join(root,'tmp/qa_v11',layout+'-movil.png'),fullPage:true});
   await page.setViewportSize({width:1280,height:900});
 }
 assert.deepEqual(errors,[]);
 await browser.close();
 console.log('Chrome QA OK: rotation, focus, keyboard, reduced motion, single image, four PC/mobile layouts; no remote network.');
})().catch(async e=>{console.error(e);if(browser)await browser.close();process.exit(1);});
