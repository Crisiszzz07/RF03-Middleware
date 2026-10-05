# Referencias y procedencia

- Spring Boot, **System Requirements, versión 3.5**: https://docs.spring.io/spring-boot/3.5/system-requirements.html . Página oficial consultada para compatibilidad: Spring Boot 3.5.16 requiere Java 17 como mínimo y Maven 3.6.3 o posterior.
- Apache Maven, **Maven Wrapper**: https://maven.apache.org/tools/wrapper/ . Explica el bootstrap de Maven y la distribución `only-script` sin JAR de wrapper.
- Apache Maven, **Wrapper Usage**: https://maven.apache.org/components/tools-archives/wrapper-LATEST/maven-wrapper-plugin/usage.html . Uso de scripts y descarga inicial mediante herramientas del sistema.
- Scripts oficiales Apache Maven Wrapper **3.3.4**, distribución `only-script`:
  - https://github.com/apache/maven-wrapper/blob/maven-wrapper-3.3.4/maven-wrapper-distribution/src/resources/only-mvnw
  - https://github.com/apache/maven-wrapper/blob/maven-wrapper-3.3.4/maven-wrapper-distribution/src/resources/only-mvnw.cmd
  Se incluyen como `mvnw` y `mvnw.cmd`, con el marcador de versión de la plantilla sustituido por 3.3.4. Se conservan sus cabeceras Apache-2.0; consulte `WRAPPER-LICENSE.txt`.

Las reglas «investigador puede radicar» y «evaluador no puede» son supuestos del ejemplo y no proceden de documentación de una institución.

Bibliografía consultada:

[1] Gamma, Helm, Johnson, Vlissides (Gang of Four)	Design Patterns: Elements of Reusable Object-Oriented Software. Addison-Wesley.	Object Behavioral Patterns: Chain of Responsibility (págs. 223–232).

[2] Robert C. Martin ("Uncle Bob")	Clean Architecture: A Craftsman's Guide to Software Structure and Design. Prentice Hall (2017).	Capítulo 7 (Single Responsibility) y Capítulo 8 (Open/Closed Principle).

[3] Mark Richards & Neal Ford	Fundamentals of Software Architecture: An Engineering Approach. O'Reilly Media (2020).	Capítulo 6: Análisis de cohesión y acoplamiento en arquitecturas modulares.