package demo.rf03;

/** Handler de CoR. El sucesor se fija al construir una cadena inmutable. */
public abstract class ManejadorSeguridad {
    protected final ManejadorSeguridad siguiente;
    protected ManejadorSeguridad(ManejadorSeguridad siguiente) { this.siguiente = siguiente; }
    public abstract RespuestaRadicacion procesar(SolicitudRadicacion solicitud);

    protected RespuestaRadicacion continuar(SolicitudRadicacion solicitud) {
        // @fragment delegar:start
        if (siguiente == null) throw new IllegalStateException("Falta el manejador terminal");
        RespuestaRadicacion respuesta = siguiente.procesar(solicitud);
        // @fragment delegar:end
        solicitud.evento(getClass().getSimpleName(), "continuar", "COMPLETA", "RETORNO",
                "Recibe la respuesta del sucesor", "La pila de llamadas retorna al filtro anterior",
                respuesta.codigo(), "ManejadorSeguridad", "delegar",
                "El resultado vuelve por los filtros que sí participaron.");
        return respuesta;
    }

    /** Eventos informativos de omisión: no invocan procesar en los sucesores. */
    protected void marcarNoEjecutados(SolicitudRadicacion solicitud, int codigo) {
        // @fragment omitir:start
        for (ManejadorSeguridad omitido = siguiente; omitido != null; omitido = omitido.siguiente) {
            solicitud.evento(omitido.getClass().getSimpleName(), "marcarNoEjecutados",
                    "NO_EJECUTADO", "OMISION", "No se invoca procesar",
                    "Un filtro anterior rechazó la solicitud", codigo,
                    "ManejadorSeguridad", "omitir", "Este eslabón no se ejecutó: no hay delegación.");
        }
        // @fragment omitir:end
    }
}
