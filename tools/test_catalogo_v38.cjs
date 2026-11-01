const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { createRequire } = require('node:module');
const deps = createRequire('C:/Users/pmamo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/package.json');
const base = 'http://127.0.0.1:63737/portal/?distribuidora=20';
const out = path.join(__dirname, '../tmp/qa_catalogo38');
(async () => {
  fs.mkdirSync(out, { recursive: true });
  const browser = await deps('playwright').chromium.launch({ headless: true });
  const failures = [];
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' });
    await context.route('https://example.test/**', r => r.fulfill({ contentType: 'image/svg+xml', body: '<svg xmlns="http://www.w3.org/2000/svg" width="60" height="60"/>' }));
    await context.addInitScript(() => {
      window.catalogoMediaActive = 0;
      const native = window.matchMedia.bind(window);
      window.matchMedia = query => {
        const m = native(query);
        if (query !== '(max-width:1023px)') return m;
        const add = m.addEventListener.bind(m), remove = m.removeEventListener.bind(m);
        m.addEventListener = (event, fn, ...args) => { if (event === 'change') window.catalogoMediaActive++; return add(event, fn, ...args); };
        m.removeEventListener = (event, fn, ...args) => { if (event === 'change') window.catalogoMediaActive--; return remove(event, fn, ...args); };
        return m;
      };
    });
    const p = await context.newPage();
    const errors = []; p.on('pageerror', e => errors.push(e.message));
    async function check(name, fn) { try { await fn(); console.log('PASS', name); } catch (e) { failures.push(name + ': ' + e.message); console.error('FAIL', name, e.message); } }
    await p.goto(base);
    await check('lateral largo completo sobre carrito y resize', async () => {
      await p.evaluate(() => {
        const promos = document.querySelector('.catalogo-promociones');
        for (let i = 0; i < 8; i++) { const s = document.createElement('section'); s.innerHTML = '<h2>Promoción sintética ' + i + '</h2><p>Contenido largo de prueba</p><a class="button" href="#prueba">Último control ' + i + '</a>'; promos.append(s); }
      });
      for (const [width, height, padding] of [[1440,900,14],[1280,720,35],[1100,640,24]]) {
        await p.setViewportSize({ width, height });
        await p.locator('.sticky').evaluate((e, v) => { e.style.paddingTop = v + 'px'; e.style.paddingBottom = v + 'px'; }, padding);
        await p.locator('.catalogo-grid').evaluate(e => window.scrollTo(0, e.getBoundingClientRect().top + scrollY + 150));
        await p.waitForTimeout(80);
        await p.locator('.catalogo-lateral').evaluate(e => { e.scrollTop = e.scrollHeight; });
        await p.waitForTimeout(80);
        const geometry = await p.evaluate(() => {
          const side = document.querySelector('.catalogo-lateral'), last = side.querySelector('.catalogo-promociones section:last-child a'), r = last.getBoundingClientRect(), bar = document.querySelector('.sticky').getBoundingClientRect();
          return { width: innerWidth, height: innerHeight, side: side.getBoundingClientRect().toJSON(), last: r.toJSON(), bar: bar.toJSON(), hit: document.elementFromPoint(r.x + r.width/2, r.bottom - 1) === last };
        });
        fs.writeFileSync(path.join(out, `geometry-${width}.json`), JSON.stringify(geometry, null, 2));
        await p.screenshot({ path: path.join(out, `lateral-${width}-${process.env.QA_PHASE || 'green'}.png`) });
        assert.ok(geometry.side.bottom <= geometry.bar.top, "todo el lateral sobre la barra: " + JSON.stringify(geometry));
        assert.ok(geometry.last.bottom <= geometry.bar.top, JSON.stringify(geometry));
        assert.ok(geometry.hit, 'borde inferior del último botón clickeable');
      }
    });
    await p.setViewportSize({ width: 390, height: 900 });
    await p.goto(base);
    await check('panel nuevo móvil cerrado tras navegación real de sesión', async () => {
      for (let i = 0; i < 5; i++) {
        await p.locator('[data-catalogo-panel] summary').click();
        assert.equal(await p.locator('[data-catalogo-panel]').getAttribute('open'), '');
        const old = await p.locator('[data-catalogo-panel]').elementHandle();
        await p.evaluate(url => window.MidistriTab.load(url), base + '&q=Producto&page=' + (i % 2 + 1));
        await p.waitForFunction(e => !e.isConnected, old);
        assert.equal(await p.locator('[data-catalogo-panel]').getAttribute('open'), null, 'panel nuevo cerrado');
      }
    });
    await check('render repetido idempotente conserva elección sin listeners acumulados', async () => {
      await p.goto(base);
      await p.locator('[data-catalogo-panel] summary').click();
      await p.evaluate(() => { for (let i=0; i<5; i++) document.dispatchEvent(new CustomEvent('midistri:render')); });
      assert.equal(await p.locator('[data-catalogo-panel]').getAttribute('open'), '', 'conserva apertura manual');
      for(let i=0;i<5;i++) { const old=await p.locator('[data-catalogo-panel]').elementHandle(); await p.evaluate(url=>window.MidistriTab.load(url),base+'&page='+(i%2+1)); await p.waitForFunction(e=>!e.isConnected,old); }
      assert.equal(await p.evaluate(() => window.catalogoMediaActive), 1, 'sólo un listener de breakpoint activo');
      await p.setViewportSize({ width: 1440, height: 900 });
      await p.waitForTimeout(80);
      assert.equal(await p.locator('[data-catalogo-panel]').getAttribute('open'), '');
      await p.setViewportSize({ width: 390, height: 900 });
      await p.waitForTimeout(80);
      assert.equal(await p.locator('[data-catalogo-panel]').getAttribute('open'), null, 'responde al breakpoint después de navegación');
      await p.screenshot({ path: path.join(out, `sesion-movil-${process.env.QA_PHASE || 'green'}.png`) });
      await p.setViewportSize({ width: 1440, height: 900 });
      await p.evaluate(url=>window.MidistriTab.load(url),base);
      await p.waitForTimeout(120);
      assert.equal(await p.locator('[data-catalogo-panel]').getAttribute('open'), '');
      await p.screenshot({ path: path.join(out, `sesion-desktop-${process.env.QA_PHASE || 'green'}.png`) });
    });
    assert.deepEqual(errors, []);
    await context.close();
  } finally { await browser.close(); }
  assert.deepEqual(failures, []);
  console.log('CATALOGO_V38_OK: long sidebar, cart height/resize, real session navigation, manual toggle, idempotence and one active breakpoint listener');
})().catch(e => { console.error(e); process.exit(1); });
