package demo.rf03;

import java.util.List;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

public final class RepositorioPropuestasEnMemoria {
    public record Propuesta(String id, String titulo, String autor) {}
    private final AtomicInteger secuencia = new AtomicInteger();
    private final ConcurrentHashMap<String, Propuesta> propuestas = new ConcurrentHashMap<>();
    public String guardar(SolicitudRadicacion solicitud) {
        String id = "RF03-%04d".formatted(secuencia.incrementAndGet());
        propuestas.put(id, new Propuesta(id, solicitud.titulo(), solicitud.identidad().usuario()));
        return id;
    }
    public List<Propuesta> listar() { return List.copyOf(propuestas.values()); }
}
