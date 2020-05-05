# See https://github.com/dabeaz/compilers_2020_05/wiki/WabbitScript.md
from difflib import unified_diff
from subprocess import Popen, PIPE

from wabbit.check_syntax import check_syntax
from wabbit.format_json import format_json
from wabbit.format_source import format_source
from wabbit.model import (
    Assign,
    BinOp,
    ConstDef,
    Float,
    If,
    Integer,
    Name,
    Print,
    UnaryOp,
    VarDef,
    While,
    Statements,
)


def check(source, model, label):
    check_syntax(model)
    dump_json(model, label)
    transpiled_source = format_source(model)
    if transpiled_source.strip() != source.strip():
        diff = "\n".join(unified_diff(source.splitlines(), transpiled_source.splitlines()))
        proc = Popen(["delta"], stdin=PIPE)
        proc.stdin.write(diff.encode("utf-8"))  # type: ignore
        proc.communicate()


def dump_json(model, label):
    with open(f"/tmp/model_{label}.json", "w") as fh:
        fh.write(format_json(model))


# ----------------------------------------------------------------------
# Simple Expression
expr_source = "2 + 3 * 4;"
expr_model = Statements([BinOp("+", Integer(2), BinOp("*", Integer(3), Integer(4)))])

check(expr_source, expr_model, 0)

# ----------------------------------------------------------------------
# Program 1: Printing
source1 = """
print 2 + 3 * -4;
print 2.0 - 3.0 / -4.0;
print -2 + 3;
print 2 * 3 + -4;
"""

model1 = Statements(
    [
        Print(BinOp("+", Integer(2), BinOp("*", Integer(3), UnaryOp("-", Integer(4))))),
        Print(BinOp("-", Float(2.0), BinOp("/", Float(3.0), UnaryOp("-", Float(4.0))))),
        Print(BinOp("+", UnaryOp("-", Integer(2)), Integer(3))),
        Print(BinOp("+", BinOp("*", Integer(2), Integer(3)), UnaryOp("-", Integer(4)))),
    ]
)

check(source1, model1, 1)

# ----------------------------------------------------------------------
# Program 2: Variable and constant declarations.
#            Expressions and assignment.
source2 = """
const pi = 3.14159;
var tau float;
tau = 2.0 * pi;
print tau;
"""

model2 = Statements(
    [
        ConstDef("pi", None, 3.14159),
        VarDef("tau", "float", None),
        Assign("tau", BinOp("*", Float(2.0), Name("pi"))),
        Print(Name("tau")),
    ]
)

check(source2, model2, 2)

# ----------------------------------------------------------------------
# Program 3: Conditionals.  This program prints out the minimum of
# two values.
#
source3 = """
var a int = 2;
var b int = 3;
if a < b {
    print a;
} else {
    print b;
}
"""

model3 = Statements(
    [
        VarDef("a", "int", 2),
        VarDef("b", "int", 3),
        If(
            BinOp("<", Name("a"), Name("b")),
            Statements([Print(Name("a"))]),
            Statements([Print(Name("b"))]),
        ),
    ]
)

check(source3, model3, 3)

# ----------------------------------------------------------------------
# Program 4: Loops.  This program prints out the first 10 factorials.
#

source4 = """
const n = 10;
var x int = 1;
var fact int = 1;

while x < n {
    fact = fact * x;
    print fact;
    x = x + 1;
}
"""

model4 = Statements(
    [
        ConstDef("n", None, 10),
        VarDef("x", "int", 1),
        VarDef("fact", "int", 1),
        While(
            BinOp("<", Name("x"), Name("n")),
            Statements(
                [
                    Assign("fact", BinOp("*", Name("fact"), Name("x"))),
                    Print(Name("fact")),
                    Assign("x", BinOp("+", Name("x"), Integer(1))),
                ]
            ),
        ),
    ]
)

check(source4, model4, 4)


# ----------------------------------------------------------------------
# Program 5: Compound Expressions.  This program swaps the values of
# two variables using a single expression.
#

source5 = """
var x = 37;
var y = 42;
x = { var t = y; y = x; t; };     // Compound expression.
print x;
print y;
"""

model5 = Statements(
    [
        VarDef("x", None, Integer(37)),
        VarDef("y", None, Integer(42)),
        Assign("x", Statements([VarDef("t", None, Name("y")), Assign("y", Name("x")), Name("t")])),
        Print(Name("x")),
        Print(Name("y")),
    ]
)

check(source5, model5, 5)
