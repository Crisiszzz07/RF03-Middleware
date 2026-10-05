package demo.rf03;

public final class AuditoriaMiddleware extends ManejadorSeguridad {
    private final RegistroAuditoriaEnMemoria registro;
    public AuditoriaMiddleware(ManejadorSeguridad siguiente, RegistroAuditoriaEnMemoria registro) {
        super(siguiente); this.registro = registro;
    }
    @Override public RespuestaRadicacion procesar(SolicitudRadicacion solicitud) {
        solicitud.evento("AuditoriaMiddleware", "procesar", "EJECUTANDO", "IDA",
                "Abre la envoltura de auditoría", "Debe observar éxitos y rechazos", null,
                "AuditoriaMiddleware", "envolver", "Auditoría espera el resultado del resto de la cadena.");
        // @fragment envolver:start
        RespuestaRadicacion respuesta = continuar(solicitud);
        registro.registrar(solicitud, respuesta);
        // @fragment envolver:end
        solicitud.evento("AuditoriaMiddleware", "procesar", "COMPLETA", "RETORNO",
                "Registra el resultado " + respuesta.codigo(), "La llamada al sucesor ya retornó",
                respuesta.codigo(), "AuditoriaMiddleware", "envolver",
                "El mismo filtro registra 401, 403 y 200. Nunca guarda el token.");
        return respuesta;
    }
}
