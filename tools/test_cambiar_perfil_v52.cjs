const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');

const portal = 'http://127.0.0.1:63405';
const acceso = portal + '/portal/acceso/?perfiles=1';
const profiles = [
    {seleccion: 'perfil-a', nombre: 'Kiosco A', distribuidora: 'Distribuidora A'},
    {seleccion: 'perfil-b', nombre: 'Kiosco B', distribuidora: 'Distribuidora B'},
];
const assets = path.resolve(__dirname, '../midistri_portal/static/midistri_portal');

async function verify(browser, identities, remembered, width = 390) {
    const page = await browser.newPage({viewport: {width, height: 820}});
    const calls = [];
    let current = identities[0];
    const html = (content) => '<!doctype html><body data-recordar="1" data-recordar-presente="' +
        (remembered ? '1' : '0') + '">' + content +
        '<form hidden id="midistri-recordado-csrf"><input name="csrfmiddlewaretoken" value="token-de-prueba"></form>' +
        '<script src="/static/sesion.js" defer></script><script src="/static/recordado.js" defer></script></body>';
    try {
        await page.route(portal + '/**', async (route) => {
            const request = route.request();
            const url = new URL(request.url());
            if (url.pathname.startsWith('/static/')) {
                const file = path.basename(url.pathname);
                assert.ok(['recordado.js', 'sesion.js'].includes(file));
                return route.fulfill({contentType: 'application/javascript', body: fs.readFileSync(path.join(assets, file))});
            }
            if (url.pathname.endsWith('/recordado/')) {
                const body = request.postData();
                calls.push(body);
                if (body.includes('perfil-b')) current = identities[1];
                const data = body.includes('elegir') && !body.includes('seleccion')
                    ? {fase: 'elegir', identidades: identities} : {fase: 'dentro', url: '/portal/'};
                return route.fulfill({json: data});
            }
            const content = url.pathname === '/portal/'
                ? '<header>Hola, ' + current.nombre + '</header><main><a href="' + acceso + '">Cambiar perfil</a></main>'
                : '<main><label>Email <input name="email"></label></main>';
            return route.fulfill({contentType: 'text/html', body: html(content)});
        });
        await page.goto(portal + '/portal/');
        if (!remembered) await page.evaluate(() => window.MidistriTab.proof(true));
        await page.getByRole('link', {name: 'Cambiar perfil'}).click();
        if (!remembered) {
            await page.getByRole('textbox', {name: 'Email'}).waitFor();
            assert.equal(calls.length, 0);
            return;
        }
        await page.getByRole('heading', {name: 'Cambiar perfil'}).waitFor();
        assert.match(calls.at(-1), /token-de-prueba/);
        assert.equal(await page.getByRole('option').count(), identities.length);
        if (identities.length === 1) {
            await page.getByText('Hay un solo perfil recordado.', {exact: false}).waitFor();
            await page.getByRole('link', {name: 'Verificar mi Email'}).click();
            await page.getByRole('textbox', {name: 'Email'}).waitFor();
            assert.match(page.url(), /otro=1/);
            return;
        }
        await page.getByRole('combobox', {name: 'Kiosco'}).selectOption('perfil-b');
        await page.getByRole('button', {name: 'Continuar'}).click();
        await page.getByText('Hola, Kiosco B').waitFor();
        assert.match(calls.at(-1), /perfil-b/);
        assert.equal(page.url(), portal + '/portal/');
    } finally {
        await page.close();
    }
}

(async () => {
    const browser = await chromium.launch({headless: true, executablePath: process.env.MIDISTRI_QA_CHROMIUM || undefined});
    try {
        await verify(browser, profiles, true);
        await verify(browser, profiles, true, 1440);
        await verify(browser, profiles.slice(0, 1), true);
        await verify(browser, profiles, false);
        console.log('Cambio de kiosco y verificación de Email correctos en navegador a 390 y 1440 px.');
    } finally {
        await browser.close();
    }
})().catch(error => {
    console.error(error);
    process.exitCode = 1;
});
