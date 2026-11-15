(function () {
    'use strict';
    const tareas = new Map();
    const estado = document.createElement('div');
    estado.id = 'midistri-progreso';
    estado.setAttribute('role', 'status');
    estado.setAttribute('aria-live', 'polite');
    const icono = document.createElement('span');
    icono.className = 'recordado-spinner';
    icono.setAttribute('aria-hidden', 'true');
    const texto = document.createElement('span');
    estado.append(icono, texto);

    function actualizar() {
        const mensajes = Array.from(tareas.values());
        estado.hidden = mensajes.length === 0;
        texto.textContent = mensajes[mensajes.length - 1] || '';
        if (!estado.isConnected) document.body.append(estado);
        const contenido = document.querySelector('main');
        if (contenido) contenido.setAttribute('aria-busy', String(tareas.size > 0));
    }

    function iniciar(mensaje) {
        const tarea = Symbol();
        tareas.set(tarea, mensaje);
        actualizar();
        return () => {
            tareas.delete(tarea);
            actualizar();
        };
    }

    document.addEventListener('midistri:render', actualizar);
    window.MidistriProgreso = {iniciar};
})();
