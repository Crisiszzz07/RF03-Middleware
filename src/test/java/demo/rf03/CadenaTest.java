package demo.rf03;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

class CadenaTest {
    static class Laboratorio {
        final RepositorioPropuestasEnMemoria repositorio = new RepositorioPropuestasEnMemoria();
        final RegistroAuditoriaEnMemoria registro = new RegistroAuditoriaEnMemoria();
        final RadicarPropuestaHandler terminal = spy(new RadicarPropuestaHandler(repositorio));
        final AutorizacionMiddleware autorizacion = spy(new AutorizacionMiddleware(terminal, new PoliticaPermisosSimulada()));
        final AutenticacionMiddleware autenticacion = spy(new AutenticacionMiddleware(autorizacion, new ValidadorTokenSimulado()));
        final AuditoriaMiddleware auditoria = spy(new AuditoriaMiddleware(autenticacion, registro));
        final ClienteRadicacion cliente = new ClienteRadicacion(auditoria, registro, repositorio);
    }
    @ParameterizedTest
    @CsvSource({"DEMO-INVALIDO,401,0,0", "DEMO-EVALUADOR,403,1,0", "DEMO-INVESTIGADOR,200,1,1"})
    void escenariosAuditanSinRadicarRechazosYTrazaCoincideConInvocaciones(String token, int codigo, int autoriza, int radica) {
        var l = new Laboratorio();
        var resultado = l.cliente.ejecutar(token, "Propuesta de investigación demostrativa");
        assertEquals(codigo, resultado.respuesta().codigo());
        assertEquals(radica, l.repositorio.listar().size());
        assertEquals(1, l.registro.listar().size());
        assertEquals(codigo, resultado.auditoria().codigo());
        assertEquals(resultado.solicitudId(), resultado.auditoria().solicitudId());
        verify(l.auditoria).procesar(any()); verify(l.autenticacion).procesar(any());
        verify(l.autorizacion, times(autoriza)).procesar(any());
        verify(l.terminal, times(radica)).procesar(any());
        var esperados = new java.util.ArrayList<>(List.of("AuditoriaMiddleware", "AutenticacionMiddleware"));
        if (autoriza == 1) esperados.add("AutorizacionMiddleware");
        if (radica == 1) esperados.add("RadicarPropuestaHandler");
        assertEquals(esperados, resultado.traza().stream().filter(e -> e.estado().equals("EJECUTANDO")).map(EventoTraza::manejador).toList());
        Set<String> omitidos = resultado.traza().stream().filter(e -> e.estado().equals("NO_EJECUTADO")).map(EventoTraza::manejador).collect(Collectors.toSet());
        assertEquals(codigo == 401 ? Set.of("AutorizacionMiddleware", "RadicarPropuestaHandler") : codigo == 403 ? Set.of("RadicarPropuestaHandler") : Set.of(), omitidos);
        var eventos = resultado.traza();
        assertEquals("ClienteRadicacion", eventos.get(eventos.size() - 1).manejador());
        assertEquals("AuditoriaMiddleware", eventos.get(eventos.size() - 2).manejador());
        assertEquals("RETORNO", eventos.get(eventos.size() - 2).direccion());
        for (int i = 0; i < eventos.size(); i++) {
            assertEquals(i + 1, eventos.get(i).paso());
            assertFalse(eventos.get(i).fragmento().isBlank());
            assertFalse(eventos.get(i).toString().contains(token));
        }
        if (radica == 1) {
            assertNotNull(resultado.respuesta().propuestaId());
            assertEquals("investigadora-demo", l.repositorio.listar().get(0).autor());
        } else assertNull(resultado.respuesta().propuestaId());
    }
    @Test void autorizacionUsaIdentidadDelValidador() {
        var politica = spy(new PoliticaPermisosSimulada());
        var repo = new RepositorioPropuestasEnMemoria();
        var cadena = new AutenticacionMiddleware(new AutorizacionMiddleware(new RadicarPropuestaHandler(repo), politica), new ValidadorTokenSimulado());
        var solicitud = new SolicitudRadicacion("DEMO-EVALUADOR", "Propuesta demostrativa");
        // Incluso un contexto interno prellenado se reemplaza con la identidad validada.
        solicitud.autenticar(new IdentidadSimulada("identidad-manipulada", IdentidadSimulada.Perfil.INVESTIGADOR));
        assertEquals(403, cadena.procesar(solicitud).codigo());
        verify(politica).puedeRadicar(new IdentidadSimulada("evaluador-demo", IdentidadSimulada.Perfil.EVALUADOR));
        assertTrue(repo.listar().isEmpty());
    }
    @Test void solicitudesSucesivasNoMezclanNiMutanTrazas() {
        var l = new Laboratorio();
        var primera = l.cliente.ejecutar("DEMO-INVALIDO", "Primera propuesta");
        var copia = List.copyOf(primera.traza());
        var segunda = l.cliente.ejecutar("DEMO-INVESTIGADOR", "Segunda propuesta");
        assertNotEquals(primera.solicitudId(), segunda.solicitudId());
        assertEquals(copia, primera.traza());
        assertTrue(primera.traza().stream().allMatch(e -> e.titulo().equals("Primera propuesta")));
        assertTrue(segunda.traza().stream().allMatch(e -> e.titulo().equals("Segunda propuesta")));
        assertEquals(1, segunda.traza().get(0).paso());
        assertThrows(UnsupportedOperationException.class, () -> primera.traza().clear());
        assertEquals(2, l.registro.listar().size());
    }
    @Test void concurrenciaAislaContextos() throws Exception {
        var l = new Laboratorio();
        var ejecutor = Executors.newFixedThreadPool(4);
        try {
            var tareas = IntStream.range(0, 24).<java.util.concurrent.Callable<ClienteRadicacion.Ejecucion>>mapToObj(i ->
                    () -> l.cliente.ejecutar(i % 2 == 0 ? "DEMO-INVESTIGADOR" : "DEMO-EVALUADOR", "Propuesta concurrente " + i)).toList();
            var resultados = ejecutor.invokeAll(tareas);
            var ids = new java.util.HashSet<String>();
            for (var futuro : resultados) {
                var r = futuro.get(); ids.add(r.solicitudId());
                assertTrue(r.traza().stream().allMatch(e -> e.titulo().equals(r.traza().get(0).titulo())));
                assertEquals(1, r.traza().get(0).paso());
                assertEquals(r.solicitudId(), r.auditoria().solicitudId());
            }
            assertEquals(24, ids.size()); assertEquals(24, l.registro.listar().size()); assertEquals(12, l.repositorio.listar().size());
        } finally { ejecutor.shutdownNow(); }
    }
    @Test void validacionDeDatosEsPreviaYNoSeConfundeConSeguridad() {
        var l = new Laboratorio();
        for (String titulo : List.of("", "    ", "abc", "a".repeat(121))) {
            var r = l.cliente.ejecutar("DEMO-INVESTIGADOR", titulo);
            assertEquals(400, r.respuesta().codigo()); assertNull(r.auditoria());
            assertEquals(1, r.traza().size()); assertEquals("VALIDACION", r.traza().get(0).direccion());
        }
        verify(l.auditoria, never()).procesar(any()); assertTrue(l.repositorio.listar().isEmpty());
    }
    @Test void tokenAusenteSeRechazaYSeAudita() {
        var l = new Laboratorio(); var r = l.cliente.ejecutar(null, "Propuesta con token ausente");
        assertEquals(401, r.respuesta().codigo()); assertEquals("anónimo", r.auditoria().usuario());
        assertTrue(l.repositorio.listar().isEmpty());
    }
}
