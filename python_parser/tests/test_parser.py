import pytest
from organizador_parser.parser import ParserHorarios


@pytest.fixture(autouse=True)
def mocked_carreras(mocker):
    mocker.patch.object(ParserHorarios, 'load_carreras')


@pytest.fixture
def mocked_dict_clase():
    clase = {
        'Materia': "XXYY",
        'Curso': 'AAA',
        'Nombre': 'Una Materia',
        'Docentes': 'John Doe',
        'Dia': 'Lu',
        'Inicio': '07:30',
        'Fin': '10:30',
        'Clase': 'TPO',
        'Vacantes': 33,
        'Aula': 'L3',
        'Sede': 'PC',
    }
    return clase


@pytest.mark.parametrize('hora, indice', (
        ('07:00', 0),
        ('07:30', 1),
        ('07:45', 1),
        ('09:00', 4),
))
def test_num_hora(hora, indice):
    assert ParserHorarios.num_hora(hora) == indice


@pytest.mark.parametrize('dia, indice', (
        ('Lu', 0),
        ('lU', 0),
        ('Ju', 3),
        ('Sa', 5)
))
def test_num_dia(dia, indice):
    assert ParserHorarios.num_dia(dia) == indice


def test_add_clase(mocked_dict_clase, mocker):
    clase_curso = mocker.patch.object(ParserHorarios, 'add_clase_curso')
    parser = ParserHorarios()
    parser.add_clase(mocked_dict_clase)

    data_clase = {
        'aula': 'L3',
        'dia': 0,
        'inicio': 1,
        'fin': 7,
        'sede': 'PC',
        'tipo': 'TPO'
    }

    data_kw = {
        'cod_curso': 'AAA',
        'cod_materia': 'XXYY',
        'cupo': 33,
        'docentes': 'John Doe',
        'nombre': 'Una Materia',
    }
    clase_curso.assert_called_once_with(data_clase, **data_kw)
