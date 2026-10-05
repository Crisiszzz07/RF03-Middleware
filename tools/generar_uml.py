"""Genera PlantUML editable y SVG local desde un modelo común, sin servicios remotos.
Las vistas SVG se dibujan con la biblioteca estándar, no requieren PlantUML instalado.
"""
from pathlib import Path
from html import escape
from textwrap import wrap
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'src/main/resources/static/uml'
OUT.mkdir(parents=True,exist_ok=True)
classes=[
('ClienteRadicacion','Client',35,75,390,['- cabeza: ManejadorSeguridad','- auditoria: RegistroAuditoriaEnMemoria','- repositorio: RepositorioPropuestasEnMemoria'],['+ ejecutar(token, titulo): Ejecucion']),
('ManejadorSeguridad','abstract · Handler',505,75,435,['# siguiente: ManejadorSeguridad [0..1]'],['+ procesar(solicitud): RespuestaRadicacion {abstract}','# continuar(solicitud): RespuestaRadicacion','# marcarNoEjecutados(solicitud, codigo): void']),
('ConfiguracionCadena','Composición Spring',1000,75,405,[],['+ cliente(repositorio, auditoria): ClienteRadicacion','+ repositorio(): RepositorioPropuestasEnMemoria','+ auditoria(): RegistroAuditoriaEnMemoria']),
('AuditoriaMiddleware','ConcreteHandler',35,350,320,['- registro: RegistroAuditoriaEnMemoria'],['+ procesar(solicitud): RespuestaRadicacion']),
('AutenticacionMiddleware','ConcreteHandler',385,350,325,['- validador: ValidadorTokenSimulado'],['+ procesar(solicitud): RespuestaRadicacion']),
('AutorizacionMiddleware','ConcreteHandler',740,350,330,['- politica: PoliticaPermisosSimulada'],['+ procesar(solicitud): RespuestaRadicacion']),
('RadicarPropuestaHandler','ConcreteHandler · terminal',1100,350,320,['- repositorio: RepositorioPropuestasEnMemoria'],['+ procesar(solicitud): RespuestaRadicacion']),
('RegistroAuditoriaEnMemoria','Servicio simulado',35,610,320,['- registros: CopyOnWriteArrayList<Registro>'],['+ registrar(solicitud, respuesta): Registro','+ listar(): List<Registro>']),
('ValidadorTokenSimulado','Servicio simulado',385,610,325,['- identidades: Map<String, IdentidadSimulada>'],['+ validar(token): Optional<IdentidadSimulada>']),
('PoliticaPermisosSimulada','Servicio simulado',740,610,330,[],['+ puedeRadicar(identidad): boolean']),
('RepositorioPropuestasEnMemoria','Servicio simulado',1100,610,320,['- propuestas: ConcurrentHashMap<String, Propuesta>','- secuencia: AtomicInteger'],['+ guardar(solicitud): String','+ listar(): List<Propuesta>']),
('SolicitudRadicacion','Contexto por petición',35,900,440,['- id: String · UUID','- token: String (no serializado)','- titulo: String','- identidad: IdentidadSimulada','- traza: List<EventoTraza>'],['+ autenticar(identidad): void','+ evento(...): void','+ traza(): List<EventoTraza>','+ id(), token(), titulo(), identidad()']),
('RespuestaRadicacion','record · resultado',520,900,405,['- codigo: int','- mensaje: String','- propuestaId: String [0..1]'],[]),
('EventoTraza','record · instantánea',975,900,445,['- paso: int; manejador, metodo: String','- estado, direccion, accion, motivo: String','- identidad, titulo: String; codigo: Integer','- archivo, fragmento, explicacion: String'],[]),
('IdentidadSimulada','record · perfil del validador',520,1120,405,['- usuario: String','- perfil: Perfil (INVESTIGADOR | EVALUADOR)'],[]),
('RadicacionController','Adaptador HTTP externo al patrón',35,1285,440,['- cliente: ClienteRadicacion','- repositorio: RepositorioPropuestasEnMemoria','- auditoria: RegistroAuditoriaEnMemoria'],['+ radicar(Entrada): ResponseEntity<Ejecucion>','+ propuestas(), auditoria(), jsonInvalido()']),
('FragmentosFuente','Utilidad de documentación',975,1285,445,[],['+ leer(clase, clave): String {static}'])]
relations=[('ClienteRadicacion','-->','ManejadorSeguridad','cabeza'),('ManejadorSeguridad','-->','ManejadorSeguridad','siguiente [0..1]'),('ConfiguracionCadena','..>','ClienteRadicacion','construye'),('ConfiguracionCadena','..>','AuditoriaMiddleware','cabeza'),('RadicacionController','-->','ClienteRadicacion','invoca'),('SolicitudRadicacion','*--','EventoTraza','traza'),('SolicitudRadicacion','-->','IdentidadSimulada','identidad'),('SolicitudRadicacion','..>','FragmentosFuente','extrae fragmentos'),('ClienteRadicacion','..>','SolicitudRadicacion','crea'),('ManejadorSeguridad','..>','RespuestaRadicacion','retorna')]
for name,*_ in classes[3:7]: relations.append((name,'--|>','ManejadorSeguridad','hereda'))
for a,b in [('AuditoriaMiddleware','RegistroAuditoriaEnMemoria'),('AutenticacionMiddleware','ValidadorTokenSimulado'),('AutorizacionMiddleware','PoliticaPermisosSimulada'),('RadicarPropuestaHandler','RepositorioPropuestasEnMemoria')]: relations.append((a,'--> ',b,'usa'))
puml=['@startuml','title RF03 · clases reales (getters, constructores y records anidados abreviados)','skinparam classAttributeIconSize 0','hide empty members']
for name,role,x,y,w,attrs,methods in classes:
 puml.append(('abstract class ' if name=='ManejadorSeguridad' else 'class ')+name+' {')
 puml.extend('  '+s for s in attrs+methods);puml.append('}')
for a,r,b,label in relations: puml.append(f'{a} {r.strip()} {b} : {label}')
puml.append('@enduml');(OUT/'clases.puml').write_text('\n'.join(puml)+'\n')
svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1460 1525" role="img" aria-labelledby="title desc">', '<title id="title">RF03: diagrama UML de clases</title><desc id="desc">Las flechas triangulares vacías denotan herencia. ManejadorSeguridad referencia siguiente. Los filtros usan servicios simulados.</desc>', '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M1 1 L9 5 L1 9" fill="none" stroke="#66418b" stroke-width="1.5"/></marker><marker id="inherit" markerWidth="16" markerHeight="14" refX="14" refY="7" orient="auto"><path d="M1 1 L14 7 L1 13 Z" fill="white" stroke="#66418b" stroke-width="1.5"/></marker></defs>', '<rect width="1460" height="1525" fill="#faf8fe"/>', '<style>text{font-family:system-ui,Segoe UI,sans-serif;fill:#30213f} .title{font-size:19px;font-weight:700}.member{font-size:14px}.role{font-size:13px;fill:#6b4b88}.edge{fill:none;stroke:#66418b;stroke-width:2}</style>','<text x="35" y="38" class="title">RF03 · UML de clases</text>']
def edge(d,marker='arrow',dash=False): svg.append(f'<path d="{d}" class="edge" marker-end="url(#{marker})"'+(' stroke-dasharray="6 4"' if dash else '')+'/>')
edge('M425 155 H505');svg.append('<text x="440" y="140" class="role">cabeza</text>')
edge('M790 75 V52 H958 V125 H940');svg.append('<text x="975" y="60" class="role">siguiente 0..1</text>')
edge('M1000 230 V290 H405 V240',dash=True);svg.append('<text x="790" y="280" class="role">construye y ordena la cadena</text>')
for i,c in enumerate(classes[3:7]):
 name,role,x,y,w,attrs,methods=c
 center=x+w/2
 edge(f'M{center} 350 V320 H{center} V305 H722 V265','inherit')
 edge(f'M{center} {350+80+sum(len(wrap(s,width=int((w-24)/6.8))) for s in attrs+methods)*25+12} V610');svg.append(f'<text x="{center+10}" y="570" class="role">usa</text>')
svg.append('<text x="35" y="875" class="title">Datos y apoyo · dependencias descritas en las fuentes PlantUML</text>')
edge('M475 1000 H520');svg.append('<text x="480" y="985" class="role">retorna</text>') # client result context? this edge misleading Solicitud returns! remove below
svg=svg[:-2]
edge('M475 1070 H498 V1190 H520');svg.append('<text x="480" y="1150" class="role">identidad</text>')
edge('M475 965 H493 V840 H955 V965 H975');svg.append('<text x="635" y="830" class="role">SolicitudRadicacion contiene traza: List&lt;EventoTraza&gt;</text>')
for name,role,x,y,w,attrs,methods in classes:
 attrs=[line for item in attrs for line in wrap(item,width=int((w-24)/6.8))]
 methods=[line for item in methods for line in wrap(item,width=int((w-24)/6.8))]
 h=80+len(attrs)*25+len(methods)*25+12
 # Maintain fixed layout breathing room; concrete classes have room for long member names.
 svg.append(f'<g><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="white" stroke="#b9a6cd"/><rect x="{x}" y="{y}" width="{w}" height="70" rx="6" fill="#eee5fa"/><text x="{x+12}" y="{y+26}" class="title"'+(' style="font-size:14px"' if len(name)>30 else ' style="font-size:16px"' if len(name)>24 else '')+(' font-style="italic"' if name=='ManejadorSeguridad' else '')+'>'+escape(name)+'</text>'+f'<text x="{x+12}" y="{y+50}" class="role">'+escape(role)+'</text>')
 yy=y+91
 for s in attrs: svg.append(f'<text x="{x+12}" y="{yy}" class="member">{escape(s)}</text>'); yy+=25
 if attrs and methods: svg.append(f'<path d="M{x} {yy-14} H{x+w}" stroke="#ded4e8"/>')
 for s in methods: svg.append(f'<text x="{x+12}" y="{yy}" class="member">{escape(s)}</text>'); yy+=25
 svg.append('</g>')
svg.append('<text x="35" y="1500" class="role">Triángulo vacío = herencia · flecha = referencia/dependencia · constructores y records anidados abreviados</text></svg>')
(OUT/'clases.svg').write_text('\n'.join(svg)+'\n')
seq='''@startuml
title RF03 · radicar una propuesta (datos válidos)
participant ClienteRadicacion as C
participant AuditoriaMiddleware as A
participant AutenticacionMiddleware as N
participant AutorizacionMiddleware as Z
participant RadicarPropuestaHandler as R
participant RegistroAuditoriaEnMemoria as L
C -> A : procesar(solicitud)
activate A
A -> N : continuar → procesar(solicitud)
activate N
N -> N : validador.validar(token)
alt token inválido
  N --> A : RespuestaRadicacion(401)
  note over Z,R : No ejecutados: no se llama a procesar
else token válido
  N -> N : solicitud.autenticar(identidad)
  N -> Z : continuar → procesar(solicitud)
  activate Z
  Z -> Z : politica.puedeRadicar(solicitud.identidad())
  alt sin permiso (evaluador)
    Z --> N : RespuestaRadicacion(403)
    note over R : No ejecutado
    N --> A : respuesta 403
  else con permiso (investigador)
    Z -> R : continuar → procesar(solicitud)
    activate R
    R -> R : repositorio.guardar(solicitud)
    R --> Z : RespuestaRadicacion(200, id)
    deactivate R
    Z --> N : respuesta 200
    N --> A : respuesta 200
  end
  deactivate Z
end
deactivate N
A -> L : registrar(solicitud, respuesta)
L --> A : Registro (sin token)
A --> C : respuesta 401 / 403 / 200
deactivate A
note over A : Auditoría trabaja al retornar el sucesor
note over C : validar título ocurre antes; datos inválidos → 400, sin cadena
@enduml
'''
(OUT/'secuencia.puml').write_text(seq)
svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1460 1330" role="img" aria-labelledby="title desc"><title id="title">RF03: secuencia 401, 403 y 200</title><desc id="desc">Las tres alternativas retornan a Auditoría, que registra y responde al cliente.</desc><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M1 1 L9 5 L1 9" fill="none" stroke="#66418b" stroke-width="1.5"/></marker></defs><rect width="1460" height="1330" fill="#faf8fe"/><style>text{font:17px system-ui,Segoe UI,sans-serif;fill:#30213f}.small{font-size:15px}.title{font-size:23px;font-weight:700}.heading{font-size:16px;font-weight:700}</style><text x="30" y="40" class="title">RF03 · Secuencia: ida, decisiones y retorno auditado</text>']
xs=[120,365,610,855,1100,1330]
names=['ClienteRadicacion','AuditoriaMiddleware','AutenticacionMiddleware','AutorizacionMiddleware','RadicarPropuestaHandler','RegistroAuditoriaEnMemoria']
for x,name in zip(xs,names):
 svg.append(f'<rect x="{x-110}" y="70" width="220" height="65" rx="5" fill="#eee5fa" stroke="#b9a6cd"/><text x="{x}" y="108" text-anchor="middle" class="heading" style="font-size:14px">{name}</text><path d="M{x} 135 V1230" stroke="#c5b4d6" stroke-dasharray="6 5"/>')
def msg(a,b,y,label,ret=False):
 xa,xb=xs[a],xs[b]
 svg.append(f'<path d="M{xa} {y} H{xb}" fill="none" stroke="#66418b" stroke-width="2" marker-end="url(#arrow)"'+(' stroke-dasharray="6 4"' if ret else '')+'/>')
 svg.append(f'<text x="{(xa+xb)/2}" y="{y-9}" text-anchor="middle" class="small">{escape(label)}</text>')
def note(x,y,s): svg.append(f'<rect x="{x}" y="{y}" width="360" height="38" rx="5" fill="#f3eef9"/><text x="{x+12}" y="{y+25}" class="small">{escape(s)}</text>')
msg(0,1,190,'procesar(solicitud)');msg(1,2,240,'continuar → procesar');note(475,260,'validador.validar(token)')
# Three clearly labelled alternatives depict the same shared call prefix.
for y,h,label,color in [(325,115,'alt · token inválido → 401','#fff4f6'),(465,190,'else · evaluador válido, sin permiso → 403','#fff4f6'),(680,290,'else · investigador válido, con permiso → 200','#f3faf6')]:
 svg.append(f'<rect x="25" y="{y}" width="1405" height="{h}" fill="{color}" fill-opacity=".8" stroke="#b9a6cd"/><text x="40" y="{y+25}" class="heading">{label}</text>')
msg(2,1,400,'401 · token inválido',True);note(890,375,'Autorización y radicación: no ejecutados')
msg(2,3,535,'identidad validada → procesar');note(850,550,'politica.puedeRadicar(identidad) = false')
msg(3,2,605,'403 · sin permiso',True);msg(2,1,640,'403',True)
msg(2,3,750,'identidad validada → procesar');note(730,765,'politica.puedeRadicar(identidad) = true')
msg(3,4,840,'continuar → procesar');note(970,850,'repositorio.guardar(solicitud)')
msg(4,3,915,'200 + identificador',True);msg(3,2,945,'200',True);msg(2,1,970,'200',True)
msg(1,5,1040,'registrar(solicitud, respuesta) · común a 401 / 403 / 200');msg(5,1,1100,'Registro en memoria · sin token',True);msg(1,0,1170,'respuesta final',True)
svg.append('<text x="30" y="1260" class="heading">Auditoría envuelve la llamada y registra cuando retorna el sucesor.</text><text x="30" y="1300" class="small">Título inválido: ClienteRadicacion responde 400 antes de iniciar la cadena (validación de datos).</text></svg>')
(OUT/'secuencia.svg').write_text('\n'.join(svg)+'\n')
for p in OUT.glob('*'): (ROOT/'docs'/p.name).write_bytes(p.read_bytes())
print('Generados: UML editable y vistas SVG desde modelo común.')
