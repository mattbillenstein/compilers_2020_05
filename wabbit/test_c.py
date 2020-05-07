from wabbit.c import compile_program
from wabbit.model import *


def test_float():
    model = Statements([Float("2.1")])
    assert compile_program(model).statements == "2.1;"


def test_int():
    model = Statements([Integer(3)])
    assert compile_program(model).statements == "3;"


def test_plus():
    model = Statements([BinOp("+", Integer(3), Integer(88))])
    assert compile_program(model).statements == "3 + 88;"

