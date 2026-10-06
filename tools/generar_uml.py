"""Genera PlantUML y vistas SVG locales desde los mismos modelos editables.
SVG trazado con biblioteca estándar; no requiere PlantUML ni servicios remotos.
Las referencias se muestran solo como atributos, sin asociaciones duplicadas.
"""
from pathlib import Path
from html import escape
from textwrap import wrap
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'src/main/resources/static/uml'
PROCESAR = '+ procesar(solicitud: SolicitudRadicacion): RespuestaRadicacion'
# Nombre, rol, posición, ancho, atributos y operaciones. Constructores/getters abreviados.
CLASES = [
    ('ClienteRadicacion', 'Client', 35, 90, 390,
     ['- cabeza: ManejadorSeguridad [1] {readOnly}', '- auditoria: RegistroAuditoriaEnMemoria [1] {readOnly}', '- repositorio: RepositorioPropuestasEnMemoria [1] {readOnly}'],
     ['+ ejecutar(token: String, titulo: String): Ejecucion']),
    ('ManejadorSeguridad', 'abstract · Handler', 505, 90, 435,
     ['# siguiente: ManejadorSeguridad [0..1] {readOnly}'],
     ['{abstract} ' + PROCESAR, '# continuar(solicitud: SolicitudRadicacion): RespuestaRadicacion', '# marcarNoEjecutados(solicitud: SolicitudRadicacion, codigo: int): void']),
    ('ConfiguracionCadena', 'Composición Spring', 1000, 90, 405, [],
     ['+ cliente(repositorio: RepositorioPropuestasEnMemoria, auditoria: RegistroAuditoriaEnMemoria): ClienteRadicacion', '+ repositorio(): RepositorioPropuestasEnMemoria', '+ auditoria(): RegistroAuditoriaEnMemoria']),
    ('AuditoriaMiddleware', 'ConcreteHandler', 35, 450, 320,
     ['- registro: RegistroAuditoriaEnMemoria [1] {readOnly}'], [PROCESAR]),
    ('AutenticacionMiddleware', 'ConcreteHandler', 385, 450, 325,
     ['- validador: ValidadorTokenSimulado [1] {readOnly}'], [PROCESAR]),
    ('AutorizacionMiddleware', 'ConcreteHandler', 740, 450, 330,
     ['- politica: PoliticaPermisosSimulada [1] {readOnly}'], [PROCESAR]),
    ('RadicarPropuestaHandler', 'ConcreteHandler · terminal', 1100, 450, 320,
     ['- repositorio: RepositorioPropuestasEnMemoria [1] {readOnly}'], [PROCESAR]),
    ('RegistroAuditoriaEnMemoria', 'Servicio simulado', 35, 720, 320,
     ['- registros: CopyOnWriteArrayList<Registro>'],
     ['+ registrar(solicitud: SolicitudRadicacion, respuesta: RespuestaRadicacion): Registro', '+ listar(): List<Registro>']),
    ('ValidadorTokenSimulado', 'Servicio simulado', 385, 720, 325,
     ['- identidades: Map<String, IdentidadSimulada>'], ['+ validar(token: String): Optional<IdentidadSimulada>']),
    ('PoliticaPermisosSimulada', 'Servicio simulado', 740, 720, 330, [],
     ['+ puedeRadicar(identidad: IdentidadSimulada): boolean']),
    ('RepositorioPropuestasEnMemoria', 'Almacenamiento en memoria', 1100, 720, 320,
     ['- propuestas: ConcurrentHashMap<String, Propuesta>', '- secuencia: AtomicInteger'],
     ['+ guardar(solicitud: SolicitudRadicacion): String', '+ listar(): List<Propuesta>']),
    ('SolicitudRadicacion', 'Contexto por petición', 35, 1090, 440,
     ['- id: String', '- token: String (no serializado)', '- titulo: String', '- identidad: IdentidadSimulada [0..1]', '- traza: List<EventoTraza>'],
     ['+ autenticar(identidad: IdentidadSimulada): void', '+ evento(...): void', '+ traza(): List<EventoTraza>']),
    ('RespuestaRadicacion', 'record · resultado', 520, 1090, 405,
     ['- codigo: int', '- mensaje: String', '- propuestaId: String [0..1]'], []),
    ('EventoTraza', 'record · instantánea', 975, 1090, 445,
     ['- paso: int; manejador, metodo: String', '- estado, direccion, accion, motivo: String', '- identidad, titulo: String; codigo: Integer', '- archivo, fragmento, explicacion: String'], []),
    ('IdentidadSimulada', 'record · perfil del validador', 520, 1290, 405,
     ['- usuario: String', '- perfil: Perfil (INVESTIGADOR | EVALUADOR)'], []),
    ('RadicacionController', 'Adaptador HTTP externo al patrón', 35, 1430, 440,
     ['- cliente: ClienteRadicacion [1] {readOnly}', '- repositorio: RepositorioPropuestasEnMemoria [1] {readOnly}', '- auditoria: RegistroAuditoriaEnMemoria [1] {readOnly}'],
     ['+ radicar(entrada: Entrada): ResponseEntity<Ejecucion>', '+ propuestas(), auditoria(), jsonInvalido()']),
    ('FragmentosFuente', 'Utilidad de documentación', 975, 1430, 445, [], ['{static} + leer(clase: String, clave: String): String']),
]
SUBCLASES = [c[0] for c in CLASES[3:7]]

# Participantes separados; los mensajes y alternativas son el modelo de ambas vistas.
PARTICIPANTES = [
    ('C', 'ClienteRadicacion', 100), ('A', 'AuditoriaMiddleware', 290),
    ('N', 'AutenticacionMiddleware', 480), ('V', 'ValidadorTokenSimulado', 670),
    ('Q', 'SolicitudRadicacion', 860), ('Z', 'AutorizacionMiddleware', 1050),
    ('P', 'PoliticaPermisosSimulada', 1240), ('R', 'RadicarPropuestaHandler', 1430),
    ('D', 'RepositorioPropuestasEnMemoria', 1620), ('L', 'RegistroAuditoriaEnMemoria', 1810),
]

def llamada(origen, destino, texto): return ('mensaje', origen, destino, texto, False)
def retorno(origen, destino, texto): return ('mensaje', origen, destino, texto, True)
def nota(texto): return ('nota', texto)
def alternativa(ramas): return ('alt', ramas)

SECUENCIA = [
    llamada('C', 'A', 'procesar(solicitud)'),
    llamada('A', 'N', 'procesar(solicitud)'),
    llamada('N', 'V', 'validar(solicitud.token())'),
    retorno('V', 'N', 'Optional<IdentidadSimulada>'),
    alternativa([
        ('identidad ausente · token inválido → 401', [
            retorno('N', 'A', 'RespuestaRadicacion(401)'),
            nota('AutorizacionMiddleware y RadicarPropuestaHandler no se invocan.'),
        ]),
        ('identidad presente · token válido', [
            llamada('N', 'Q', 'autenticar(identidad)'),
            retorno('Q', 'N', 'void'),
            llamada('N', 'Z', 'procesar(solicitud)'),
            llamada('Z', 'P', 'puedeRadicar(solicitud.identidad())'),
            retorno('P', 'Z', 'permiso: boolean'),
            alternativa([
                ('sin permiso · evaluador → 403', [
                    retorno('Z', 'N', 'RespuestaRadicacion(403)'),
                    retorno('N', 'A', 'respuesta 403'),
                    nota('RadicarPropuestaHandler no se invoca.'),
                ]),
                ('con permiso · investigador → 200', [
                    llamada('Z', 'R', 'procesar(solicitud)'),
                    llamada('R', 'D', 'guardar(solicitud)'),
                    retorno('D', 'R', 'id: String'),
                    retorno('R', 'Z', 'RespuestaRadicacion(200, id)'),
                    retorno('Z', 'N', 'respuesta 200'),
                    retorno('N', 'A', 'respuesta 200'),
                ]),
            ]),
        ]),
    ]),
    llamada('A', 'L', 'registrar(solicitud, respuesta)'),
    retorno('L', 'A', 'Registro (sin token)'),
    retorno('A', 'C', 'respuesta 401 / 403 / 200'),
]
NOTA_ALCANCE = ('Escenarios con título válido. Se omite la instrumentación de la traza. '
                'Auditoría registra respuestas normales 401, 403 y 200; este diagrama no representa excepciones inesperadas.')


def cabecera_svg(ancho, alto, titulo, descripcion):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho} {alto}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{escape(titulo)}</title><desc id="desc">{escape(descripcion)}</desc>',
            '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M1 1 L9 5 L1 9" fill="none" stroke="#66418b" stroke-width="1.5"/></marker><marker id="inherit" markerWidth="16" markerHeight="14" refX="14" refY="7" orient="auto"><path d="M1 1 L14 7 L1 13 Z" fill="white" stroke="#66418b" stroke-width="1.5"/></marker></defs>',
            f'<rect width="{ancho}" height="{alto}" fill="#faf8fe"/>',
            '<style>text{font-family:system-ui,Segoe UI,sans-serif;fill:#30213f}.title{font-size:21px;font-weight:700}.member{font-size:14px}.role{font-size:13px;fill:#6b4b88}.edge{fill:none;stroke:#66418b;stroke-width:2}</style>']


def texto_svg(x, y, texto, clase='member', extra=''):
    return f'<text x="{x}" y="{y}" class="{clase}" {extra}>{escape(texto)}</text>'


def miembros(clase):
    _, _, _, _, ancho, atributos, operaciones = clase
    limite = int((ancho - 24) / 7.3)
    return ([linea for m in atributos for linea in wrap(m, limite)],
            [linea for m in operaciones for linea in wrap(m, limite)])


def alto_clase(clase):
    atributos, operaciones = miembros(clase)
    return 92 + 24 * (len(atributos) + len(operaciones))


def generar_clases():
    puml = ['@startuml', 'title RF03 · clases reales', 'skinparam classAttributeIconSize 0', 'hide empty members']
    for nombre, rol, _, _, _, atributos, operaciones in CLASES:
        puml.append(('abstract class ' if nombre == 'ManejadorSeguridad' else 'class ') + nombre + ' {')
        puml.extend('  ' + s for s in atributos + operaciones)
        puml.append('}')
    puml.extend(f'{nombre} --|> ManejadorSeguridad' for nombre in SUBCLASES)
    puml.extend(['ConfiguracionCadena ..> ClienteRadicacion : construye',
                 'ConfiguracionCadena ..> ManejadorSeguridad : compone la cadena',
                 'note bottom of ManejadorSeguridad',
                 'Referencias mostradas solo como atributos; sin asociaciones duplicadas.',
                 'El sucesor se fija mediante el constructor; no hay setters.',
                 'RadicarPropuestaHandler es terminal: siguiente = null.',
                 'end note', 'legend bottom',
                 'Constructores, getters y records anidados abreviados.',
                 'Servicios y almacenamiento simulados; no son seguridad de producción.',
                 'endlegend', '@enduml'])
    svg = cabecera_svg(1460, 1810, 'RF03: UML de clases', 'Referencias con visibilidad, multiplicidad y readOnly. Cuatro subclases del Handler abstracto; servicios simulados.')
    svg.extend([texto_svg(35, 38, 'RF03 · UML de clases', 'title'),
                texto_svg(35, 65, 'Referencias solo como atributos: visibilidad, multiplicidad y {readOnly}. Sin asociaciones duplicadas.', 'role')])
    base = CLASES[1]
    base_fin = base[3] + alto_clase(base)
    for clase in CLASES[3:7]:
        cx = clase[2] + clase[4] / 2
        svg.append(f'<path data-subclass="{clase[0]}" d="M{cx} 450 V410 H722 V{base_fin}" class="edge" marker-end="url(#inherit)"/>')
    svg.append('<path d="M1000 275 H965 V320 H940" class="edge" stroke-dasharray="6 4" marker-end="url(#arrow)"/>')
    svg.append(texto_svg(1030, 405, 'Construye y compone la cadena', 'role'))
    svg.append(texto_svg(35, 695, 'Servicios referenciados por los manejadores · todos simulados', 'title'))
    svg.append(texto_svg(35, 1060, 'Contexto, respuesta y apoyo · tipos reales del proyecto', 'title'))
    for clase in CLASES:
        nombre, rol, x, y, ancho, _, _ = clase
        atributos, operaciones = miembros(clase)
        alto = alto_clase(clase)
        svg.extend([f'<g data-class="{nombre}">', f'<rect x="{x}" y="{y}" width="{ancho}" height="{alto}" rx="6" fill="white" stroke="#b9a6cd"/>',
                    f'<rect x="{x}" y="{y}" width="{ancho}" height="70" rx="6" fill="#eee5fa"/>'])
        tam = 14 if len(nombre) > 30 else 16 if len(nombre) > 24 else 19
        estilo = f'style="font-size:{tam}px"' + (' font-style="italic"' if nombre == 'ManejadorSeguridad' else '')
        svg.extend([texto_svg(x + 12, y + 27, nombre, 'title', estilo), texto_svg(x + 12, y + 50, rol, 'role')])
        yy = y + 92
        for linea in atributos:
            svg.append(texto_svg(x + 12, yy, linea)); yy += 24
        if atributos and operaciones:
            svg.append(f'<path d="M{x} {yy - 12} H{x + ancho}" stroke="#ded4e8"/>')
        for linea in operaciones:
            svg.append(texto_svg(x + 12, yy, linea)); yy += 24
        svg.append('</g>')
    for i, linea in enumerate(['Triángulo vacío = herencia; línea discontinua = dependencia. Constructores, getters y records anidados abreviados.',
                               'El sucesor se fija mediante constructor; no hay setters. Terminal: siguiente = null.',
                               'Servicios y almacenamiento simulados; no representan seguridad de producción.']):
        svg.append(texto_svg(35, 1730 + 26 * i, linea, 'role'))
    svg.append('</svg>')
    return '\n'.join(puml) + '\n', '\n'.join(svg) + '\n'


def bloques_puml(bloques, sangria=''):
    lineas = []
    for bloque in bloques:
        if bloque[0] == 'mensaje':
            _, origen, destino, etiqueta, es_retorno = bloque
            lineas.append(f'{sangria}{origen} {"-->" if es_retorno else "->"} {destino} : {etiqueta}')
        elif bloque[0] == 'nota':
            lineas.append(sangria + 'note over Z,R : ' + bloque[1])
        else:
            for i, (condicion, rama) in enumerate(bloque[1]):
                lineas.append(sangria + ('alt ' if i == 0 else 'else ') + condicion)
                lineas.extend(bloques_puml(rama, sangria + '  '))
            lineas.append(sangria + 'end')
    return lineas


def generar_secuencia():
    puml = ['@startuml', 'title RF03 · retorno normal 401 / 403 / 200', 'hide footbox']
    puml.extend(f'participant {nombre} as {alias}' for alias, nombre, _ in PARTICIPANTES)
    puml.append('note over C,L')
    puml.extend(wrap(NOTA_ALCANCE, 86))
    puml.append('end note')
    puml.extend(bloques_puml(SECUENCIA))
    puml.extend(['note over C,L', 'Las llamadas entre manejadores se realizan mediante continuar(solicitud).',
                 'Getters simples y constructores omitidos. El título se valida antes de la cadena: 400 no entra aquí.',
                 'end note', '@enduml'])
    xs = {alias: x for alias, _, x in PARTICIPANTES}
    mensajes, marcos = [], []

    def dibujar_bloques(bloques, y, profundidad=0):
        for bloque in bloques:
            if bloque[0] == 'mensaje':
                _, origen, destino, etiqueta, es_retorno = bloque
                xa, xb = xs[origen], xs[destino]
                limite = max(17, int(abs(xa - xb) / 8))
                lineas = wrap(etiqueta, limite)
                y += 22 + 19 * len(lineas)
                mensajes.append(f'<g data-from="{origen}" data-to="{destino}" data-kind="{"retorno" if es_retorno else "llamada"}">')
                for i, linea in enumerate(lineas):
                    mensajes.append(texto_svg((xa + xb) / 2, y - 12 - 19 * (len(lineas) - 1 - i), linea, extra='text-anchor="middle"'))
                mensajes.append(f'<path d="M{xa} {y} H{xb}" class="edge" marker-end="url(#arrow)"' + (' stroke-dasharray="7 5"' if es_retorno else '') + '/></g>')
                y += 22
            elif bloque[0] == 'nota':
                mensajes.append(f'<rect x="1040" y="{y + 5}" width="820" height="40" rx="5" fill="#fff0f4" stroke="#dfbdca"/>')
                mensajes.append(texto_svg(1055, y + 31, bloque[1], 'role'))
                y += 57
            else:
                inicio = y
                x = 35 + profundidad * 35
                ancho = 1830 - profundidad * 70
                separadores = []
                for i, (condicion, rama) in enumerate(bloque[1]):
                    if i: separadores.append(y)
                    mensajes.append(texto_svg(x + 15, y + 27, ('alt · ' if i == 0 else 'else · ') + condicion, 'role', 'font-weight="700"'))
                    y = dibujar_bloques(rama, y + 38, profundidad + 1) + 14
                marcos.append(f'<rect data-fragment="alt" x="{x}" y="{inicio}" width="{ancho}" height="{y - inicio}" fill="none" stroke="#ad94c6" stroke-width="2"/>')
                marcos.extend(f'<path d="M{x} {yy} H{x + ancho}" stroke="#ad94c6" stroke-dasharray="5 4"/>' for yy in separadores)
                y += 18
        return y

    fin = dibujar_bloques(SECUENCIA, 175)
    alto = fin + 180
    svg = cabecera_svg(1900, alto, 'RF03: UML de secuencia', NOTA_ALCANCE)
    svg.append(texto_svg(30, 36, 'RF03 · Secuencia: servicios separados y retorno auditado', 'title'))
    # Marcos y líneas de vida primero; mensajes encima para que sus etiquetas no queden tapadas.
    svg.extend(marcos)
    for alias, nombre, x in PARTICIPANTES:
        svg.extend([f'<g data-participant="{alias}" data-name="{nombre}">',
                    f'<rect x="{x - 86}" y="65" width="172" height="85" rx="5" fill="#eee5fa" stroke="#b9a6cd"/>',
                    texto_svg(x, 88, alias, 'role', 'text-anchor="middle"'),
                    f'<path d="M{x} 150 V{fin + 10}" stroke="#c5b4d6" stroke-dasharray="6 5"/>'])
        # División por palabras de CamelCase para conservar los nombres completos y legibles.
        palabras = re.findall(r'[A-ZÁÉÍÓÚ][a-záéíóúñ]*|[0-9]+', nombre)
        lineas, actual = [], ''
        for palabra in palabras:
            if len(actual + palabra) > 20 and actual: lineas.append(actual); actual = palabra
            else: actual += palabra
        if actual: lineas.append(actual)
        for i, linea in enumerate(lineas):
            svg.append(texto_svg(x, 113 + 18 * i, linea, extra='text-anchor="middle" font-weight="650"'))
        svg.append('</g>')
    svg.extend(mensajes)
    for i, linea in enumerate(wrap(NOTA_ALCANCE, 165)):
        svg.append(texto_svg(30, fin + 43 + 25 * i, linea, 'role'))
    svg.extend([texto_svg(30, fin + 115, 'Llamadas: líneas continuas. Retornos: líneas discontinuas. Getters simples, constructores e instrumentación omitidos.', 'role'),
                texto_svg(30, fin + 145, 'Entre manejadores, continuar(solicitud) invoca procesar del sucesor. Validación de título → 400 ocurre antes de la cadena.', 'role'), '</svg>'])
    return '\n'.join(puml) + '\n', '\n'.join(svg) + '\n'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for nombre, generador in [('clases', generar_clases), ('secuencia', generar_secuencia)]:
        puml, svg = generador()
        for extension, contenido in [('puml', puml), ('svg', svg)]:
            for carpeta in [OUT, ROOT / 'docs']:
                (carpeta / f'{nombre}.{extension}').write_text(contenido, encoding='utf-8')
    print('Generados y sincronizados: clases y secuencia, PlantUML y SVG.')


if __name__ == '__main__':
    main()
