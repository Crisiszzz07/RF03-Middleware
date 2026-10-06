# Verificación de la entrega

## Comprobaciones realizadas en entorno local (Fedora WSL2 / Java 17)

| Comprobación | Estado | Evidencia / Observaciones |
|---|---|---|
| Compilación Java y empaquetado JAR | Superado | Compilado exitosamente mediante Eclipse Temurin JDK 17.0.14 y Maven Wrapper (`BUILD SUCCESS`). |
| Pruebas automatizadas (JUnit / Mockito) | Superado | Suite completa de pruebas ejecutada sin fallos ni errores reportados en `target/surefire-reports/`. |
| Arranque de Spring Boot | Superado | Tomcat levantado en puerto 8080 bajo Java 17 en entorno Linux Fedora. |
| Escenarios de la cadena (401, 403 y 200) | Superado | Se verificó la interrupción correcta de la cadena en fallos de autenticación/autorización y omisión de eslabones posteriores. Idempotencia validada en reinicio. |
| Responsividad y accesibilidad web | Superado | Diseño fluido verificado en 320px, 375px, 414px, 768px y 1280px. Foco visible por teclado validado. |
| Generación de artefactos finales | Superado | Ejecución de `tools/empaquetar.py` completada; JAR generado e integrado en el archivo ZIP final de entrega. |
## Actualización: simulación de la reacción del ERP (2026-10-06)

Las verificaciones anteriores describen la entrega previa. Para el nuevo componente:

- TypeScript 5.9.3 con configuración estricta: compilación correcta de `app.ts` y `simulacion.ts`.
- Comprobación estructural: 234 comprobaciones aprobadas, incluidos los IDs del nuevo panel.
- `node tools/simulacion.test.mjs`: siete casos de interacción aprobados (ocho pruebas contando el grupo). DOM y transporte controlados; no es una prueba de navegador. Comprueba 401, 403, consulta 200, registro ausente, aislamiento de respuestas tardías, 400 y ausencia de respuesta.
- `CadenaTest`: ocho pruebas Java aprobadas con JDK 17 y Byte Buddy precargado como agente, evitando el autoattach que bloquea el entorno. No se cambió la lógica Java de la cadena.
- `./mvnw -o verify`: la suite completa no pudo finalizar con éxito en el entorno del agente. Tomcat no puede abrir sockets (`SocketException: Operation not permitted`); el primer intento de Mockito sin agente también falló por autoattach. Las pruebas HTTP siguen pendientes en un entorno que permita abrir el servidor.
- Chromium/Playwright: se intentó abrir para revisar la interfaz actual, pero el proceso falla antes de crear una página (`Operation not permitted` en `sandbox_host_linux.cc`). Revisión visual móvil y prueba del nuevo panel en navegador real: pendientes.

El ZIP fuente se actualiza con `python3 tools/empaquetar.py --solo-fuentes`. El JAR anterior no se actualiza ni se presenta como comprobado con la nueva interfaz. Para incluir el componente en un JAR, ejecute `./mvnw clean verify` en el entorno local con los permisos habituales. La interfaz se inicia de la misma manera; no requiere servicios ni dependencias nuevos.

## Actualización: mini pantalla de ERP interactiva

El panel anterior se rediseñó como una aplicación incrustada: marco de ventana, barra de sesión, navegación y vistas de recuperación, borrador, solicitud de acceso, ticket ficticio y detalle de propuesta.

- TypeScript estricto: compilación correcta de los dos módulos y sus JavaScript entregados.
- `node tools/simulacion.test.mjs`: 11 casos de interacción aprobados (12 pruebas contando el grupo). Se comprueban también el reintento explícito con título editado, el cambio de cuenta, los formularios inválidos, la cancelación y la limpieza de las vistas. Los elementos de prueba se contrastan con los IDs del HTML real.
- `tools/verificar_estatica.py`: 274 comprobaciones aprobadas.
- Sintaxis del verificador de navegador y `git diff --check`: sin errores.
- `tools/verificar_interfaz.mjs` actualizado para cubrir el reintento real 401 → 403 con una cuenta de evaluador, envío de motivo local, vista de ticket y navegación de propuesta.
- Revisión visual en Chromium, anchos móviles y ese flujo HTTP en navegador: pendientes por las restricciones de sockets/Chromium ya registradas. Las pruebas sin navegador no se presentan como una comprobación visual.

El ZIP se actualizó con fuentes y recursos compilados. El JAR anterior requiere recompilarse para incorporar este rediseño; no se sobrescribe con una compilación sin las verificaciones completas.

## Actualización: corrección de los diagramas UML

- `clases.puml` / `clases.svg`: las referencias se muestran una sola vez como atributos, con visibilidad, multiplicidad y `{readOnly}`. La cabeza del cliente tiene multiplicidad 1; el sucesor protegido tiene 0..1. El contrato abstracto y sus cuatro subclases se contrastaron con las declaraciones Java.
- `secuencia.puml` / `secuencia.svg`: participantes separados para validador, política, repositorio, registro de auditoría y solicitud. Se muestra `autenticar(identidad)`, se distinguen llamadas y retornos y se ubica el registro después del retorno a Auditoría, antes de responder al cliente. Se añadió la nota de alcance sobre título válido, instrumentación omitida y respuestas normales.
- Se actualizaron el generador y las dos copias de los cuatro artefactos: `docs/` y recursos locales de la interfaz. Los SVG y PlantUML se generan desde el mismo modelo de clases y mensajes.
- `python3 -m unittest discover -s tools -p 'test_uml.py'`: seis pruebas aprobadas. Comprueban declaraciones Java, participantes, los tres caminos, orden de auditoría, estilo de retornos y sincronización de artefactos.
- XML de los SVG válido y 274 comprobaciones estructurales aprobadas. No se ejecutó un renderizador PlantUML ni se declara una revisión visual en navegador.
