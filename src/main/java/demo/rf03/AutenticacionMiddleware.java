package demo.rf03;

public final class AutenticacionMiddleware extends ManejadorSeguridad {
    private final ValidadorTokenSimulado validador;
    public AutenticacionMiddleware(ManejadorSeguridad siguiente, ValidadorTokenSimulado validador) {
        super(siguiente); this.validador = validador;
    }
    @Override public RespuestaRadicacion procesar(SolicitudRadicacion solicitud) {
        solicitud.evento("AutenticacionMiddleware", "procesar", "EJECUTANDO", "IDA",
                "Consulta el validador ficticio", "El token solo existe en el contexto interno", null,
                "ValidadorTokenSimulado", "validar", "La identidad viene del servicio Java, no de un rol del navegador.");
        // @fragment autenticar:start
        var identidad = validador.validar(solicitud.token());
        if (identidad.isEmpty()) {
            solicitud.evento("AutenticacionMiddleware", "procesar", "RECHAZA", "RETORNO",
                    "Rechaza: token inválido", "No se estableció una identidad", 401,
                    "AutenticacionMiddleware", "autenticar", "No se llama al siguiente filtro.");
            marcarNoEjecutados(solicitud, 401);
            return new RespuestaRadicacion(401, "Token de demostración inválido", null);
        }
        solicitud.autenticar(identidad.get());
        solicitud.evento("AutenticacionMiddleware", "procesar", "CONTINUA", "IDA",
                "Establece la identidad validada", "Token ficticio reconocido", null,
                "AutenticacionMiddleware", "autenticar", "El siguiente filtro recibe una identidad validada.");
        return continuar(solicitud);
        // @fragment autenticar:end
    }
}
