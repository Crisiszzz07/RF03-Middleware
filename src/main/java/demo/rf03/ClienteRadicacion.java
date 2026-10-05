package demo.rf03;

import java.util.List;

/** Client del patrón: inicia siempre por la cabeza. No depende de HTTP. */
public final class ClienteRadicacion {
    public record Ejecucion(String solicitudId, RespuestaRadicacion respuesta, List<EventoTraza> traza,
                            RegistroAuditoriaEnMemoria.Registro auditoria, int propuestasRegistradas) {}
    private final ManejadorSeguridad cabeza;
    private final RegistroAuditoriaEnMemoria auditoria;
    private final RepositorioPropuestasEnMemoria repositorio;
    public ClienteRadicacion(ManejadorSeguridad cabeza, RegistroAuditoriaEnMemoria auditoria,
                            RepositorioPropuestasEnMemoria repositorio) {
        this.cabeza = cabeza; this.auditoria = auditoria; this.repositorio = repositorio;
    }
    public Ejecucion ejecutar(String token, String titulo) {
        SolicitudRadicacion solicitud = new SolicitudRadicacion(token, titulo);
        // @fragment validarDatos:start
        if (solicitud.titulo().length() < 5 || solicitud.titulo().length() > 120) {
            solicitud.evento("ClienteRadicacion", "ejecutar", "RECHAZA", "VALIDACION",
                    "Título inválido", "Se requieren entre 5 y 120 caracteres", 400,
                    "ClienteRadicacion", "validarDatos", "Validación de datos previa: la cadena de seguridad no se inició.");
            return new Ejecucion(solicitud.id(), new RespuestaRadicacion(400, "Título: entre 5 y 120 caracteres", null),
                    solicitud.traza(), null, repositorio.listar().size());
        }
        // @fragment validarDatos:end
        solicitud.evento("ClienteRadicacion", "ejecutar", "CONTINUA", "IDA",
                "Inicia por Auditoría", "Los datos del título son válidos", null,
                "ClienteRadicacion", "iniciar", "El cliente conoce la cabeza, no decide el flujo de seguridad.");
        // @fragment iniciar:start
        RespuestaRadicacion respuesta = cabeza.procesar(solicitud);
        // @fragment iniciar:end
        solicitud.evento("ClienteRadicacion", "ejecutar", "COMPLETA", "RETORNO",
                "Recibe el resultado final", "Auditoría ya registró el resultado", respuesta.codigo(),
                "ClienteRadicacion", "iniciar", "Java terminó; el navegador solo reproducirá estos eventos.");
        var registro = auditoria.listar().stream().filter(r -> r.solicitudId().equals(solicitud.id())).findFirst().orElseThrow();
        return new Ejecucion(solicitud.id(), respuesta, solicitud.traza(), registro, repositorio.listar().size());
    }
}
