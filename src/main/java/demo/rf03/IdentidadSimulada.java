package demo.rf03;

public record IdentidadSimulada(String usuario, Perfil perfil) {
    public enum Perfil { INVESTIGADOR, EVALUADOR }
}
