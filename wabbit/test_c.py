from wabbit.c import compile_program
from wabbit.model import *


def inner_code(prog):
    program = compile_program(prog)
    print(program)
    return program.locals + program.statements


def test_float():
    model = Statements([Float("2.1")])
    assert inner_code(model) == "float _1;\n_1 = 2.1;\n_1;"


def test_int():
    model = Statements([Integer(3)])
    assert inner_code(model) == "int _1;_1;"


def test_plus():
    model = Statements([BinOp("+", Integer(3), Integer(88))])
    assert compile_program(model).statements == "3 + 88;"


def test_script_models_2():
    source2 = """
        const pi = 3.14159;
    """

    model2 = Statements([Const("pi", None, Float("3.14159"))])

    assert compile_program(model2).locals == "pi float;\n"
    assert compile_program(model2).statements == "pi = 3.14159;"

    source3 = """
    var tau float;
    tau = 2.0 * pi;
    print tau;
    """
    model3 = Statements([Var("tau", "float", None)])

    assert compile_program(model3).locals == "tau float;\n"
    assert compile_program(model3).statements == ";"

    source3 = """
        const pi = 3.141
        var tau float;
        tau = 2.0 * pi;
        print tau;
    """
    model3 = Statements(
        [
            Const("pi", None, Float("3.141")),
            Var("tau", "float", None),
            Assignment(Variable("tau"), BinOp("*", Float("2.0"), Variable("pi"))),
        ]
    )

    assert compile_program(model3).locals == "tau float;\n"
    assert compile_program(model3).statements == ";"
