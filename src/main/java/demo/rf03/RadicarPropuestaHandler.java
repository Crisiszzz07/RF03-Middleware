package demo.rf03;

public final class RadicarPropuestaHandler extends ManejadorSeguridad {
    private final RepositorioPropuestasEnMemoria repositorio;
    public RadicarPropuestaHandler(RepositorioPropuestasEnMemoria repositorio) {
        super(null); this.repositorio = repositorio;
    }
    @Override public RespuestaRadicacion procesar(SolicitudRadicacion solicitud) {
        solicitud.evento("RadicarPropuestaHandler", "procesar", "EJECUTANDO", "IDA",
                "Radica la propuesta en memoria", "Todos los filtros permitieron avanzar", null,
                "RadicarPropuestaHandler", "radicar", "Solo este manejador crea una propuesta.");
        // @fragment radicar:start
        String id = repositorio.guardar(solicitud);
        RespuestaRadicacion respuesta = new RespuestaRadicacion(200, "Propuesta radicada en memoria", id);
        // @fragment radicar:end
        solicitud.evento("RadicarPropuestaHandler", "procesar", "COMPLETA", "RETORNO",
                "Crea " + id + " y responde 200", "Manejador terminal: no delega", 200,
                "RadicarPropuestaHandler", "radicar", "200 es una convención de estos escenarios didácticos.");
        return respuesta;
    }
}
