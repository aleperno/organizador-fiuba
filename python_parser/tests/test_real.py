import pytest
from organizador_parser.parser import ParserHorarios


def test_data_real():
    parser = ParserHorarios()
    csv = "/tmp/horarios.csv"

    parser.parse_csv(csv, sep=";")

    parser.dump_data()
