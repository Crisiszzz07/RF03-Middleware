type Estado = 'PENDIENTE' | 'EJECUTANDO' | 'CONTINUA' | 'RECHAZA' | 'COMPLETA' | 'NO_EJECUTADO';
type Direccion = 'IDA' | 'RETORNO' | 'OMISION' | 'VALIDACION';
interface EventoTraza {
  paso: number; manejador: string; metodo: string; estado: Estado; direccion: Direccion;
  accion: string; motivo: string; identidad: string; titulo: string; codigo: number | null;
  archivo: string; fragmento: string; explicacion: string;
}
interface Ejecucion {
  solicitudId: string;
  respuesta: { codigo: number; mensaje: string; propuestaId: string | null };
  traza: EventoTraza[];
  auditoria: { solicitudId: string; fecha: string; usuario: string; codigo: number; propuestaId: string | null } | null;
  propuestasRegistradas: number;
}
interface Escenario { token: string; descripcion: string }
const escenarios: Record<string, Escenario> = {
  invalido: { token: 'DEMO-INVALIDO', descripcion: 'Credencial ficticia no reconocida. Resultado esperado: 401 y auditoría, sin propuesta.' },
  evaluador: { token: 'DEMO-EVALUADOR', descripcion: 'Credencial ficticia de evaluador. Resultado esperado: 403 y auditoría, sin propuesta.' },
  investigador: { token: 'DEMO-INVESTIGADOR', descripcion: 'Credencial ficticia de investigador. Resultado esperado: 200, propuesta y auditoría.' }
};
const etiquetas: Record<Estado, string> = {
  PENDIENTE: '○ Pendiente', EJECUTANDO: '◉ Ejecutando', CONTINUA: '→ Continúa',
  RECHAZA: '⊘ Rechaza', COMPLETA: '✓ Completa', NO_EJECUTADO: '— No ejecutado'
};
const direcciones: Record<Direccion, string> = {
  IDA: '→ Avanza la solicitud', RETORNO: '← Retorna la respuesta hacia Auditoría y el cliente',
  OMISION: '— Eslabón omitido por el rechazo anterior', VALIDACION: '⊘ Validación de datos: la cadena no se inició'
};
function elemento<T extends HTMLElement = HTMLElement>(id: string): T {
  const nodo = document.getElementById(id);
  if (!nodo) throw new Error(`Elemento ausente: ${id}`);
  return nodo as T;
}
function texto(id: string, valor: string): void { elemento(id).textContent = valor; }
const formulario = elemento<HTMLFormElement>('formulario');
const selector = elemento<HTMLSelectElement>('event-select');
const nodos = Array.from(document.querySelectorAll<HTMLButtonElement>('[data-handler]'));
let ejecucion: Ejecucion | null = null;
let posicion = -1;
let temporizador: number | undefined;
let enviando = false;
const movimientoReducido = window.matchMedia('(prefers-reduced-motion: reduce)');

function escenarioElegido(): Escenario {
  const radio = formulario.querySelector<HTMLInputElement>('input[name="escenario"]:checked');
  return escenarios[radio?.value ?? 'investigador'];
}
function controles(): void {
  const disponible = !!ejecucion && !enviando;
  elemento<HTMLButtonElement>('play').disabled = !disponible || temporizador !== undefined || posicion >= (ejecucion?.traza.length ?? 0) - 1;
  elemento<HTMLButtonElement>('pause').disabled = temporizador === undefined;
  elemento<HTMLButtonElement>('step').disabled = !disponible || posicion >= (ejecucion?.traza.length ?? 0) - 1;
  elemento<HTMLButtonElement>('reset').disabled = !disponible;
  selector.disabled = !disponible;
}
function pausar(): void {
  if (temporizador !== undefined) window.clearInterval(temporizador);
  temporizador = undefined;
  controles();
}
function mostrarEvento(evento: EventoTraza): void {
  texto('event-label', `PASO ${evento.paso} · ${etiquetas[evento.estado]}`);
  texto('event-title', `${evento.manejador}.${evento.metodo}()`);
  texto('event-explanation', evento.explicacion);
  texto('event-action', evento.accion);
  texto('event-reason', evento.motivo);
  texto('event-identity', evento.identidad);
  texto('event-request', evento.titulo);
  texto('code-method', evento.archivo);
  texto('code', evento.fragmento);
  texto('code-caption', 'Fuente exacta entre marcadores. El archivo puede ser un servicio consultado o un método heredado.');
  const enlace = elemento<HTMLAnchorElement>('source-link');
  // Solo enlaces a fuentes locales; el texto siempre se inserta con textContent.
  enlace.href = `codigo/${evento.archivo}`;
  enlace.hidden = false;
}
function dibujar(): void {
  nodos.forEach(nodo => {
    nodo.dataset.state = 'PENDIENTE'; nodo.setAttribute('aria-pressed', 'false');
    nodo.querySelector('.node-state')!.textContent = etiquetas.PENDIENTE;
  });
  if (ejecucion && posicion >= 0) {
    // Reduce exclusivamente eventos emitidos por Java. No deduce decisiones a partir del escenario.
    ejecucion.traza.slice(0, posicion + 1).forEach(evento => {
      const nodo = nodos.find(n => n.dataset.handler === evento.manejador);
      if (nodo) { nodo.dataset.state = evento.estado; nodo.querySelector('.node-state')!.textContent = etiquetas[evento.estado]; }
    });
    const evento = ejecucion.traza[posicion];
    nodos.find(n => n.dataset.handler === evento.manejador)?.setAttribute('aria-pressed', 'true');
    elemento('eslabones').dataset.direction = evento.direccion;
    texto('flow', direcciones[evento.direccion]);
    mostrarEvento(evento);
    texto('progress', `Paso ${posicion + 1} de ${ejecucion.traza.length}`);
    selector.value = String(posicion);
  } else {
    delete elemento('eslabones').dataset.direction;
    texto('flow', '→ Ida de la solicitud · ← Retorno de la respuesta a Auditoría');
    texto('progress', ejecucion ? `0 de ${ejecucion.traza.length} pasos` : 'Sin solicitud');
    texto('event-label', 'EXPLORADOR DE PASOS');
    texto('event-title', 'La cadena comienza en el cliente');
    texto('event-explanation', ejecucion ? 'La respuesta real ya llegó. Reproduce su traza o avanza un paso.' : 'Ejecuta uno de los escenarios para obtener su traza desde Java.');
    texto('event-action', 'Reproducción pendiente'); texto('event-reason', 'Los controles no ejecutan Java');
    texto('event-identity', 'Sin identidad autenticada'); texto('event-request', '—');
    texto('code', '// Los fragmentos provienen del backend.\n// Se extraen de los archivos Java entregados.');
    texto('code-method', 'Java · fuente del evento'); elemento('source-link').hidden = true;
    selector.value = '-1';
  }
  controles();
}
function avanzar(): void {
  if (!ejecucion || posicion >= ejecucion.traza.length - 1) { pausar(); return; }
  posicion++; dibujar();
  if (posicion >= ejecucion.traza.length - 1) pausar();
}
function reproducir(): void {
  if (!ejecucion || temporizador !== undefined || posicion >= ejecucion.traza.length - 1) return;
  avanzar();
  if (posicion < ejecucion.traza.length - 1) temporizador = window.setInterval(avanzar, movimientoReducido.matches ? 1800 : 1050);
  controles();
}
function mostrarResultado(): void {
  if (!ejecucion) return;
  const { respuesta, auditoria } = ejecucion;
  const exito = respuesta.codigo === 200;
  texto('result-code', `${exito ? '✓' : '⊘'} ${respuesta.codigo}`);
  elemento('result-code').className = `result-code ${exito ? 'success' : 'reject'}`;
  texto('result-title', respuesta.mensaje);
  texto('result-detail', `${respuesta.propuestaId ? `Identificador: ${respuesta.propuestaId}. ` : 'Esta solicitud no creó una propuesta. '}Total en memoria: ${ejecucion.propuestasRegistradas}. Java ya terminó; reproducir no guarda de nuevo.`);
  texto('audit-title', auditoria ? '✓ Resultado registrado al retornar' : 'Cadena no iniciada: sin auditoría de seguridad');
  texto('audit-id', auditoria?.solicitudId ?? '—'); texto('audit-user', auditoria?.usuario ?? '—');
  texto('audit-date', auditoria ? new Date(auditoria.fecha).toLocaleString('es-CO') : '—');
  texto('audit-code', auditoria ? String(auditoria.codigo) : '—');
}
formulario.addEventListener('change', () => texto('scenario-detail', escenarioElegido().descripcion));
formulario.addEventListener('submit', async evento => {
  evento.preventDefault();
  if (enviando) return;
  const titulo = elemento<HTMLInputElement>('titulo').value.trim();
  const error = elemento('error');
  if (titulo.length < 5 || titulo.length > 120) {
    error.textContent = 'Validación de datos: escribe un título entre 5 y 120 caracteres. La cadena aún no se ha iniciado.';
    error.hidden = false; elemento('titulo').focus(); return;
  }
  pausar(); ejecucion = null; posicion = -1; enviando = true; error.hidden = true;
  formulario.querySelectorAll<HTMLInputElement | HTMLButtonElement>('input,button').forEach(n => n.disabled = true);
  texto('result-code', '…'); elemento('result-code').className = 'result-code';
  texto('result-title', 'Procesando en Java'); texto('result-detail', 'Esperando la respuesta del servidor local');
  texto('audit-title', 'Esperando la respuesta'); ['audit-id','audit-user','audit-date','audit-code'].forEach(id => texto(id, '—'));
  dibujar();
  try {
    const respuesta = await fetch('api/radicaciones', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token: escenarioElegido().token, titulo }), signal: AbortSignal.timeout(15000)
    });
    // 401 y 403 son resultados didácticos con traza; no son fallos de transporte.
    const datos: Ejecucion | { mensaje?: string } = await respuesta.json();
    if (!('traza' in datos) || !Array.isArray(datos.traza) || !('respuesta' in datos))
      throw new Error(('mensaje' in datos && datos.mensaje) || `Respuesta inesperada (${respuesta.status})`);
    ejecucion = datos;
    selector.replaceChildren(new Option('Seleccionar un paso', '-1'), ...datos.traza.map((e, i) => new Option(`${e.paso}. ${e.manejador} · ${e.estado}`, String(i))));
    mostrarResultado();
  } catch (fallo) {
    error.textContent = `No se pudo obtener la traza del servidor local. ${fallo instanceof Error ? fallo.message : 'Comprueba la conexión'}. Si hubo un corte tras enviar, revisa /api/propuestas antes de reintentar.`;
    error.hidden = false; texto('result-code', '—'); texto('result-title', 'Sin respuesta verificable');
    texto('result-detail', 'No se reproduce una traza sin respuesta del backend.');
    texto('audit-title', 'Sin respuesta verificable');
    selector.replaceChildren(new Option('Sin traza', '-1'));
  } finally {
    enviando = false;
    formulario.querySelectorAll<HTMLInputElement | HTMLButtonElement>('input,button').forEach(n => n.disabled = false);
    dibujar();
    if (ejecucion && !movimientoReducido.matches) reproducir();
  }
});
elemento('play').addEventListener('click', reproducir);
elemento('pause').addEventListener('click', pausar);
elemento('step').addEventListener('click', () => { pausar(); avanzar(); });
elemento('reset').addEventListener('click', () => { pausar(); posicion = -1; dibujar(); });
selector.addEventListener('change', () => { pausar(); posicion = Number(selector.value); dibujar(); });
nodos.forEach(nodo => nodo.addEventListener('click', () => {
  if (!ejecucion || posicion < 0) return;
  let indice = -1;
  ejecucion.traza.slice(0, posicion + 1).forEach((e, i) => { if (e.manejador === nodo.dataset.handler) indice = i; });
  if (indice >= 0) { pausar(); posicion = indice; dibujar(); }
}));
movimientoReducido.addEventListener('change', () => { if (movimientoReducido.matches) pausar(); });
texto('scenario-detail', escenarioElegido().descripcion);
controles();
export {};
