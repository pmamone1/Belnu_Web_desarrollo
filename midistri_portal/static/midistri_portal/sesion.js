(function(){'use strict';
if(location.pathname.startsWith('/portal/administrar/')||location.pathname.startsWith('/portal/gestion/'))return;
const KEY='midistri.tab.v1',PENDING='midistri.logout.pending.v1';let busy=false,closing=false,generation=0;
function proof(create){try{let p=JSON.parse(sessionStorage.getItem(KEY)||'null');if(p&&/^[0-9a-f-]{36}$/.test(p.id)&&/^[0-9a-f]{64}$/.test(p.proof))return p;
if(!create)return null;const a=new Uint8Array(32);crypto.getRandomValues(a);p={id:crypto.randomUUID?crypto.randomUUID():([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g,c=>(c^crypto.getRandomValues(new Uint8Array(1))[0]&15>>c/4).toString(16)),proof:Array.from(a,x=>x.toString(16).padStart(2,'0')).join('')};sessionStorage.setItem(KEY,JSON.stringify(p));return p;}catch(e){return null;}}
function headers(p){return p?{'X-Midistri-Tab':p.id,'X-Midistri-Tab-Proof':p.proof}:{};}
function notice(text){let n=document.getElementById('midistri-session-status');if(!n){n=document.createElement('p');n.id='midistri-session-status';n.className='notice';n.role='status';document.querySelector('main').prepend(n);}n.textContent=text;}
async function raw(url,options,p){return fetch(url,Object.assign({credentials:'same-origin',redirect:'follow'},options,{headers:Object.assign({},options&&options.headers,headers(p))}));}
function cleared(){const visor=document.querySelector('[data-remito-visor][open]');if(visor)visor.close();const main=document.createElement('main');const p=document.createElement('p');p.textContent='Cerraste el acceso en esta pestaña.';main.append(p);const a=document.createElement('a');a.href='/portal/';a.textContent='Volver al portal';main.append(a);document.body.replaceChildren(main);}
function pending(){try{return JSON.parse(sessionStorage.getItem(PENDING)||'null');}catch(e){return null;}}
function retryNotice(){notice('Cerraste el acceso en esta pestaña. Falta confirmar el cierre remoto. Se reintentará al volver la conexión.');const b=document.createElement('button');b.type='button';b.textContent='Reintentar cierre remoto';b.onclick=retryLogout;document.querySelector('main').append(b);}
async function retryLogout(){const item=pending();if(!item||closing)return;closing=true;try{
const data=new FormData();const cookie=document.cookie.split('; ').find(x=>x.startsWith('csrftoken='));data.set('csrfmiddlewaretoken',cookie?decodeURIComponent(cookie.slice(10)):item.csrf);
const r=await raw('/portal/salir/',{method:'POST',body:data,headers:{Accept:'application/json'}},item.proof);
if(!r.ok)throw Error('pending');sessionStorage.removeItem(PENDING);if(window.MidistriRecordado)MidistriRecordado.completeLogout();notice('Cierre remoto confirmado.');
}catch(e){retryNotice();}finally{closing=false;}}
const codigo = document.body.dataset.midistriCodigo === '1';
let lecturaActual = null;

function esPortal(destino) {
    const url = new URL(destino, location.href);
    return url.origin === location.origin && url.pathname.startsWith('/portal/') &&
        !url.pathname.startsWith('/portal/administrar/') && !url.pathname.startsWith('/portal/gestion/') &&
        !url.pathname.startsWith('/portal/activar/');
}

function plazoLectura() {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 45000);
    return {signal: controller.signal, cancelar: () => controller.abort(), cerrar: () => clearTimeout(timer)};
}

function mensajeCarga(url, opciones) {
    const ruta = new URL(url, location.href).pathname;
    if (ruta === '/portal/estado-cuenta/') return 'Cargando estado de cuenta…';
    if (ruta === '/portal/remitos/') return 'Cargando remitos…';
    if (ruta === '/portal/pedidos/') return 'Cargando pedidos…';
    if (ruta === '/portal/carrito/') return 'Cargando carrito…';
    if (opciones && opciones.method === 'POST') return ruta === '/portal/enviar/' ? 'Enviando pedido…' : 'Procesando…';
    return 'Cargando…';
}

function actualizarPagina(pagina, url, reemplazar) {
    const visor = document.querySelector('[data-remito-visor][open]');
    if (visor) visor.close();
    pagina.querySelectorAll('script:not([type="application/json"])').forEach(script => script.remove());
    document.title = pagina.title;
    document.body.dataset.recordar = pagina.body.dataset.recordar || '0';
    document.body.dataset.recordarPresente = pagina.body.dataset.recordarPresente || '0';
    document.body.dataset.tema = pagina.body.dataset.tema || 'claro';
    document.body.replaceChildren(...pagina.body.childNodes);
    if (reemplazar || location.href === url) history.replaceState({}, '', url);
    else history.pushState({}, '', url);
    document.dispatchEvent(new CustomEvent('midistri:render'));
    if (!reemplazar) {
        const titulo = document.querySelector('main h2, main h3');
        if (titulo) {
            titulo.tabIndex = -1;
            titulo.focus({preventScroll: true});
        }
        window.scrollTo(0, 0);
    }
}

async function navigate(url, opciones, logout, reemplazar) {
    const acceso = codigo ? proof(false) : null;
    const lectura = !opciones || !opciones.method || opciones.method === 'GET';
    if (busy && !logout && !(lectura && lecturaActual)) return;
    const version = ++generation;
    if (lecturaActual) lecturaActual.cancelar();
    const cancelacion = lectura ? plazoLectura() : null;
    lecturaActual = cancelacion;
    busy = true;
    const finalizar = MidistriProgreso.iniciar(mensajeCarga(url, opciones));
    let mostrarInicio = false;
    let comprobarPerfil = false;
    if (logout) {
        if (window.MidistriRecordado) MidistriRecordado.markLogout();
        sessionStorage.setItem(PENDING, JSON.stringify({proof: acceso, csrf: opciones.body.get('csrfmiddlewaretoken') || ''}));
        sessionStorage.removeItem(KEY);
        cleared();
        opciones = {...opciones, headers: {Accept: 'application/json'}};
    }
    try {
        const respuesta = await raw(url, cancelacion ? {...opciones, signal: cancelacion.signal} : opciones, acceso);
        if (version !== generation) return;
        const tipo = respuesta.headers.get('Content-Type') || '';
        if (tipo.includes('application/json')) {
            const datos = await respuesta.json();
            if (version !== generation) return;
            if (logout) {
                if (!respuesta.ok) { retryNotice(); return; }
                sessionStorage.removeItem(PENDING);
                if (window.MidistriRecordado) MidistriRecordado.completeLogout();
                mostrarInicio = true;
            } else if (!respuesta.ok) {
                if (respuesta.status === 403) sessionStorage.removeItem(KEY);
                notice(datos.error || 'No pudimos completar la operación.');
            }
            return;
        }
        if (tipo.includes('application/pdf') && respuesta.ok) {
            const contenido = await respuesta.blob();
            if (version !== generation) return;
            const blob = URL.createObjectURL(contenido);
            const enlace = document.createElement('a');
            enlace.href = blob;
            enlace.download = 'remitos_pedido.pdf';
            enlace.click();
            setTimeout(() => URL.revokeObjectURL(blob), 60000);
            return;
        }
        if (respuesta.redirected && !esPortal(respuesta.url)) {
            const destino = new URL(respuesta.url);
            if (destino.origin === location.origin) location.assign(destino.href);
            else throw Error('destino');
            return;
        }
        if (!tipo.includes('text/html')) throw Error('respuesta');
        const html = await respuesta.text();
        if (version !== generation) return;
        const pagina = new DOMParser().parseFromString(html, 'text/html');
        if (!respuesta.ok) {
            const aviso = pagina.querySelector('main [role="alert"]');
            if (aviso) { notice(aviso.textContent.trim()); return; }
            throw Error('respuesta');
        }
        if (!pagina.querySelector('main') || !esPortal(respuesta.url)) throw Error('página');
        actualizarPagina(pagina, respuesta.url, reemplazar);
        comprobarPerfil = new URL(respuesta.url).pathname === '/portal/acceso/';
    } catch (_) {
        if (version !== generation) return;
        if (logout) retryNotice();
        else if (opciones && opciones.method === 'POST') notice('No pudimos confirmar la operación. Revisá el resultado antes de reintentar.');
        else notice('No pudimos cargar la consulta. Volvé a intentarlo.');
    } finally {
        if (cancelacion) cancelacion.cerrar();
        if (version === generation) {
            lecturaActual = null;
            busy = false;
        }
        finalizar();
        if (mostrarInicio) navigate('/portal/', undefined, false, true);
        else if (comprobarPerfil && window.MidistriRecordado) MidistriRecordado.bootstrap();
    }
}

addEventListener('online', retryLogout);
if (pending()) retryLogout();
window.MidistriTab = {
    proof,
    esPortal,
    request: (url, opciones) => raw(url, opciones, codigo ? proof(true) : null),
    load: url => navigate(url, undefined, false, true),
    clear: () => {
        generation++;
        if (lecturaActual) lecturaActual.cancelar();
        lecturaActual = null;
        busy = false;
        sessionStorage.removeItem(KEY);
        sessionStorage.removeItem(PENDING);
        cleared();
    },
};

let remitoEnCurso = false;
document.addEventListener('click', async event => {
    const enlace = event.target.closest('a[data-remito-pdf]');
    const acceso = codigo ? proof(false) : null;
    if (!enlace || (codigo && !acceso) || event.defaultPrevented || event.button !== 0 ||
            event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    if (remitoEnCurso) return;
    remitoEnCurso = true;
    const finalizar = MidistriProgreso.iniciar('Abriendo PDF…');
    const cancelacion = plazoLectura();
    enlace.setAttribute('aria-busy', 'true');
    const version = generation;
    try {
        const respuesta = await raw(enlace.href, {signal: cancelacion.signal}, acceso);
        if (respuesta.redirected || !respuesta.ok ||
                !(respuesta.headers.get('Content-Type') || '').includes('application/pdf')) {
            throw Error('Este remito no está disponible.');
        }
        const contenido = await respuesta.blob();
        if (version !== generation || !enlace.isConnected) return;
        const url = URL.createObjectURL(contenido);
        if (enlace.dataset.remitoPdf === 'descargar') {
            const descarga = document.createElement('a');
            descarga.href = url;
            const nombre = (respuesta.headers.get('Content-Disposition') || '').match(/filename="(remito-[a-z0-9-]+[.]pdf)"/);
            descarga.download = nombre ? nombre[1] : 'remito.pdf';
            descarga.click();
            setTimeout(() => URL.revokeObjectURL(url), 60000);
            return;
        }
        const dialogo = document.querySelector('[data-remito-visor]');
        if (!dialogo || typeof dialogo.showModal !== 'function') {
            URL.revokeObjectURL(url);
            notice('Usá Descargar PDF para abrirlo e imprimirlo en tu dispositivo.');
            return;
        }
        const marco = dialogo.querySelector('iframe');
        const abrir = dialogo.querySelector('a');
        dialogo.addEventListener('close', () => {
            marco.removeAttribute('src');
            abrir.removeAttribute('href');
            URL.revokeObjectURL(url);
            enlace.focus();
        }, {once: true});
        abrir.href = url;
        marco.src = url;
        dialogo.showModal();
    } catch (_) {
        if (version === generation && enlace.isConnected) notice('No pudimos abrir este remito. Volvé a intentarlo.');
    } finally {
        cancelacion.cerrar();
        finalizar();
        enlace.removeAttribute('aria-busy');
        remitoEnCurso = false;
    }
});
const archivosCuenta = new Map([
    ['excel', ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'estado-cuenta.xlsx']],
    ['pdf', ['application/pdf', 'estado-cuenta.pdf']],
]);
let cuentaEnDescarga = false;
document.addEventListener('click', async evento => {
    const enlace = evento.target.closest('a[data-cuenta-descarga]');
    if (!enlace || !esPortal(enlace.href) || evento.defaultPrevented || evento.button !== 0 ||
            evento.ctrlKey || evento.metaKey || evento.shiftKey || evento.altKey) return;
    const archivo = archivosCuenta.get(enlace.dataset.cuentaDescarga);
    if (!archivo) return;
    evento.preventDefault();
    if (cuentaEnDescarga) return;
    const acceso = codigo ? proof(false) : null;
    if (codigo && !acceso) {
        notice('Ingresá nuevamente para descargar tu estado de cuenta.');
        return;
    }
    cuentaEnDescarga = true;
    const [mime, nombre] = archivo;
    const version = generation;
    const cancelacion = plazoLectura();
    const finalizar = MidistriProgreso.iniciar('Preparando descarga…');
    enlace.setAttribute('aria-busy', 'true');
    try {
        const respuesta = await raw(enlace.href, {signal: cancelacion.signal, redirect: 'error'}, acceso);
        if (!respuesta.ok || (respuesta.headers.get('Content-Type') || '').split(';')[0].trim() !== mime) {
            throw Error('descarga');
        }
        const contenido = await respuesta.blob();
        if (version !== generation || !enlace.isConnected) return;
        const url = URL.createObjectURL(contenido);
        const descarga = document.createElement('a');
        descarga.href = url;
        descarga.download = nombre;
        descarga.click();
        setTimeout(() => URL.revokeObjectURL(url), 60000);
    } catch (_) {
        if (version === generation && enlace.isConnected) notice('No pudimos descargar tu estado de cuenta. Volvé a intentarlo.');
    } finally {
        cancelacion.cerrar();
        finalizar();
        enlace.removeAttribute('aria-busy');
        cuentaEnDescarga = false;
    }
});
document.addEventListener('click', evento => {
    const enlace = evento.target.closest('a[href]');
    if (evento.defaultPrevented || !enlace || (enlace.target && enlace.target !== '_self') ||
            enlace.hasAttribute('download') || evento.button !== 0 ||
            evento.ctrlKey || evento.metaKey || evento.shiftKey || evento.altKey) return;
    const url = new URL(enlace.href, location.href);
    if (!esPortal(url) || url.hash) return;
    evento.preventDefault();
    navigate(url.href);
});
document.addEventListener('submit', evento => {
    const form = evento.target;
    if (evento.defaultPrevented || form.dataset.codigo || form.closest('[data-remito-visor]') ||
            form.method === 'dialog' || !form.action || form.target) return;
    const boton = evento.submitter;
    const url = new URL(boton && boton.hasAttribute('formaction') ? boton.formAction : form.action, location.href);
    if (!esPortal(url)) return;
    evento.preventDefault();
    const datos = new FormData(form);
    if (boton && boton.name) datos.append(boton.name, boton.value);
    if (form.method.toLowerCase() === 'get') {
        url.search = new URLSearchParams(datos);
        navigate(url.href);
    } else {
        navigate(url.href, {method: 'POST', body: datos}, codigo && !!proof(false) && url.pathname === '/portal/salir/');
    }
});
addEventListener('popstate', () => {
    if (esPortal(location.href)) navigate(location.href, undefined, false, true);
});
if (codigo && document.body.dataset.recordar !== '1' && !location.pathname.startsWith('/portal/acceso/') &&
        esPortal(location.href) && proof(false)) navigate(location.href, undefined, false, true);
})();
