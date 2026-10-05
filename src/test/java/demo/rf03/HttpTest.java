package demo.rf03;

import static org.junit.jupiter.api.Assertions.*;
import java.util.Map;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.http.*;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class HttpTest {
    @Autowired TestRestTemplate http;
    @Autowired RepositorioPropuestasEnMemoria repositorio;
    @Autowired RegistroAuditoriaEnMemoria auditoria;

    @Test void escenariosPorHttpYRecursosLocales() {
        String[] tokens = {"DEMO-INVALIDO", "DEMO-EVALUADOR", "DEMO-INVESTIGADOR"};
        int[] codigos = {401, 403, 200};
        int inicial = repositorio.listar().size(), registros = auditoria.listar().size();
        for (int i = 0; i < tokens.length; i++) {
            var r = http.postForEntity("/api/radicaciones", Map.of("token", tokens[i], "titulo", "Propuesta por HTTP " + i), ClienteRadicacion.Ejecucion.class);
            assertEquals(codigos[i], r.getStatusCode().value());
            var cuerpo = r.getBody(); assertNotNull(cuerpo);
            assertEquals(codigos[i], cuerpo.respuesta().codigo()); assertEquals(codigos[i], cuerpo.auditoria().codigo());
            assertEquals(inicial + (i == 2 ? 1 : 0), repositorio.listar().size());
            assertEquals(registros + i + 1, auditoria.listar().size());
            assertFalse(http.getForObject("/api/auditoria", String.class).contains(tokens[i]));
        }
        for (String recurso : new String[]{"/", "/app.js", "/styles.css", "/uml/clases.svg", "/uml/secuencia.svg", "/uml/clases.puml", "/codigo/demo/rf03/ManejadorSeguridad.java"}) {
            assertEquals(200, http.getForEntity(recurso, String.class).getStatusCode().value(), recurso);
        }
    }
    @Test void rolDelNavegadorNoEsAceptado() {
        int n = repositorio.listar().size(), a = auditoria.listar().size();
        var r = http.postForEntity("/api/radicaciones", Map.of("token", "DEMO-EVALUADOR", "titulo", "Propuesta manipulada", "rol", "INVESTIGADOR"), String.class);
        assertEquals(400, r.getStatusCode().value()); assertEquals(n, repositorio.listar().size()); assertEquals(a, auditoria.listar().size());
        var legitima = http.postForEntity("/api/radicaciones", Map.of("token", "DEMO-EVALUADOR", "titulo", "Propuesta de un evaluador"), ClienteRadicacion.Ejecucion.class);
        assertEquals(403, legitima.getStatusCode().value());
    }
    @Test void datosInvalidosYJsonMalformadoSon400() {
        var r = http.postForEntity("/api/radicaciones", Map.of("token", "DEMO-INVESTIGADOR", "titulo", "  "), ClienteRadicacion.Ejecucion.class);
        assertEquals(400, r.getStatusCode().value()); assertNull(r.getBody().auditoria());
        var headers = new HttpHeaders(); headers.setContentType(MediaType.APPLICATION_JSON);
        assertEquals(400, http.postForEntity("/api/radicaciones", new HttpEntity<>("{malformado", headers), String.class).getStatusCode().value());
    }
}
