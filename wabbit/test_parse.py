import pytest
from wabbit.parse import WabbitParser
from wabbit.tokenize import tokenize
from wabbit.model import *
from tests.Script.test_helpers import assert_expectations


def test_parser_name():
    parser = WabbitParser()

    source = "2;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements([Integer(2)])

    source = "2.3;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements([Float(2.3)])

    source = "myObj;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements(["myObj"])

    source = "var x = 3;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements([Var("x", None, Integer(3))])

    source = "var y int = 3;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements([Var("y", "int", Integer(3))])

    source = "const a = 3.1;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements([Const("a", None, Float(3.1))])

    source = "const b float = 3.1;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements([Const("b", "float", Float(3.1))])

    source = "2 + 3;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements([BinOp("+", Integer(2), Integer(3))])

    source = "2 + 3 * 8;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements(
        [BinOp("+", Integer(2), BinOp("*", Integer(3), Integer(8)))]
    )

    source = "(2 + 3) * 8;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements(
        [BinOp("*", BinOp("+", Integer(2), Integer(3)), Integer(8))]
    )

    source = "2.9 + 2.7;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements([BinOp("+", Float(2.9), Float(2.7))])


# def test_parser_basics():
#     source = "2.9 * 2.7"
#     tokens = tokenize(source)
#     parser = WabbitParser()

#     assert parser.parse(tokens) == BinOp("*", Float(2.9), Float(2.7))

#     source = "2 / 7"
#     tokens = tokenize(source)
#     parser = WabbitParser()

#     assert parser.parse(tokens) == BinOp("/", Integer(2), Integer(7))

#     source = "2 + 3 / 7"
#     tokens = tokenize(source)
#     parser = WabbitParser()

#     assert parser.parse(tokens) == BinOp(
#         "+", Integer(2), BinOp("/", Integer(3), Integer(7))
#     )
