import logging
import json
import pandas as pd


from argparse import ArgumentParser

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


MAPPING_DIAS = {
    'lu': 0,
    'ma': 1,
    'mi': 2,
    'ju': 3,
    'vi': 4,
    'sa': 5,
}

TEMPLATE_MATERIA = {
    "codigo": None,
    "color": None,
    "cursoForzado": [],
    "cursoSel": 0,
    "cursos": [],
    "expanded": 1,
    "forzar": 0,
    "nombre": None,
    "sel": 0,
}

TEMPLATE_CURSO = {
    "docentes": None,
    "clases": [],
}

TEMPLATE_CLASE = {
    "aula": None,
    "dia": None,
    "fin": None,
    "inicio": None,
    "sede": None,
    "tipo": None,
}


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--csv', required=True, help='Archivo a Parsear')
    parser.add_argument('-s', --'sep', type=str, default=';', help="Separador del CSV")
    parser.add_argument('--salida', help="Json de Salida", default='horarios.json')
    return parser.parse_args()


class ParserHorarios(object):
    """
    Clase que se encarga de parsear los horarios
    """
    json_carreras = "/tmp/carreras.json"

    mapping_clase_keys = {
        'clase': 'tipo',
        'vacantes': 'cupo',
    }

    clase_keys = ('aula', 'dia', 'fin', 'inicio', 'sede', 'tipo')

    carreras_ordenadas = [
        'Civil',
        'Industrial',
        'Naval',
        'Agrim',
        'Mecánica',
        'Electricista',
        'Electrónica',
        'Química',
        'Sistemas',
        'Informática',
        'Alimentos',
        'Ing. Agrim',
        'Tecnicatura Naval',
        'Petróleo'
    ]

    def __init__(self):
        self.clases = []
        self.materias = {}
        self.carreras = self.load_carreras()
        self.colors = ["#FF5E5E", "#FF8F40", "#FFF45E", "#94FF52", "#7CD9D4", "#A876F5", "#FFA1F2", "#BF6E45", "#3ABA7A",
                  "#275BCC", "#82F5B4", "#B1B8C4", "#BA3A7A"]
        self.colors_i = 0

    @classmethod
    def load_carreras(cls):
        with open(cls.json_carreras) as fp:
            carreras = json.load(fp)
        return carreras

    @classmethod
    def num_hora(cls, hora:str):
        """
        El organizador parece que funciona separando el horario en bloques de 30 min, comenzando desde las 7:00
        Por lo tanto:
            07:00 -> 0
            07:30 -> 1
            ...

        :param hora: String de hora. Ej: 16:30
        :return: Un número entero
        """
        h, m = hora.split(':')
        x = (int(h) - 7) * 2
        if int(m) >= 30:
            x += 1
        return x

    @classmethod
    def num_dia(cls, dia:str):
        return MAPPING_DIAS[dia.lower()]

    @classmethod
    def parse_clase(cls, clase):
        data = {}
        for k, v in clase.items():
            key = cls.mapping_clase_keys.get(key, k.lower())
            data[key] = v
        return data

    def new_color(self):
        color = self.colors[self.colors_i % len(self.colors)]
        self.colors_i += 1
        return color

    def add_clase(self, clase):
        """
        Aca se hace el mappeo mas importante. El de los datos del archivo, con los nombres de las variables que usaremos
        internamente en el programa.
        """
        cod_materia = clase['Materia']
        cod_curso = clase['Curso']
        nombre = clase['Nombre']
        docentes = clase['Docentes']
        dia = clase['Dia']
        inicio = clase['Inicio']
        fin = clase['Fin']
        tipo = clase['Clase']
        cupo = clase['Vacantes']
        aula = clase['Aula']
        sede = clase['Sede']

        inicio = self.num_hora(inicio)
        fin = self.num_hora(fin)
        dia = self.num_dia(dia)

        data_clase = {
            'aula': str(aula),
            'dia': dia,
            'inicio': inicio,
            'fin': fin,
            'sede': sede,
            'tipo': tipo,
        }

        kw = {
            'cod_materia': str(cod_materia),
            'cod_curso': str(cod_curso),
            'nombre': nombre,
            'docentes': str(docentes),
            'cupo': cupo,
        }

        self.add_clase_curso(data_clase, **kw)

    def get_curso(self, cod_curso, cod_materia, **kw):
        if cod_materia not in self.materias:
            return None

        return self.materias[cod_materia]['cursos'].get(cod_curso)

    def add_clase_curso(self, data_clase, cod_curso, **kw):
        curso = self.get_curso(cod_curso, **kw)
        if not curso:
            curso = self.add_curso_materia(cod_curso, **kw)

        curso['clases'].append(data_clase)
        self.clases.append(data_clase)

    def add_curso_materia(self, cod_curso, cod_materia, docentes, cupo, **kw):
        if cod_materia not in self.materias:
            self.add_materia(cod_materia, **kw)

        data_curso = {
            'cod_curso': cod_curso,
            'docentes': docentes,
            'cupo': cupo,
            'clases': [],
        }

        self.materias[cod_materia]['cursos'][cod_curso] = data_curso
        return data_curso

    def add_materia(self, cod_materia, nombre):
        self.materias[cod_materia] = {
            'codigo': cod_materia,
            'nombre': nombre,
            'cursos': {},
        }

    def parse(self, data):
        for clase in data:
            self.add_clase(clase)

    def parse_csv(self, csv_file, sep):
        """
        Convierte el archivo CSV al dict
        """
        dataset = pd.read_csv(csv_file, sep=sep)
        data = dataset.to_dict(orient="records")

        self.parse(data)

    def dump_materias(self):
        materias = []
        for cod_mat, materia in self.materias.items():
            _materia = {
                'codigo': str(cod_mat),
                'color': self.new_color(),
                'cursoForzado': [],
                'cursoSel': 0,
                'cursos': [],
                'expanded': 1,
                'forzar': 0,
                'nombre': materia['nombre'],
                'sel': 0
            }
            for cod_curso, curso in materia["cursos"].items():
                curso = {
                    'docentes': curso['docentes'],
                    'clases': curso['clases']
                }
                _materia['cursos'].append(curso)
            index = len(materias)
            materias.append(_materia)
            materia['index'] = index
            _materia['index'] = index
        return materias

    def dump_data(self):
        materias = self.dump_materias()
        #carreras = [{"materias": [], "nombre": nombre} for nombre in self.carreras.keys()]
        carreras = []
        for nombre in self.carreras_ordenadas:
            cod_materias = self.carreras[nombre]['cod_materias']
            aux_materias = []
            for cod_mat in cod_materias:
                mat = self.materias.get(cod_mat)
                if not mat:
                    logger.warning("Materia %s no encontrada este cuatrimestre", cod_mat)
                else:
                    aux_materias.append(mat['index'])
            carrera = {
                'nombre': nombre,
                'materias': aux_materias
            }
            carreras.append(carrera)

        data = {
            'carreras': carreras,
            'materias': materias
        }

        with open("/tmp/2Q2019.json", 'w') as fp:
            json.dump(data, fp)


def parsear_horarios(csv, salida, sep):
    pass



def main():
    args = parse_args()
    parsear_horarios(**vars(args))


if __name__ == '__main__':
    main()