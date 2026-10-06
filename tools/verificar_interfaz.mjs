/** Verificación de interfaz REAL con servidor Java iniciado.
 * Ejecutar con Playwright disponible: node tools/verificar_interfaz.mjs
 * RF03_BASE_URL opcional, por defecto http://127.0.0.1:8080.
 * No usa respuestas simuladas ni intercepta /api.
 */
import assert from 'node:assert/strict';
import { chromium } from 'playwright';
const browser = await chromium.launch({headless: true});
try {
 const page = await browser.newPage({viewport:{width:1280,height:900},reducedMotion:'reduce'});
 const errores=[];page.on('pageerror',e=>errores.push(e.message));
 const base=process.env.RF03_BASE_URL ?? 'http://127.0.0.1:8080';
 await page.goto(base);
 let propuestas=(await (await page.request.get(`${base}/api/propuestas`)).json()).length;
 let auditorias=(await (await page.request.get(`${base}/api/auditoria`)).json()).length;
 for(const [valor,codigo,creadas] of [['invalido',401,0],['evaluador',403,0],['investigador',200,1]]) {
  await page.locator(`input[value="${valor}"]`).check();
  await page.locator('#titulo').fill(`Propuesta en interfaz ${valor}`);
  const retorno=page.waitForResponse(r=>r.url().endsWith('/api/radicaciones')&&r.request().method()==='POST');
  await page.getByRole('button',{name:'Ejecutar solicitud'}).click();
  const respuesta=await retorno; assert.equal(respuesta.status(),codigo);
  const datos=await respuesta.json();assert.equal(datos.auditoria.codigo,codigo);
  await page.getByRole('heading',{name:datos.respuesta.mensaje,exact:true}).waitFor();
  for(let i=0;i<datos.traza.length;i++) await page.getByRole('button',{name:'Avanzar un paso'}).click();
  assert.equal(await page.locator('#code').textContent(),datos.traza.at(-1).fragmento);
  const omisiones=datos.traza.filter(e=>e.estado==='NO_EJECUTADO');
  for(const e of omisiones) assert.equal(await page.locator(`[data-handler="${e.manejador}"]`).getAttribute('data-state'),'NO_EJECUTADO');
  propuestas+=creadas;auditorias++;
  assert.equal((await (await page.request.get(`${base}/api/propuestas`)).json()).length,propuestas);
  assert.equal((await (await page.request.get(`${base}/api/auditoria`)).json()).length,auditorias);
  assert.match(await page.locator('#sim-code').textContent(),new RegExp(String(codigo)));
  if(codigo===401) {
   await page.locator('#sim-account').selectOption('evaluador');
   await page.getByRole('button',{name:'Entrar con cuenta de demostración'}).click();
   assert.ok(await page.locator('input[value="evaluador"]').isChecked());
   assert.equal(await page.locator('#titulo').inputValue(),`Propuesta en interfaz ${valor}`);
   assert.match(await page.locator('#sim-feedback').textContent(),/resultado anterior sigue siendo 401/);
  } else if(codigo===403) {
   await page.getByRole('button',{name:'Solicitar acceso'}).click();
   await page.locator('#sim-permission-reason').fill('Necesito radicar mi propuesta de investigación');
   await page.getByRole('button',{name:'Enviar solicitud simulada'}).click();
   assert.ok(await page.locator('#sim-ticket').isVisible());
   assert.match(await page.locator('#sim-feedback').textContent(),/No se envió ningún mensaje ni se concedió acceso/);
  } else {
   await page.getByRole('button',{name:'Abrir mi propuesta'}).click();
   await page.locator('#sim-feedback').filter({hasText:'Registro consultado en Java'}).waitFor();
   assert.equal(await page.locator('#sim-proposal-id').textContent(),datos.respuesta.propuestaId);
   assert.ok(await page.locator('#sim-detail').isVisible());
   await page.getByRole('button',{name:'Volver al comprobante'}).click();
  }
  assert.equal((await (await page.request.get(`${base}/api/propuestas`)).json()).length,propuestas);
  assert.equal((await (await page.request.get(`${base}/api/auditoria`)).json()).length,auditorias);
  await page.getByRole('button',{name:'Reiniciar reproducción'}).click();
  assert.equal(await page.locator('[data-state="PENDIENTE"]').count(),5);
  await page.getByRole('button',{name:'Reproducir',exact:false}).first().click();
  await page.getByRole('button',{name:'Pausar'}).click();
  assert.equal((await (await page.request.get(`${base}/api/propuestas`)).json()).length,propuestas);
  if(codigo===401) {
   await page.locator('#sim-draft-title').fill('Propuesta editada dentro del mini ERP');
   const reintento=page.waitForResponse(r=>r.url().endsWith('/api/radicaciones')&&r.request().method()==='POST');
   await page.getByRole('button',{name:'Reintentar radicación'}).click();
   const respuestaNueva=await reintento;assert.equal(respuestaNueva.status(),403);
   const nueva=await respuestaNueva.json();auditorias++;
   await page.getByRole('heading',{name:'Tu cuenta no tiene este permiso'}).waitFor();
   assert.notEqual(nueva.solicitudId,datos.solicitudId);
   assert.equal(nueva.traza[0].titulo,'Propuesta editada dentro del mini ERP');
   assert.equal((await (await page.request.get(`${base}/api/propuestas`)).json()).length,propuestas);
   assert.equal((await (await page.request.get(`${base}/api/auditoria`)).json()).length,auditorias);
  }
 }
 for(const width of [320,375,414,768,1280]) {
  await page.setViewportSize({width,height:900});
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth),width);
  await page.locator('summary').click();
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth),width);
  for(const img of await page.locator('.uml img').all()) assert.ok(await img.evaluate(e=>e.complete&&e.naturalWidth>0));
  await page.locator('summary').click();
 }
 assert.deepEqual(errores,[]);
 console.log('PASS: escenarios reales 401/403/200, auditoría, reproducción, pausa, reinicio y cinco anchos sin desbordamiento.');
} finally { await browser.close(); }
