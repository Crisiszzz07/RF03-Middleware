package demo.rf03;

import java.time.Instant;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;

public final class RegistroAuditoriaEnMemoria {
    public record Registro(String solicitudId, Instant fecha, String usuario, int codigo, String propuestaId) {}
    private final CopyOnWriteArrayList<Registro> registros = new CopyOnWriteArrayList<>();
    public Registro registrar(SolicitudRadicacion solicitud, RespuestaRadicacion respuesta) {
        Registro registro = new Registro(solicitud.id(), Instant.now(),
                solicitud.identidad() == null ? "anónimo" : solicitud.identidad().usuario(),
                respuesta.codigo(), respuesta.propuestaId());
        registros.add(registro);
        return registro;
    }
    public List<Registro> listar() { return List.copyOf(registros); }
}
