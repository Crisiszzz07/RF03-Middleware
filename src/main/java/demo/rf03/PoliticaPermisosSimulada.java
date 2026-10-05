package demo.rf03;

/** Supuesto didáctico, no una política institucional verificada. */
public final class PoliticaPermisosSimulada {
    public boolean puedeRadicar(IdentidadSimulada identidad) {
        // @fragment permiso:start
        return identidad != null && identidad.perfil() == IdentidadSimulada.Perfil.INVESTIGADOR;
        // @fragment permiso:end
    }
}
