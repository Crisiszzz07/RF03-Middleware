function nodo(id) {
    const n = document.getElementById(id);
    if (!n)
        throw new Error(`Elemento de simulación ausente: ${id}`);
    return n;
}
function texto(id, valor) { nodo(id).textContent = valor; }
let resultado = null;
let consulta = null;
let cuentaPreparada = null;
let ticketCreado = false;
function verVista(vista, foco) {
    consulta?.abort();
    consulta = null;
    for (const nombre of ['home', 'compose', 'permission', 'ticket', 'detail'])
        nodo('sim-' + nombre).hidden = nombre !== vista;
    nodo('sim-nav-home').setAttribute('aria-current', vista === 'detail' ? 'false' : 'page');
    nodo('sim-nav-detail').setAttribute('aria-current', vista === 'detail' ? 'page' : 'false');
    texto('sim-view-label', { home: 'Radicación', compose: 'Borrador de propuesta', permission: 'Solicitar acceso', ticket: 'Solicitud de acceso', detail: 'Mi propuesta' }[vista]);
    if (foco)
        nodo(foco).focus();
}
async function consultarPropuesta() {
    if (resultado?.respuesta.codigo !== 200 || !resultado.respuesta.propuestaId)
        return;
    const actual = resultado;
    consulta?.abort();
    const controlador = new AbortController();
    consulta = controlador;
    nodo('sim-action').disabled = true;
    nodo('sim-nav-detail').disabled = true;
    texto('sim-feedback', 'Abriendo tu propuesta desde el registro Java…');
    try {
        const respuesta = await fetch('api/propuestas', { signal: controlador.signal });
        if (!respuesta.ok)
            throw new Error(`Error HTTP ${respuesta.status}`);
        const propuestas = await respuesta.json();
        if (!Array.isArray(propuestas))
            throw new Error('Listado inesperado');
        if (resultado !== actual || controlador.signal.aborted)
            return;
        const propuesta = propuestas.find(p => p.id === actual.respuesta.propuestaId);
        if (!propuesta)
            throw new Error('El registro ya no existe; el servidor pudo reiniciarse');
        texto('sim-proposal-title', propuesta.titulo);
        texto('sim-proposal-id', propuesta.id);
        texto('sim-proposal-author', propuesta.autor);
        texto('sim-feedback', 'Registro consultado en Java. No se ha ejecutado una evaluación ni una aprobación.');
        verVista('detail', 'sim-proposal-title');
    }
    catch (error) {
        if (resultado !== actual || controlador.signal.aborted)
            return;
        texto('sim-feedback', `No se pudo consultar la propuesta: ${error instanceof Error ? error.message : 'Error de conexión'}.`);
    }
    finally {
        if (resultado === actual) {
            nodo('sim-action').disabled = false;
            nodo('sim-nav-detail').disabled = false;
        }
    }
}
export function iniciarSimulacion(alUsarCuenta, alReintentar) {
    nodo('sim-login-apply').addEventListener('click', () => {
        if (resultado?.respuesta.codigo !== 401)
            return;
        const cuenta = nodo('sim-account').value;
        if (cuenta !== 'investigador' && cuenta !== 'evaluador')
            return;
        cuentaPreparada = cuenta;
        alUsarCuenta(cuenta);
        texto('sim-session', `● ${cuenta} · sesión demo preparada`);
        nodo('sim-draft-title').value = resultado.traza[0]?.titulo ?? '';
        texto('sim-feedback', 'Sesión demo preparada. Revisa el borrador y pulsa «Reintentar radicación». Java validará la identidad; el resultado anterior sigue siendo 401.');
        verVista('compose', 'sim-draft-title');
    });
    nodo('sim-retry-form').addEventListener('submit', evento => {
        evento.preventDefault();
        if (resultado?.respuesta.codigo !== 401 || !cuentaPreparada)
            return;
        const titulo = nodo('sim-draft-title').value.trim();
        if (titulo.length < 5 || titulo.length > 120) {
            texto('sim-feedback', 'El título debe tener entre 5 y 120 caracteres. No se envió una nueva solicitud.');
            nodo('sim-draft-title').focus();
            return;
        }
        alReintentar(cuentaPreparada, titulo);
        nodo('sim-title').focus();
    });
    nodo('sim-change-account').addEventListener('click', () => {
        if (resultado?.respuesta.codigo !== 401)
            return;
        cuentaPreparada = null;
        texto('sim-session', '○ Sin sesión');
        texto('sim-feedback', '');
        verVista('home', 'sim-account');
    });
    nodo('sim-action').addEventListener('click', () => {
        if (resultado?.respuesta.codigo === 403) {
            texto('sim-feedback', '');
            verVista(ticketCreado ? 'ticket' : 'permission', ticketCreado ? 'sim-ticket-heading' : 'sim-permission-reason');
            return;
        }
        return consultarPropuesta();
    });
    nodo('sim-permission-form').addEventListener('submit', evento => {
        evento.preventDefault();
        if (resultado?.respuesta.codigo !== 403 || ticketCreado)
            return;
        const motivo = nodo('sim-permission-reason').value.trim();
        if (motivo.length < 10 || motivo.length > 400) {
            texto('sim-feedback', 'Escribe un motivo de 10 a 400 caracteres. No se creó una solicitud simulada.');
            nodo('sim-permission-reason').focus();
            return;
        }
        ticketCreado = true;
        texto('sim-ticket-id', 'ACCESO-DEMO-' + resultado.solicitudId.slice(0, 8));
        texto('sim-ticket-user', resultado.auditoria?.usuario ?? 'evaluador-demo');
        texto('sim-ticket-reason', motivo);
        texto('sim-workflow', 'Acceso solicitado · simulación local');
        texto('sim-action', 'Ver solicitud simulada');
        texto('sim-feedback', 'Solicitud simulada preparada. No se envió ningún mensaje ni se concedió acceso; la misma identidad seguirá devolviendo 403.');
        verVista('ticket', 'sim-ticket-heading');
    });
    for (const id of ['sim-nav-home', 'sim-permission-cancel', 'sim-ticket-back', 'sim-detail-back']) {
        nodo(id).addEventListener('click', () => { texto('sim-feedback', ''); verVista('home', 'sim-title'); });
    }
    nodo('sim-nav-detail').addEventListener('click', consultarPropuesta);
}
export function prepararSimulacion(mensaje = 'Ejecuta un escenario arriba para ver la respuesta de tu ERP aquí.') {
    consulta?.abort();
    consulta = null;
    resultado = null;
    cuentaPreparada = null;
    ticketCreado = false;
    nodo('simulacion').dataset.outcome = 'pendiente';
    texto('sim-code', 'Sin respuesta');
    texto('sim-title', 'Tu espacio de investigación');
    texto('sim-message', mensaje);
    texto('sim-system', 'Esperando un resultado verificable');
    texto('sim-next', 'Selecciona un escenario y ejecuta la solicitud');
    texto('sim-storage', '—');
    texto('sim-workflow', '—');
    texto('sim-request', '—');
    texto('sim-feedback', '');
    texto('sim-action', 'Esperando resultado');
    texto('sim-session', '○ Sin sesión');
    texto('sim-status-icon', '↗');
    nodo('sim-action').disabled = true;
    nodo('sim-nav-detail').disabled = true;
    nodo('sim-action').hidden = false;
    nodo('sim-login').hidden = true;
    nodo('sim-draft-title').value = '';
    nodo('sim-permission-reason').value = '';
    for (const id of ['sim-ticket-id', 'sim-ticket-user', 'sim-ticket-reason', 'sim-proposal-title', 'sim-proposal-id', 'sim-proposal-author'])
        texto(id, '—');
    verVista('home');
}
export function mostrarSimulacion(ejecucion) {
    prepararSimulacion();
    resultado = ejecucion;
    const codigo = ejecucion.respuesta.codigo;
    texto('sim-code', `Respuesta Java · ${codigo}`);
    texto('sim-request', ejecucion.solicitudId);
    texto('sim-session', ejecucion.auditoria?.usuario && codigo !== 401 ? '● ' + ejecucion.auditoria.usuario : '○ Sin sesión');
    if (codigo === 401) {
        nodo('simulacion').dataset.outcome = 'rechazo';
        texto('sim-status-icon', '⊘');
        texto('sim-title', 'Tu sesión no es válida');
        texto('sim-message', 'En un ERP real se pediría recuperar la sesión o volver a iniciar sesión antes de radicar.');
        texto('sim-system', 'Detiene la operación y ofrece recuperar la sesión');
        texto('sim-next', 'Autenticarse y volver a enviar la propuesta');
        texto('sim-storage', 'No se creó una propuesta; el rechazo quedó auditado');
        texto('sim-workflow', 'Pendiente de autenticación');
        nodo('sim-action').hidden = true;
        nodo('sim-login').hidden = false;
        nodo('sim-account').value = 'investigador';
    }
    else if (codigo === 403) {
        nodo('simulacion').dataset.outcome = 'rechazo';
        texto('sim-status-icon', '⊘');
        texto('sim-title', 'Tu cuenta no tiene este permiso');
        texto('sim-message', 'El ERP reconoce tu identidad, pero bloquea la radicación. Repetir el intento con los mismos permisos no cambia el resultado.');
        texto('sim-system', 'Informa la restricción y conserva el rechazo en auditoría');
        texto('sim-next', 'Solicitar una revisión de permisos al administrador');
        texto('sim-storage', 'No se creó una propuesta; identidad: ' + (ejecucion.auditoria?.usuario ?? '—'));
        texto('sim-workflow', 'Radicación bloqueada por permisos');
        texto('sim-action', 'Solicitar acceso');
        nodo('sim-action').disabled = false;
    }
    else if (codigo === 200 && ejecucion.respuesta.propuestaId) {
        nodo('simulacion').dataset.outcome = 'exito';
        texto('sim-status-icon', '✓');
        nodo('sim-nav-detail').disabled = false;
        texto('sim-title', 'Propuesta radicada correctamente');
        texto('sim-message', `Comprobante: ${ejecucion.respuesta.propuestaId}. ${ejecucion.traza[0]?.titulo ?? ''}`);
        texto('sim-system', 'Confirma el registro y ofrece consultar la propuesta');
        texto('sim-next', 'Consultar el radicado; luego seguir el proceso de revisión del ERP');
        texto('sim-storage', 'Propuesta guardada realmente en memoria y operación auditada');
        texto('sim-workflow', 'Radicada ≠ aprobada · revisión futura ilustrativa');
        texto('sim-action', 'Abrir mi propuesta');
        nodo('sim-action').disabled = false;
    }
    else {
        texto('sim-title', codigo === 400 ? 'Corrige los datos de la propuesta' : 'Resultado fuera de los tres escenarios');
        texto('sim-message', ejecucion.respuesta.mensaje);
        texto('sim-system', codigo === 400 ? 'Solicita corregir los datos antes de iniciar la cadena' : 'No se simula una continuación para este resultado');
        texto('sim-next', 'Revisa los datos antes de enviar otra solicitud');
        nodo('sim-action').hidden = true;
    }
}
