import pytest
from wabbit.model import *
from wabbit.interp import interpret_program
from wabbit.errors import InterpreterException


def test_var_assignment():
    env = interpret_program(Var("x", None, Integer(2)))
    assert env["x"] == ("var", 2)

    env = interpret_program(Var("y", "float", Float(2.0)))
    assert env["y"] == ("var", 2.0)


# def test_var_reassignment():
#     env = interpret_program(Var("x", "int", Integer(2)))
#     assert env["x"] == ("var", 2)

#     try:
#         interpret_program(Var("x", "int", Integer(2)), env)
#         pytest.fail("Did not hit exception when attempting reassignment")
#     except InterpreterException:
#         print("found expected exception")


# def test_var_reassignment_to_types():
#     try:
#         env = interpret_program(
#             Statements(
#                 [Var("x", "int", Integer(2)), Assignment(Variable("x"), Float(2.0)),]
#             )
#         )
#         pytest.fail("Did not expect to be able to resassign int to float")
#     except InterpreterException:
#         pass
