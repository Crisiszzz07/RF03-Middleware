"""Verifica requisitos UML y concordancia con las declaraciones Java y artefactos.
Ejecutar desde la raíz: python3 -m unittest discover -s tools -p 'test_uml.py'
No requiere un servidor ni un renderizador PlantUML.
"""
import unittest
import re
import xml.etree.ElementTree as ET
from generar_uml import (
    CLASES, SUBCLASES, SECUENCIA, PARTICIPANTES, NOTA_ALCANCE,
    generar_clases, generar_secuencia, ROOT, OUT,
)


def caminos(bloques):
    rutas = [[]]
    for bloque in bloques:
        if bloque[0] == 'mensaje':
            rutas = [ruta + [bloque] for ruta in rutas]
        elif bloque[0] == 'alt':
            opciones = [ruta for _, rama in bloque[1] for ruta in caminos(rama)]
            rutas = [ruta + opcion for ruta in rutas for opcion in opciones]
    return rutas


def mensajes(bloques):
    for bloque in bloques:
        if bloque[0] == 'mensaje': yield bloque
        elif bloque[0] == 'alt':
            for _, rama in bloque[1]: yield from mensajes(rama)


class ContratoUMLTest(unittest.TestCase):
    def test_referencias_y_contrato_corresponden_a_java(self):
        modelo = {c[0]: c for c in CLASES}
        campos = [
            ('ClienteRadicacion', 'cabeza', 'ManejadorSeguridad', '-', '1'),
            ('ManejadorSeguridad', 'siguiente', 'ManejadorSeguridad', '#', '0..1'),
            ('AuditoriaMiddleware', 'registro', 'RegistroAuditoriaEnMemoria', '-', '1'),
            ('AutenticacionMiddleware', 'validador', 'ValidadorTokenSimulado', '-', '1'),
            ('AutorizacionMiddleware', 'politica', 'PoliticaPermisosSimulada', '-', '1'),
            ('RadicarPropuestaHandler', 'repositorio', 'RepositorioPropuestasEnMemoria', '-', '1'),
        ]
        for clase, campo, tipo, visibilidad, multiplicidad in campos:
            with self.subTest(clase=clase):
                declaracion = f'{visibilidad} {campo}: {tipo} [{multiplicidad}] {{readOnly}}'
                self.assertEqual(modelo[clase][5].count(declaracion), 1)
                fuente = (ROOT / f'src/main/java/demo/rf03/{clase}.java').read_text()
                java_vis = 'protected' if visibilidad == '#' else 'private'
                self.assertRegex(fuente, rf'{java_vis}\s+final\s+{tipo}\s+{campo}\s*;')
        self.assertIn('{abstract} + procesar(solicitud: SolicitudRadicacion): RespuestaRadicacion', modelo['ManejadorSeguridad'][6])
        self.assertIn('# continuar(solicitud: SolicitudRadicacion): RespuestaRadicacion', modelo['ManejadorSeguridad'][6])
        self.assertEqual(len(SUBCLASES), 4)
        for clase in SUBCLASES:
            self.assertIn('extends ManejadorSeguridad', (ROOT / f'src/main/java/demo/rf03/{clase}.java').read_text())
        puml, _ = generar_clases()
        self.assertIn('abstract class ManejadorSeguridad', puml)
        self.assertNotRegex(puml, r'setSiguiente|setSuccessor|JWT|SSO|Oracle')
        self.assertNotIn('-->', puml, 'No duplicar atributos mediante asociaciones')

    def test_servicios_y_solicitud_tienen_participantes_distintos(self):
        participantes = {a: n for a, n, _ in PARTICIPANTES}
        for clase in ['ValidadorTokenSimulado', 'PoliticaPermisosSimulada', 'RepositorioPropuestasEnMemoria', 'RegistroAuditoriaEnMemoria', 'SolicitudRadicacion']:
            self.assertIn(clase, participantes.values())
        for _, origen, destino, _, _ in mensajes(SECUENCIA): self.assertNotEqual(origen, destino)
        self.assertEqual(participantes['Q'], 'SolicitudRadicacion')

    def test_los_tres_caminos_no_invocan_manejadores_omitidos(self):
        rutas = caminos(SECUENCIA)
        self.assertEqual(len(rutas), 3)
        for ruta in rutas:
            codigo = next(int(re.search(r'RespuestaRadicacion\((\d+)', m[3])[1]) for m in ruta if 'RespuestaRadicacion(' in m[3])
            llamadas = [(m[1], m[2]) for m in ruta if not m[4]]
            self.assertIn(('N', 'V'), llamadas)
            self.assertIn(('A', 'L'), llamadas)
            if codigo == 401:
                self.assertNotIn(('N', 'Q'), llamadas)
                self.assertNotIn(('N', 'Z'), llamadas)
                self.assertFalse(any('R' in par or 'P' in par or 'D' in par for par in llamadas))
            else:
                self.assertIn(('N', 'Q'), llamadas)
                self.assertIn(('N', 'Z'), llamadas)
                self.assertIn(('Z', 'P'), llamadas)
                autenticar = next(i for i, m in enumerate(ruta) if m[1:3] == ('N', 'Q'))
                autorizar = next(i for i, m in enumerate(ruta) if m[1:3] == ('N', 'Z'))
                self.assertLess(autenticar, autorizar)
                if codigo == 403:
                    self.assertNotIn(('Z', 'R'), llamadas)
                    self.assertNotIn(('R', 'D'), llamadas)
                else:
                    self.assertEqual(codigo, 200)
                    self.assertIn(('Z', 'R'), llamadas)
                    self.assertIn(('R', 'D'), llamadas)

    def test_registro_ocurre_despues_de_recibir_y_antes_de_responder(self):
        for ruta in caminos(SECUENCIA):
            recibe = next(i for i, m in enumerate(ruta) if m[1:3] == ('N', 'A') and m[4])
            registra = next(i for i, m in enumerate(ruta) if m[1:3] == ('A', 'L') and not m[4])
            responde = next(i for i, m in enumerate(ruta) if m[1:3] == ('A', 'C') and m[4])
            self.assertLess(recibe, registra)
            self.assertLess(registra, responde)
            retorno_filtros = [m[1:3] for m in ruta if m[4] and m[1] in ['N', 'Z', 'R', 'A']]
            codigo = next(int(re.search(r'RespuestaRadicacion\((\d+)', m[3])[1]) for m in ruta if 'RespuestaRadicacion(' in m[3])
            esperado = {401: [('N', 'A'), ('A', 'C')], 403: [('Z', 'N'), ('N', 'A'), ('A', 'C')], 200: [('R', 'Z'), ('Z', 'N'), ('N', 'A'), ('A', 'C')]}
            self.assertEqual(retorno_filtros, esperado[codigo])

    def test_fuentes_y_svg_comparten_mensajes_y_estilo_de_retorno(self):
        puml, svg = generar_secuencia()
        root = ET.fromstring(svg)
        ns = {'s': 'http://www.w3.org/2000/svg'}
        grupos = root.findall('.//s:g[@data-from]', ns)
        modelo = list(mensajes(SECUENCIA))
        self.assertEqual(len(grupos), len(modelo))
        for grupo, (_, origen, destino, etiqueta, es_retorno) in zip(grupos, modelo):
            self.assertEqual(grupo.get('data-from'), origen)
            self.assertEqual(grupo.get('data-to'), destino)
            self.assertEqual(grupo.get('data-kind'), 'retorno' if es_retorno else 'llamada')
            path = grupo.find('s:path', ns)
            self.assertEqual(path.get('stroke-dasharray') is not None, es_retorno)
            self.assertIn(f'{origen} {"-->" if es_retorno else "->"} {destino} : {etiqueta}', puml)
        self.assertEqual(root.find('s:desc', ns).text, NOTA_ALCANCE)
        self.assertIn('título válido', puml)
        self.assertIn(NOTA_ALCANCE, ' '.join(puml.split()))
        self.assertIn('400', puml)

    def test_artefactos_regenerados_estan_sincronizados(self):
        for nombre, generador in [('clases', generar_clases), ('secuencia', generar_secuencia)]:
            puml, svg = generador()
            for extension, esperado in [('puml', puml), ('svg', svg)]:
                for carpeta in [OUT, ROOT / 'docs']:
                    self.assertEqual((carpeta / f'{nombre}.{extension}').read_text(), esperado)
                if extension == 'svg': ET.fromstring(esperado)


if __name__ == '__main__': unittest.main()
