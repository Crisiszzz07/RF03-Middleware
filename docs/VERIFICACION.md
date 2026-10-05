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