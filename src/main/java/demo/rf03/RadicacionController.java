package demo.rf03;

import java.util.List;
import java.util.Map;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.annotation.*;

/** Adaptador HTTP. No decide autenticación ni autorización. */
@RestController
@RequestMapping("/api")
public class RadicacionController {
    public record Entrada(String token, String titulo) {}
    private final ClienteRadicacion cliente;
    private final RepositorioPropuestasEnMemoria repositorio;
    private final RegistroAuditoriaEnMemoria auditoria;
    public RadicacionController(ClienteRadicacion cliente, RepositorioPropuestasEnMemoria repositorio,
                                RegistroAuditoriaEnMemoria auditoria) {
        this.cliente = cliente; this.repositorio = repositorio; this.auditoria = auditoria;
    }
    @PostMapping("/radicaciones")
    public ResponseEntity<ClienteRadicacion.Ejecucion> radicar(@RequestBody Entrada entrada) {
        var ejecucion = cliente.ejecutar(entrada.token(), entrada.titulo());
        return ResponseEntity.status(ejecucion.respuesta().codigo()).body(ejecucion);
    }
    @GetMapping("/propuestas") public List<RepositorioPropuestasEnMemoria.Propuesta> propuestas() { return repositorio.listar(); }
    @GetMapping("/auditoria") public List<RegistroAuditoriaEnMemoria.Registro> auditoria() { return auditoria.listar(); }
    @ExceptionHandler(HttpMessageNotReadableException.class)
    public ResponseEntity<Map<String, String>> jsonInvalido() {
        return ResponseEntity.badRequest().body(Map.of("mensaje", "JSON inválido: solo se aceptan token y titulo"));
    }
}
