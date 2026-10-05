package demo.rf03;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class ConfiguracionCadena {
    @Bean public RepositorioPropuestasEnMemoria repositorio() { return new RepositorioPropuestasEnMemoria(); }
    @Bean public RegistroAuditoriaEnMemoria auditoria() { return new RegistroAuditoriaEnMemoria(); }
    @Bean public ClienteRadicacion cliente(RepositorioPropuestasEnMemoria repositorio, RegistroAuditoriaEnMemoria auditoria) {
        // @fragment cadena:start
        var terminal = new RadicarPropuestaHandler(repositorio);
        var autorizacion = new AutorizacionMiddleware(terminal, new PoliticaPermisosSimulada());
        var autenticacion = new AutenticacionMiddleware(autorizacion, new ValidadorTokenSimulado());
        var cabeza = new AuditoriaMiddleware(autenticacion, auditoria);
        return new ClienteRadicacion(cabeza, auditoria, repositorio);
        // @fragment cadena:end
    }
}
