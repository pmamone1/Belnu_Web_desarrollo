(function () {
    'use strict';
    function inicializar() {
        document.querySelectorAll('[data-pedido-toggle]').forEach(enlace => {
            const detalle = document.getElementById(enlace.getAttribute('aria-controls'));
            if (!detalle) return;
            detalle.hidden = true;
            enlace.setAttribute('aria-expanded', 'false');
        });
    }
    document.addEventListener('click', evento => {
        const enlace = evento.target.closest('[data-pedido-toggle]');
        const detalle = enlace && document.getElementById(enlace.getAttribute('aria-controls'));
        if (!detalle || evento.defaultPrevented || evento.ctrlKey || evento.metaKey ||
                evento.shiftKey || evento.altKey || evento.button !== 0) return;
        evento.preventDefault();
        detalle.hidden = !detalle.hidden;
        enlace.setAttribute('aria-expanded', String(!detalle.hidden));
        enlace.textContent = detalle.hidden ? 'Ver detalle' : 'Ocultar detalle';
    });
    document.addEventListener('midistri:render', inicializar);
    inicializar();
})();
