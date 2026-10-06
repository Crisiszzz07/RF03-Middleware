"""Empaqueta exclusivamente el proyecto fuente. No descarga ni compila dependencias."""
from pathlib import Path
import zipfile
import shutil
import hashlib
import argparse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--solo-fuentes',action='store_true',help='Actualizar ZIP y SHA-256 sin copiar el JAR')
args=parser.parse_args()
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs';OUT.mkdir(exist_ok=True)
zip_path=OUT/'rf03-chain-fuentes.zip'
files=[p for name in ['src','docs','tools','.mvn'] for p in (ROOT/name).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
files += [ROOT/name for name in ['README.md','pom.xml','mvnw','mvnw.cmd','tsconfig.json','.gitignore','WRAPPER-LICENSE.txt','WRAPPER-NOTICE.txt']]
files += list(ROOT.glob('img*.png'))  # Capturas locales referenciadas por el README
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(files): z.write(p,Path('rf03-chain')/p.relative_to(ROOT))
with zipfile.ZipFile(zip_path) as z:
 assert z.testzip() is None
 names=z.namelist()
 assert all('/target/' not in s and '/node_modules/' not in s and '/.git/' not in s and '/outputs/' not in s for s in names)
 for s in ['pom.xml','mvnw','mvnw.cmd','.mvn/wrapper/maven-wrapper.properties','src/main/resources/static/app.ts','src/main/resources/static/app.js','src/test/java/demo/rf03/CadenaTest.java']:
  assert 'rf03-chain/'+s in names
jar=ROOT/'target/rf03-chain-1.0.0.jar'
if jar.exists() and not args.solo_fuentes:
 reports=list((ROOT/'target/surefire-reports').glob('TEST-*.xml'))
 assert reports, 'No copiar JAR sin informes de pruebas'
 import xml.etree.ElementTree as ET
 for r in reports:
  suite=ET.parse(r).getroot()
  assert int(suite.get('failures',0))==0 and int(suite.get('errors',0))==0
 shutil.copy2(jar,OUT/jar.name)
 print('JAR copiado tras comprobar informes exitosos.')
elif args.solo_fuentes:print('Solo fuentes: JAR existente no actualizado; recompilar para incluir los cambios.')
else:print('No hay JAR compilado: se entrega ZIP fuente; consultar docs/VERIFICACION.md.')
digest=hashlib.sha256(zip_path.read_bytes()).hexdigest()
(OUT/'SHA256SUMS.txt').write_text(f'{digest}  {zip_path.name}\n')
print(f'ZIP validado: {len(files)} archivos, {zip_path.stat().st_size} bytes')
