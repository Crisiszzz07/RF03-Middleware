package demo.rf03;

import java.io.IOException;
import java.nio.charset.StandardCharsets;

/** Lee el Java empaquetado por Maven, entre marcadores; no mantiene copias de snippets. */
public final class FragmentosFuente {
    private FragmentosFuente() {}
    public static String leer(String clase, String clave) {
        String ruta = "/static/codigo/demo/rf03/" + clase + ".java";
        try (var entrada = FragmentosFuente.class.getResourceAsStream(ruta)) {
            if (entrada == null) throw new IllegalStateException("Fuente ausente: " + ruta);
            String fuente = new String(entrada.readAllBytes(), StandardCharsets.UTF_8);
            String inicio = "// @fragment " + clave + ":start";
            String fin = "// @fragment " + clave + ":end";
            int a = fuente.indexOf(inicio), b = fuente.indexOf(fin);
            if (a < 0 || b <= a) throw new IllegalStateException("Marcador ausente: " + clave);
            return fuente.substring(a + inicio.length(), b).stripIndent().strip();
        } catch (IOException e) { throw new IllegalStateException("No se puede leer " + ruta, e); }
    }
}
