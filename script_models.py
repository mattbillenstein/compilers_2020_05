# See https://github.com/dabeaz/compilers_2020_05/wiki/WabbitScript.md
import utils
from wabbit.check_syntax import check_syntax
from wabbit.interp import interpret_program
from wabbit.format_json import format_json
from wabbit.format_source import format_source
from wabbit.model import (
    Assign,
    BinOp,
    Block,
    ConstDef,
    Float,
    If,
    Integer,
    Location,
    Name,
    Print,
    UnaryOp,
    VarDef,
    While,
    Statements,
)
from wabbit.tokenize import tokenize


def check(source, model):
    check_syntax(model)
    transpiled_source = format_source(model)
    if transpiled_source.strip() != source.strip():
        utils.print_diff(source, transpiled_source)


def dump_json(model, label):
    with open(f"/tmp/model_{label}.json", "w") as fh:
        fh.write(format_json(model))


sources = []
models = []

# ----------------------------------------------------------------------
# Program 0: Simple Expression
sources.append("2 + 3 * 4;")
models.append(Statements([BinOp("+", Integer(2), BinOp("*", Integer(3), Integer(4)))]))


# ----------------------------------------------------------------------
# Program 1: Printing
sources.append(
    """
print 2 + 3 * -4;
print 2.0 - 3.0 / -4.0;
print -2 + 3;
print 2 * 3 + -4;
"""
)

models.append(
    Statements(
        [
            Print(BinOp("+", Integer(2), BinOp("*", Integer(3), UnaryOp("-", Integer(4))))),
            Print(BinOp("-", Float(2.0), BinOp("/", Float(3.0), UnaryOp("-", Float(4.0))))),
            Print(BinOp("+", UnaryOp("-", Integer(2)), Integer(3))),
            Print(BinOp("+", BinOp("*", Integer(2), Integer(3)), UnaryOp("-", Integer(4)))),
        ]
    )
)

# ----------------------------------------------------------------------
# Program 2: Variable and constant declarations.
#            Expressions and assignment.
sources.append(
    """
const pi = 3.14159;
var tau float;
tau = 2.0 * pi;
print tau;
"""
)

models.append(
    Statements(
        [
            ConstDef("pi", None, 3.14159),
            VarDef("tau", "float", None),
            Assign(Location("tau"), BinOp("*", Float(2.0), Name("pi"))),
            Print(Name("tau")),
        ]
    )
)

# ----------------------------------------------------------------------
# Program 3: Conditionals.  This program prints out the minimum of
# two values.
#
sources.append(
    """
var a int = 2;
var b int = 3;
if a < b {
    print a;
} else {
    print b;
}
"""
)

models.append(
    Statements(
        [
            VarDef("a", "int", Integer(2)),
            VarDef("b", "int", Integer(3)),
            If(
                BinOp("<", Name("a"), Name("b")),
                Statements([Print(Name("a"))]),
                Statements([Print(Name("b"))]),
            ),
        ]
    )
)


# ----------------------------------------------------------------------
# Program 4: Loops.  This program prints out the first 10 factorials.
#

sources.append(
    """
const n = 10;
var x int = 1;
var fact int = 1;

while x < n {
    fact = fact * x;
    print fact;
    x = x + 1;
}
"""
)

models.append(
    Statements(
        [
            ConstDef("n", None, 10),
            VarDef("x", "int", Integer(1)),
            VarDef("fact", "int", Integer(1)),
            While(
                BinOp("<", Name("x"), Name("n")),
                Statements(
                    [
                        Assign(Location("fact"), BinOp("*", Name("fact"), Name("x"))),
                        Print(Name("fact")),
                        Assign(Location("x"), BinOp("+", Name("x"), Integer(1))),
                    ]
                ),
            ),
        ]
    )
)


# ----------------------------------------------------------------------
# Program 5: Compound Expressions.  This program swaps the values of
# two variables using a single expression.
#

sources.append(
    """
var x = 37;
var y = 42;
x = { var t = y; y = x; t; };     // Compound expression.
print x;
print y;
"""
)

models.append(
    Statements(
        [
            VarDef("t", None, Integer(77)),
            VarDef("x", None, Integer(37)),
            VarDef("y", None, Integer(42)),
            Assign(
                Location("x"),
                Block(
                    Statements(
                        [VarDef("t", None, Name("y")), Assign(Location("y"), Name("x")), Name("t")]
                    )
                ),
            ),
            Print(Name("t")),
            Print(Name("x")),
            Print(Name("y")),
        ]
    )
)


sources.append(
    """
var i = 0;
while i < 3 {
    print i;
    i = i + 1;
}
"""
)

models.append(
    Statements(
        [
            VarDef("i", None, Integer(0)),
            While(
                BinOp("<", Name("i"), Integer(3)),
                Statements(
                    [Print(Name("i")), Assign(Location("i"), BinOp("+", Name("i"), Integer(1)))]
                ),
            ),
        ]
    )
)

if __name__ == "__main__":
    for i, (source, model) in enumerate(zip(sources, models)):
        print("\n\n--------------------------------------------------------------------------")
        print(i, "\n")
        utils.print_source(source)
        tokens = list(tokenize(source))
        check(source, model)
        dump_json(model, i)
        print("Interpreter output:\n")
        interpret_program(model)
