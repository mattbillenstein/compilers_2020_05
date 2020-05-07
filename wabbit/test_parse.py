import pytest
from wabbit.parse import WabbitParser
from wabbit.tokenize import tokenize
from wabbit.model import *
from wabbit.to_source import to_source
from tests.Script.test_helpers import assert_expectations


def test_parser_arithmetic():
    parser = WabbitParser()

    source = "2;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements([Integer(2)])

    source = "2.3;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements([Float("2.3")])

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

    source = "5 * 9 + 2;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements(
        [BinOp("+", BinOp("*", Integer(5), Integer(9)), Integer(2))]
    )

    source = "(2 + 3) * 8;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements(
        [BinOp("*", BinOp("+", Integer(2), Integer(3)), Integer(8))]
    )

    source = "2.9 + 2.7;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements([BinOp("+", Float("2.9"), Float("2.7"))])

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
                BinOp(
                    "-",
                    Float("2.0"),
                    BinOp("/", Float("3.0"), UnaryOp("-", Float("4.0"))),
                )
            )
        ]
    )


def test_parser_assignment_and_location():
    parser = WabbitParser()

    source = "a = 2;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements([Assignment(Variable("a"), Integer(2))])

    source = "a = 2 * 3;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements(
        [Assignment(Variable("a"), BinOp("*", Integer(2), Integer(3)))]
    )

    source = "obj.b = 2 * 3;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements(
        [
            Assignment(
                DottedLocation(Variable("obj"), "b"), BinOp("*", Integer(2), Integer(3))
            )
        ]
    )

    source = "myObj;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements([Variable("myObj")])

    source = "yourObj.foo;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements(
        [DottedLocation(Variable("yourObj"), "foo")]
    )

    source = "(x + y * z).value;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements(
        [
            DottedLocation(
                BinOp("+", Variable("x"), BinOp("*", Variable("y"), Variable("z"))),
                "value",
            )
        ]
    )


def test_const_definition():
    parser = WabbitParser()

    source = "const maxSeen = 2 + x * 7;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements(
        [
            Const(
                "maxSeen",
                None,
                BinOp("+", Integer(2), BinOp("*", Variable("x"), Integer(7))),
            )
        ]
    )

    source = "const lastSeen = x;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements([Const("lastSeen", None, Variable("x"),)])

    source = "const lastSeen = 23.9;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements([Const("lastSeen", None, Float("23.9"))])

    source = "const maxSeen int = 2 + x * 7;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements(
        [
            Const(
                "maxSeen",
                "int",
                BinOp("+", Integer(2), BinOp("*", Variable("x"), Integer(7))),
            )
        ]
    )

    source = "const lastSeen Point = x;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements(
        [Const("lastSeen", "Point", Variable("x"),)]
    )

    source = "const lastSeen Line = 23.9;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements(
        [Const("lastSeen", "Line", Float("23.9"))]
    )


def test_var_definition():
    parser = WabbitParser()

    source = "var maxSeen = 2 + x * 7;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements(
        [
            Var(
                "maxSeen",
                None,
                BinOp("+", Integer(2), BinOp("*", Variable("x"), Integer(7))),
            )
        ]
    )

    source = "var lastSeen = x;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements([Var("lastSeen", None, Variable("x"),)])

    source = "var lastSeen = 23.9;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements([Var("lastSeen", None, Float("23.9"))])

    source = "var maxSeen int = 2 + x * 7;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements(
        [
            Var(
                "maxSeen",
                "int",
                BinOp("+", Integer(2), BinOp("*", Variable("x"), Integer(7))),
            )
        ]
    )

    source = "var lastSeen Point = x;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements(
        [Var("lastSeen", "Point", Variable("x"),)]
    )

    source = "var lastSeen Line = 23.9;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements([Var("lastSeen", "Line", Float("23.9"))])

    source = "var amount Currency;"
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements([Var("amount", "Currency", None)])


def test_function_definition():
    parser = WabbitParser()

    source = "func max () int { 2 + 3; }"
    tokens = tokenize(source)

    assert parser.parse(tokens) == Statements(
        [
            FunctionDefinition(
                "max", None, "int", Statements([BinOp("+", Integer(2), Integer(3))])
            )
        ]
    )

    source = "func min (a bool, b float) int { 2 + 3; }"
    tokens = tokenize(source)

    assert parser.parse(tokens) == Statements(
        [
            FunctionDefinition(
                "min",
                Arguments(Argument("a", "bool"), Argument("b", "float")),
                "int",
                Statements([BinOp("+", Integer(2), Integer(3))]),
            )
        ]
    )

    source = "func average () int { 2 + 3; }"
    tokens = tokenize(source)

    assert parser.parse(tokens) == Statements(
        [
            FunctionDefinition(
                "average",
                None,
                "int",
                Statements([BinOp("+", Integer(2), Integer(3))]),
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
                BinOp(
                    "-",
                    Float("2.0"),
                    BinOp("/", Float("3.0"), UnaryOp("-", Float("4.0"))),
                )
            ),
            Print(BinOp("+", UnaryOp("-", Integer(2)), Integer(3))),
            Print(
                BinOp("+", BinOp("*", Integer(2), Integer(3)), UnaryOp("-", Integer(4)))
            ),
        ]
    )

    tokens = tokenize(source1)
    assert parser.parse(tokens) == model1


def test_parser_basics():
    source = "2.9 * 2.7;"
    tokens = tokenize(source)
    parser = WabbitParser()

    assert parser.parse(tokens) == Statements([BinOp("*", Float("2.9"), Float("2.7"))])

    source = "2 / 7;"
    tokens = tokenize(source)
    parser = WabbitParser()

    assert parser.parse(tokens) == Statements([BinOp("/", Integer(2), Integer(7))])

    source = "2 + 3 / 7;"
    tokens = tokenize(source)
    parser = WabbitParser()

    assert parser.parse(tokens) == Statements(
        [BinOp("+", Integer(2), BinOp("/", Integer(3), Integer(7)))]
    )


def test_parser_struct():
    parser = WabbitParser()

    source = """struct Point {
        x int;
        y float;
    }
    """
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements(
        [Struct("Point", Argument("x", "int"), Argument("y", "float"))]
    )

    source = """struct Fraction {
    }
    """
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements([Struct("Fraction")])


def test_parser_enum_definition():
    parser = WabbitParser()

    source = """enum Choice {
        YES;
        NO;
    }
    """
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements(
        [Enum("Choice", EnumChoice("YES"), EnumChoice("NO"))]
    )

    source = """enum MaybeStuff {
        NO;
        MaybeFloat(float);
        MaybeInt(int);
    }
    """
    tokens = tokenize(source)
    assert parser.parse(tokens) == Statements(
        [
            Enum(
                "MaybeStuff",
                EnumChoice("NO", None),
                EnumChoice("MaybeFloat", "float"),
                EnumChoice("MaybeInt", "int"),
            )
        ]
    )

