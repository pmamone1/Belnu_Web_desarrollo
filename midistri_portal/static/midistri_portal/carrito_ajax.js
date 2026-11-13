(function () {
    'use strict';
    let enCurso = false;

    function actualizarIndicador(unidades) {
        document.querySelectorAll('[data-carrito-unidades]').forEach(el => { el.textContent = unidades; });
        document.querySelectorAll('[data-carrito-descripcion]').forEach(el => {
            el.textContent = unidades + (unidades === 1 ? ' unidad' : ' unidades') + ' en el carrito';
        });
    }

    function mostrar(nodo, texto, error) {
        nodo.textContent = texto;
        nodo.toggleAttribute('data-error', error);
    }

    // No se puede enviar ni navegar mediante el portal mientras se guarda un cambio.
    document.addEventListener('submit', async evento => {
        const form = evento.target;
        if (enCurso) {
            evento.preventDefault();
            return;
        }
        if (!form.matches('form[data-carrito-cantidad]') || !window.fetch) return;
        evento.preventDefault();
        const panel = form.closest('[data-carrito-contenido]');
        const estado = panel ? document.querySelector('[data-carrito-estado]') : form.querySelector('[data-carrito-estado]');
        const datos = new FormData(form);
        if (evento.submitter && evento.submitter.name === 'quitar') datos.set('quitar', '1');
        const activo = document.activeElement;
        const botones = Array.from(form.querySelectorAll('button:not([disabled]),input[name=cantidad]:not([disabled])'));
        enCurso = true;
        form.setAttribute('aria-busy', 'true');
        botones.forEach(b => { b.disabled = true; });
        mostrar(estado, 'Actualizando carrito…', false);

        try {
            const opciones = {method: 'POST', body: datos, headers: {Accept: 'application/json'}};
            const respuesta = window.MidistriTab
                ? await window.MidistriTab.request(form.action, opciones)
                : await fetch(form.action, {...opciones, credentials: 'same-origin'});
            const result = await respuesta.json();
            if (!respuesta.ok) {
                mostrar(estado, result.error || 'No pudimos actualizar el carrito.', true);
                return;
            }
            if (!form.isConnected || !Number.isInteger(result.unidades) || !Number.isInteger(result.cantidad)) return;
            actualizarIndicador(result.unidades);
            if (panel && typeof result.carrito_html === 'string') {
                const observaciones = panel.querySelector('[name=observaciones]');
                const texto = observaciones && observaciones.value;
                // La plantilla de servidor escapa los datos de producto y de la tienda.
                panel.innerHTML = result.carrito_html;
                const nuevaObservacion = panel.querySelector('[name=observaciones]');
                if (nuevaObservacion && texto) nuevaObservacion.value = texto;
                const siguiente = Array.from(panel.querySelectorAll('[data-carrito-cantidad]')).find(
                    item => item.elements.producto.value === datos.get('producto'));
                if (!activo.isConnected) {
                    const foco = (siguiente && siguiente.querySelector('button[type=submit]:not([name]), button:not([type])'))
                        || document.getElementById('carrito-revision');
                    foco.focus({preventScroll: true});
                }
            } else {
                const cantidad = form.querySelector('[name=cantidad]');
                if (cantidad) cantidad.value = result.cantidad;
            }
            mostrar(estado, result.mensaje + ' ' + result.unidades + (result.unidades === 1 ? ' unidad.' : ' unidades.'), false);
        } catch (_) {
            mostrar(estado, 'No pudimos confirmar el cambio. Revisá el carrito antes de volver a intentarlo.', true);
        } finally {
            enCurso = false;
            form.removeAttribute('aria-busy');
            botones.forEach(b => { b.disabled = false; });
            if (activo.isConnected && form.contains(activo) && document.activeElement === document.body) {
                activo.focus({preventScroll: true});
            }
        }
    }, true);

    document.addEventListener('click', evento => {
        const enlace = evento.target.closest('a[href]');
        if (enCurso && enlace && enlace.origin === location.origin && enlace.pathname.startsWith('/portal/')) {
            evento.preventDefault();
        }
    }, true);
})();
