'use strict';
const {readFileSync} = require('node:fs');
const {join} = require('node:path');
const vm = require('node:vm');
const {test} = require('node:test');
const assert = require('node:assert/strict');

const raiz = join(__dirname, '..', 'midistri_portal', 'static', 'midistri_portal');

function nodo() {
    return {
        dataset: {}, attrs: {}, childNodes: [], isConnected: false, hidden: false,
        setAttribute(nombre, valor) {this.attrs[nombre] = valor;},
        append(...nodos) {this.childNodes.push(...nodos); nodos.forEach(h => h.isConnected = true);},
        replaceChildren(...nodos) {
            this.childNodes.forEach(h => h.isConnected = false);
            this.childNodes = [];
            this.append(...nodos);
        },
        prepend(hijo) {this.childNodes.unshift(hijo);},
    };
}

function portal() {
    const body = nodo();
    let main = nodo();
    body.append(main);
    const eventos = new Map();
    const historial = [];
    const peticiones = [];
    const location = new URL('https://midistri.test/portal/');
    const document = {
        body,
        querySelector: sel => sel === 'main' ? main : null,
        getElementById: id => body.childNodes.find(hijo => hijo.id === id),
        createElement: nodo,
        addEventListener(tipo, listener) {
            eventos.set(tipo, [...(eventos.get(tipo) || []), listener]);
        },
        dispatchEvent(evento) {(eventos.get(evento.type) || []).forEach(listener => listener(evento));},
    };
    const sandbox = {
        document, location, URL, AbortController, setTimeout, clearTimeout,
        addEventListener() {}, scrollTo() {},
        sessionStorage: {getItem: () => null},
        CustomEvent: class {constructor(type) {this.type = type;}},
        history: {
            pushState(_, __, url) {historial.push(url); location.href = url;},
            replaceState(_, __, url) {location.href = url;},
        },
        fetch(url, {signal}) {
            return new Promise((resolver, rechazar) => {
                peticiones.push({url, signal, resolver});
                signal.addEventListener('abort', () => rechazar(new Error('Abortada')), {once: true});
            });
        },
        DOMParser: class {
            parseFromString(titulo) {
                const contenido = nodo();
                const pagina = {
                    title: titulo, body: {...nodo(), childNodes: [contenido]},
                    querySelector: selector => selector === 'main' ? contenido : null,
                    querySelectorAll: () => [],
                };
                if (titulo !== 'Error') main = contenido;
                return pagina;
            }
        },
    };
    sandbox.window = sandbox;
    vm.createContext(sandbox);
    for (const archivo of ['progreso.js', 'sesion.js']) {
        vm.runInContext(readFileSync(join(raiz, archivo), 'utf8'), sandbox, {filename: archivo});
    }
    function tocar(ruta) {
        const href = new URL(ruta, location).href;
        const enlace = {href, target: '', hasAttribute: () => false};
        let interceptado = false;
        document.dispatchEvent({type: 'click', button: 0,
            target: {closest: selector => selector === 'a[href]' ? enlace : null},
            preventDefault() {this.defaultPrevented = true; interceptado = true;}});
        assert.ok(interceptado);
    }
    function responder(indice, titulo, correcto = true) {
        const {url, resolver} = peticiones[indice];
        resolver({url, ok: correcto, headers: {get: () => 'text/html'}, text: async () => titulo});
        return new Promise(continuar => setImmediate(continuar));
    }
    return {tocar, responder, peticiones, document, historial, progreso: () => document.getElementById('midistri-progreso')};
}

test('una consulta muestra progreso y deja la misma página al fallar', async () => {
    const {tocar, responder, document, historial, progreso} = portal();
    const anterior = document.querySelector('main');
    tocar('/portal/remitos/');
    assert.equal(progreso().hidden, false);
    assert.equal(progreso().childNodes[1].textContent, 'Cargando remitos…');
    assert.equal(anterior.attrs['aria-busy'], 'true');
    await responder(0, 'Error', false);
    assert.equal(progreso().hidden, true);
    assert.equal(anterior.attrs['aria-busy'], 'false');
    assert.equal(document.querySelector('main'), anterior);
    assert.match(anterior.childNodes[0].textContent, /No pudimos cargar la consulta/);
    assert.deepEqual(historial, []);
});

test('la consulta más reciente reemplaza la anterior sin recargar el documento', async () => {
    const {tocar, responder, peticiones, document, historial, progreso} = portal();
    const body = document.body;
    tocar('/portal/remitos/');
    tocar('/portal/estado-cuenta/');
    assert.equal(peticiones[0].signal.aborted, true);
    assert.equal(progreso().childNodes[1].textContent, 'Cargando estado de cuenta…');
    await responder(1, 'Mi estado de cuenta');
    assert.equal(document.body, body);
    assert.equal(document.title, 'Mi estado de cuenta');
    assert.equal(progreso().hidden, true);
    assert.deepEqual(historial, ['https://midistri.test/portal/estado-cuenta/']);
});
