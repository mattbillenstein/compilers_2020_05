import pytest
from wabbit.parse import WabbitParser
from wabbit.tokenize import tokenize
from wabbit.model import *
from wabbit.to_source import to_source
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
    assert parser.parse(tokens) == Statements([Variable("myObj")])

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

    source = "2 + 3 + 4;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements(
        [BinOp("+", BinOp("+", Integer(2), Integer(3)), Integer(4))]
    )

    source = "2 + 3 * 8;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements(
        [BinOp("+", Integer(2), BinOp("*", Integer(3), Integer(8)))]
    )

    source = "2 * 3 + 8;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements(
        [BinOp("*", Integer(2), BinOp("*", Integer(3), Integer(8)))]
    )

    source = "(2 + 3) * 8;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements(
        [BinOp("*", BinOp("+", Integer(2), Integer(3)), Integer(8))]
    )

    source = "2.9 + 2.7;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements([BinOp("+", Float(2.9), Float(2.7))])

    source = "3 * -4;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements(
        [BinOp("*", Integer(3), UnaryOp("-", Integer(4)))]
    )

    source = "2 * 3 + -4;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements(
        [BinOp("+", BinOp("*", Integer(2), Integer(3)), UnaryOp("-", Integer(4)))]
    )

    source = "print 2;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements([Print(Integer(2))])

    source = "print 2 + 3;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements(
        [Print(BinOp("+", Integer(2), Integer(3)))]
    )

    source = "print 3 + -4;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements(
        [Print(BinOp("+", Integer(3), UnaryOp("-", Integer(4))))]
    )

    source = "print 2 * 3 + -4;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements(
        [
            Print(
                BinOp("+", BinOp("*", Integer(2), Integer(3)), UnaryOp("-", Integer(4)))
            )
        ]
    )

    source = "print 2 + 3 * -4;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements(
        [
            Print(
                BinOp("+", Integer(2), BinOp("*", Integer(3), UnaryOp("-", Integer(4))))
            )
        ]
    )

    source = "print 2.0 - 3.0 / -4.0;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements(
        [
            Print(
                BinOp("-", Float(2.0), BinOp("/", Float(3.0), UnaryOp("-", Float(4.0))))
            )
        ]
    )


def test_script_models():
    parser = WabbitParser()

    source1 = """
        print 2 + 3 * -4;
        print 2.0 - 3.0 / -4.0;
        print -2 + 3;
        print 2 * 3 + -4;
    """
    model1 = Statements(
        [
            Print(
                BinOp("+", Integer(2), BinOp("*", Integer(3), UnaryOp("-", Integer(4))))
            ),
            Print(
                BinOp("-", Float(2.0), BinOp("/", Float(3.0), UnaryOp("-", Float(4.0))))
            ),
            Print(BinOp("+", UnaryOp("-", Integer(2)), Integer(3))),
            Print(
                BinOp("*", Integer(2), BinOp("+", Integer(3), UnaryOp("-", Integer(4))))
            ),
        ]
    )

    tokens = tokenize(source1)
    assert parser.parse(tokens) == model1


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
