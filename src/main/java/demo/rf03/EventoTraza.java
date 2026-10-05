package demo.rf03;

/** Instantánea inmutable: nunca contiene el token. */
public record EventoTraza(int paso, String manejador, String metodo, String estado,
                          String direccion, String accion, String motivo,
                          String identidad, String titulo, Integer codigo,
                          String archivo, String fragmento, String explicacion) {}
