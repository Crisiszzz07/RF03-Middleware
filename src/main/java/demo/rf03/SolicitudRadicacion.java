package demo.rf03;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/** Contexto nuevo por solicitud. Los manejadores compartidos no almacenan este estado. */
public final class SolicitudRadicacion {
    private final String id = UUID.randomUUID().toString();
    private final String token;
    private final String titulo;
    private IdentidadSimulada identidad;
    private final List<EventoTraza> traza = new ArrayList<>();

    public SolicitudRadicacion(String token, String titulo) {
        this.token = token;
        this.titulo = titulo == null ? "" : titulo.strip();
    }
    public String id() { return id; }
    public String token() { return token; }
    public String titulo() { return titulo; }
    public IdentidadSimulada identidad() { return identidad; }
    public void autenticar(IdentidadSimulada identidad) { this.identidad = identidad; }
    public List<EventoTraza> traza() { return List.copyOf(traza); }

    public void evento(String clase, String metodo, String estado, String direccion,
                       String accion, String motivo, Integer codigo, String fuente,
                       String clave, String explicacion) {
        traza.add(new EventoTraza(traza.size() + 1, clase, metodo, estado, direccion,
                accion, motivo, identidad == null ? "Sin identidad autenticada" :
                identidad.usuario() + " · " + identidad.perfil(), titulo, codigo,
                "demo/rf03/" + fuente + ".java", FragmentosFuente.leer(fuente, clave), explicacion));
    }
}
