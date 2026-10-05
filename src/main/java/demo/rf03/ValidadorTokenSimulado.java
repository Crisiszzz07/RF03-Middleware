package demo.rf03;

import java.util.Map;
import java.util.Optional;

/** Tabla ficticia: no verifica firmas, expiración, revocación ni SSO. */
public final class ValidadorTokenSimulado {
    private final Map<String, IdentidadSimulada> identidades = Map.of(
            "DEMO-INVESTIGADOR", new IdentidadSimulada("investigadora-demo", IdentidadSimulada.Perfil.INVESTIGADOR),
            "DEMO-EVALUADOR", new IdentidadSimulada("evaluador-demo", IdentidadSimulada.Perfil.EVALUADOR));
    public Optional<IdentidadSimulada> validar(String token) {
        // @fragment validar:start
        if (token == null) return Optional.empty();
        return Optional.ofNullable(identidades.get(token));
        // @fragment validar:end
    }
}
