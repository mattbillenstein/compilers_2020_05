# See https://github.com/dabeaz/compilers_2020_05/wiki/WabbitScript.md
import sys
from difflib import unified_diff
from subprocess import Popen, PIPE

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


def assert_equivalent(source, model):
    transpiled_source = format_source(model)
    if transpiled_source.strip() != source.strip():
        diff = "\n".join(unified_diff(source.splitlines(), transpiled_source.splitlines()))
        proc = Popen(["delta"], stdin=PIPE)
        proc.stdin.write(diff.encode("utf-8"))  # type: ignore
        proc.communicate()


# ----------------------------------------------------------------------
# Simple Expression
expr_source = "2 + 3 * 4;"
expr_model = Statements([BinOp("+", Integer(2), BinOp("*", Integer(3), Integer(4)))])

assert_equivalent(expr_source, expr_model)

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

assert_equivalent(source1, model1)

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

assert_equivalent(source2, model2)

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

assert_equivalent(source3, model3)

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

assert_equivalent(source4, model4)


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

model5 = None
# print(to_source(model5))

# ----------------------------------------------------------------------
# What's next?  If you've made it here are are looking for more,
# proceed to the file "func_models.py" and continue.
