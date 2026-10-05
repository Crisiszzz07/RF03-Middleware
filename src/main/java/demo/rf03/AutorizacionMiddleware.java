package demo.rf03;

public final class AutorizacionMiddleware extends ManejadorSeguridad {
    private final PoliticaPermisosSimulada politica;
    public AutorizacionMiddleware(ManejadorSeguridad siguiente, PoliticaPermisosSimulada politica) {
        super(siguiente); this.politica = politica;
    }
    @Override public RespuestaRadicacion procesar(SolicitudRadicacion solicitud) {
        solicitud.evento("AutorizacionMiddleware", "procesar", "EJECUTANDO", "IDA",
                "Consulta el permiso de radicar", "Usa únicamente solicitud.identidad()", null,
                "PoliticaPermisosSimulada", "permiso", "Tener un token válido no implica tener este permiso.");
        // @fragment autorizar:start
        if (!politica.puedeRadicar(solicitud.identidad())) {
            solicitud.evento("AutorizacionMiddleware", "procesar", "RECHAZA", "RETORNO",
                    "Rechaza: sin permiso", "La identidad validada no puede radicar", 403,
                    "AutorizacionMiddleware", "autorizar", "El evaluador es conocido, pero no tiene este permiso.");
            marcarNoEjecutados(solicitud, 403);
            return new RespuestaRadicacion(403, "La identidad no tiene permiso para radicar", null);
        }
        solicitud.evento("AutorizacionMiddleware", "procesar", "CONTINUA", "IDA",
                "Permite radicar", "La identidad validada es investigadora", null,
                "AutorizacionMiddleware", "autorizar", "Ahora puede alcanzarse el manejador terminal.");
        return continuar(solicitud);
        // @fragment autorizar:end
    }
}
