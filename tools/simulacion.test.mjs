/** Pruebas de interacción del componente, sin navegador.
 * DOM y transporte de lectura controlados: no certifican el servidor ni el diseño visual.
 * Ejecutar: node tools/simulacion.test.mjs
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
const fuente = await readFile(new URL('../src/main/resources/static/simulacion.js', import.meta.url), 'utf8');
const { iniciarSimulacion, prepararSimulacion, mostrarSimulacion } = await import(`data:text/javascript;base64,${Buffer.from(fuente).toString('base64')}`);
const html = await readFile(new URL('../src/main/resources/static/index.html', import.meta.url), 'utf8');
const ids = new Set(Array.from(html.matchAll(/id="([^"]+)"/g), m => m[1]));
function montar() {
 const elementos = new Map();
 globalThis.document = { getElementById(id) {
  assert.ok(ids.has(id),`Elemento presente en el HTML real: ${id}`);
  if (!elementos.has(id)) elementos.set(id,{textContent:'',hidden:false,disabled:false,value:'',dataset:{},listeners:{},attributes:{},focus(){},setAttribute(k,v){this.attributes[k]=v;},addEventListener(tipo,accion){this.listeners[tipo]=accion;}});
  return elementos.get(id);
 }};
 const nodo=id=>document.getElementById(id);
 const cuentas=[]; const reintentos=[]; const peticiones=[];
 globalThis.fetch=async (...args)=>{peticiones.push(args);throw new Error('Transporte no preparado');};
 iniciarSimulacion(cuenta=>cuentas.push(cuenta),(cuenta,titulo)=>reintentos.push({cuenta,titulo}));prepararSimulacion();
 return {nodo,cuentas,reintentos,peticiones,click:id=>nodo(id).listeners.click(),submit:id=>nodo(id).listeners.submit({preventDefault(){}})};
}
function resultado(codigo, id='solicitud-1') {
 return {solicitudId:id,respuesta:{codigo,mensaje:'Respuesta Java',propuestaId:codigo===200?'RF03-0001':null},traza:[{titulo:'Propuesta de investigación'}],auditoria:codigo===400?null:{usuario:codigo===403?'evaluador-demo':'investigadora-demo'}};
}
test('reacciones y acciones posteriores a la respuesta Java',async t=>{
 await t.test('401 prepara credenciales sin reenviar ni cambiar el resultado',()=>{
  const ui=montar();mostrarSimulacion(resultado(401));
  assert.equal(ui.nodo('sim-login').hidden,false);assert.equal(ui.nodo('sim-action').hidden,true);
  ui.nodo('sim-account').value='evaluador';ui.click('sim-login-apply');
  assert.deepEqual(ui.cuentas,['evaluador']);assert.deepEqual(ui.peticiones,[]);
  assert.match(ui.nodo('sim-feedback').textContent,/resultado anterior sigue siendo 401/);
  assert.match(ui.nodo('sim-code').textContent,/401/);
  assert.equal(ui.nodo('sim-compose').hidden,false);
  assert.equal(ui.nodo('sim-draft-title').value,'Propuesta de investigación');
 });
 await t.test('403 permite simular solicitud de permiso sin concederlo ni escribir al servidor',async()=>{
  const ui=montar();mostrarSimulacion(resultado(403));await ui.click('sim-action');
  assert.equal(ui.nodo('sim-permission').hidden,false);
  ui.nodo('sim-permission-reason').value='Necesito radicar una investigación';
  ui.submit('sim-permission-form');
  assert.equal(ui.nodo('sim-ticket').hidden,false);
  assert.match(ui.nodo('sim-ticket-id').textContent,/ACCESO-DEMO-/);
  assert.match(ui.nodo('sim-feedback').textContent,/seguirá devolviendo 403/);
  assert.equal(ui.nodo('sim-action').textContent,'Ver solicitud simulada');assert.deepEqual(ui.cuentas,[]);assert.deepEqual(ui.peticiones,[]);
 });
 await t.test('200 consulta el identificador real con una lectura, sin crear ni aprobar',async()=>{
  const ui=montar();mostrarSimulacion(resultado(200));
  globalThis.fetch=async (...args)=>{ui.peticiones.push(args);return {ok:true,json:async()=>[{id:'RF03-0001',titulo:'Título del repositorio',autor:'investigadora-demo'}]};};
  await ui.click('sim-action');assert.equal(ui.peticiones.length,1);
  assert.equal(ui.peticiones[0][0],'api/propuestas');assert.equal(ui.peticiones[0][1].method,undefined);
  assert.equal(ui.nodo('sim-detail').hidden,false);
  assert.equal(ui.nodo('sim-proposal-title').textContent,'Título del repositorio');
  assert.equal(ui.nodo('sim-proposal-id').textContent,'RF03-0001');
  assert.match(ui.nodo('sim-feedback').textContent,/No se ha ejecutado una evaluación/);
 });
 await t.test('registro ausente no fabrica una confirmación',async()=>{
  const ui=montar();mostrarSimulacion(resultado(200));
  globalThis.fetch=async()=>({ok:true,json:async()=>[]});await ui.click('sim-action');
  assert.match(ui.nodo('sim-feedback').textContent,/registro ya no existe/);assert.equal(ui.nodo('sim-action').disabled,false);
 });
 await t.test('una lectura anterior no contamina una nueva solicitud',async()=>{
  const ui=montar();mostrarSimulacion(resultado(200));let completar;
  globalThis.fetch=()=>new Promise(resolve=>{completar=resolve;});
  const lectura=ui.click('sim-action');mostrarSimulacion(resultado(403,'solicitud-2'));
  completar({ok:true,json:async()=>[{id:'RF03-0001',titulo:'Antigua',autor:'demo'}]});await lectura;
  assert.equal(ui.nodo('sim-feedback').textContent,'');assert.equal(ui.nodo('sim-request').textContent,'solicitud-2');
  assert.equal(ui.nodo('sim-action').disabled,false);
 });
 await t.test('400 diferencia la validación previa de un rechazo de seguridad',()=>{
  const ui=montar();mostrarSimulacion(resultado(400));assert.match(ui.nodo('sim-system').textContent,/antes de iniciar la cadena/);
  assert.equal(ui.nodo('sim-action').hidden,true);assert.equal(ui.nodo('sim-login').hidden,true);
 });
 await t.test('sin respuesta no se conserva un resultado ni una acción anterior',()=>{
  const ui=montar();mostrarSimulacion(resultado(403));prepararSimulacion('Sin respuesta verificable');
  assert.equal(ui.nodo('sim-request').textContent,'—');assert.equal(ui.nodo('sim-action').disabled,true);
  assert.equal(ui.nodo('sim-feedback').textContent,'');assert.match(ui.nodo('sim-message').textContent,/Sin respuesta/);
 });
 await t.test('reintento explícito conserva cuenta y envía el título editado al cliente',()=>{
  const ui=montar();mostrarSimulacion(resultado(401));ui.nodo('sim-account').value='investigador';ui.click('sim-login-apply');
  assert.deepEqual(ui.reintentos,[]);
  ui.nodo('sim-draft-title').value='  Propuesta editada  ';ui.submit('sim-retry-form');
  assert.deepEqual(ui.reintentos,[{cuenta:'investigador',titulo:'Propuesta editada'}]);
 });
 await t.test('título inválido y cambio de cuenta impiden reintentar con una sesión sin preparar',()=>{
  const ui=montar();mostrarSimulacion(resultado(401));ui.nodo('sim-account').value='investigador';ui.click('sim-login-apply');
  ui.nodo('sim-draft-title').value='   ';ui.submit('sim-retry-form');assert.deepEqual(ui.reintentos,[]);
  assert.match(ui.nodo('sim-feedback').textContent,/No se envió una nueva solicitud/);
  ui.click('sim-change-account');ui.nodo('sim-draft-title').value='Propuesta editada';ui.submit('sim-retry-form');
  assert.deepEqual(ui.reintentos,[]);assert.equal(ui.nodo('sim-home').hidden,false);
 });
 await t.test('cancelar o enviar un motivo inválido no crea un ticket',()=>{
  const ui=montar();mostrarSimulacion(resultado(403));ui.click('sim-action');
  ui.nodo('sim-permission-reason').value=' ';ui.submit('sim-permission-form');
  assert.equal(ui.nodo('sim-ticket').hidden,true);assert.match(ui.nodo('sim-feedback').textContent,/No se creó/);
  ui.click('sim-permission-cancel');assert.equal(ui.nodo('sim-home').hidden,false);assert.deepEqual(ui.peticiones,[]);
 });
 await t.test('volver al comprobante y abrir un nuevo resultado limpia detalle y ticket',async()=>{
  const ui=montar();mostrarSimulacion(resultado(200));
  globalThis.fetch=async()=>({ok:true,json:async()=>[{id:'RF03-0001',titulo:'Título',autor:'demo'}]});
  await ui.click('sim-action');ui.click('sim-detail-back');assert.equal(ui.nodo('sim-home').hidden,false);
  mostrarSimulacion(resultado(403,'solicitud-nueva'));
  assert.equal(ui.nodo('sim-detail').hidden,true);assert.equal(ui.nodo('sim-proposal-id').textContent,'—');
  assert.equal(ui.nodo('sim-nav-detail').disabled,true);assert.equal(ui.nodo('sim-ticket-id').textContent,'—');
 });

});
