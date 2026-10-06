"""Verificación estructural. No sustituye javac, JUnit ni una revisión en navegador."""
from pathlib import Path
from html.parser import HTMLParser
import re
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
JAVA=ROOT/'src/main/java/demo/rf03'
STATIC=ROOT/'src/main/resources/static'
checks=0
def check(ok,message):
 global checks
 if not ok: raise AssertionError(message)
 checks+=1

pom=ET.parse(ROOT/'pom.xml');ns={'m':'http://maven.apache.org/POM/4.0.0'}
check(pom.findtext('m:parent/m:version',namespaces=ns)=='3.5.16','Spring Boot fijado')
check(pom.findtext('m:properties/m:java.version',namespaces=ns)=='17','Java 17')
fuentes={p.stem:p.read_text() for p in JAVA.glob('*.java')}
for name,source in fuentes.items():
 check('package demo.rf03;' in source,f'Paquete de {name}')
 for fragment in re.findall(r'// @fragment (\w+):start',source):
  check(source.count('// @fragment '+fragment+':start')==1,f'Marcador único {name}/{fragment}')
  check(source.count('// @fragment '+fragment+':end')==1,f'Marcador fin {name}/{fragment}')
 # Comprueba cada referencia de clase + clave de fragmento en llamadas evento.
 for cls,key in re.findall(r'"(\w+)",\s*"(\w+)",\s*"[^"\n]*"\);',source):
  if cls in fuentes:
   check('// @fragment '+key+':start' in fuentes[cls],f'Referencia de fragmento {name} -> {cls}/{key}')
for name in ['AuditoriaMiddleware','AutenticacionMiddleware','AutorizacionMiddleware','RadicarPropuestaHandler']:
 check('extends ManejadorSeguridad' in fuentes[name],f'Herencia {name}')
check('protected final ManejadorSeguridad siguiente' in fuentes['ManejadorSeguridad'],'Referencia sucesor')
check('cabeza.procesar(solicitud)' in fuentes['ClienteRadicacion'],'Cliente usa cabeza')
check('siguiente.procesar(solicitud)' in fuentes['ManejadorSeguridad'],'Delegación real')
check(fuentes['AuditoriaMiddleware'].index('continuar(solicitud)')<fuentes['AuditoriaMiddleware'].index('registro.registrar(solicitud, respuesta)'),'Auditoría después del retorno')
check('solicitud.identidad()' in fuentes['AutorizacionMiddleware'],'Consulta identidad en autorización')
check('rol' not in fuentes['RadicacionController'].split('public record Entrada')[1].split('{}')[0],'DTO sin rol')
class HTML(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.resources=[];self.handlers=[]
 def handle_starttag(self,tag,attrs):
  attrs=dict(attrs)
  if 'id' in attrs:self.ids.append(attrs['id'])
  if tag in ['script','img'] and 'src' in attrs:self.resources.append(attrs['src'])
  if tag=='link' and attrs.get('rel')=='stylesheet':self.resources.append(attrs['href'])
  if 'data-handler' in attrs:self.handlers.append(attrs['data-handler'])
html=HTML();html.feed((STATIC/'index.html').read_text())
check(len(html.ids)==len(set(html.ids)),'IDs únicos')
for res in html.resources:
 check(not re.match(r'https?://',res),f'Recurso local {res}')
 check((STATIC/res).is_file(),f'Recurso presente {res}')
for cls in html.handlers:check(cls in fuentes,f'Nodo real {cls}')
check(html.handlers==['ClienteRadicacion','AuditoriaMiddleware','AutenticacionMiddleware','AutorizacionMiddleware','RadicarPropuestaHandler'],'Orden de presentación')
ts=(STATIC/'app.ts').read_text()
for archivo in ['app.ts','simulacion.ts']:
 contenido=(STATIC/archivo).read_text()
 for id in re.findall(r"(?:elemento(?:<[^>]+>)?|nodo(?:<[^>]+>)?|texto)\('([^']+)'(?=\s*[,\)])",contenido):check(id in html.ids,f'ID TS presente {archivo}/{id}')
check('datos.traza.map' in ts and 'ejecucion.traza.slice' in ts,'Consume eventos backend')
check('innerHTML' not in ts,'Inserción segura textContent')
check('token: escenarioElegido().token, titulo' in ts,'Entrada token/titulo')
check('prefers-reduced-motion' in ts and 'prefers-reduced-motion' in (STATIC/'styles.css').read_text(),'Movimiento reducido')
for type in ['clases','secuencia']:
 for ext in ['svg','puml']:
  p=STATIC/'uml'/f'{type}.{ext}'
  check(p.read_bytes()==(ROOT/'docs'/p.name).read_bytes(),f'UML local/documentación {p.name}')
 ET.parse(STATIC/'uml'/f'{type}.svg')
 check(True,f'SVG {type} XML válido')
puml=(STATIC/'uml/clases.puml').read_text()
for cls in fuentes:
 if cls!='Aplicacion':check('class '+cls in puml,f'Clase documentada {cls}')
for f in ['mvnw','mvnw.cmd']:
 s=(ROOT/f).read_text()
 check('@@project.version@@' not in s and 'version 3.3.4' in s,f'Wrapper versionado {f}')
check('apache-maven/3.9.11/' in (ROOT/'.mvn/wrapper/maven-wrapper.properties').read_text(),'Maven versionado')
print(f'PASS: {checks} comprobaciones estructurales. Java y navegador no ejecutados.')
