# See https://github.com/dabeaz/compilers_2020_05/wiki/WabbitScript.md
from wabbit.model import (
    Assignment,
    Integer,
    Float,
    If,
    Name,
    UnaryOp,
    BinOp,
    ConstDef,
    VarDef,
    Print,
    to_source,
)

# ----------------------------------------------------------------------
# Simple Expression
expr_source = "2 + 3 * 4;"
expr_model = [BinOp("+", Integer(2), BinOp("*", Integer(3), Integer(4)))]

print("\n\n0\n-----------------------------------------------------------\n")
print(expr_source)
print(to_source(expr_model))
print()

# ----------------------------------------------------------------------
# Program 1: Printing
source1 = """
print 2 + 3 * -4;
print 2.0 - 3.0 / -4.0;
print -2 + 3;
print 2 * 3 + -4;
"""

model1 = [
    Print(BinOp("+", Integer(2), BinOp("*", Integer(3), UnaryOp("-", Integer(4))))),
    Print(BinOp("-", Float(2.0), BinOp("/", Float(3.0), UnaryOp("-", Float(4.0))))),
    Print(BinOp("+", UnaryOp("-", Integer(2)), Integer(3))),
    Print(BinOp("+", BinOp("*", Integer(2), Integer(3)), UnaryOp("-", Integer(4)))),
]

print("\n\n1\n-----------------------------------------------------------\n")
print(source1)
print()
print(to_source(model1))
print()

# ----------------------------------------------------------------------
# Program 2: Variable and constant declarations.
#            Expressions and assignment.
source2 = """
const pi = 3.14159;
var tau float;
tau = 2.0 * pi;
print tau;
"""

model2 = [
    ConstDef("pi", 3.14159),
    VarDef("tau", "float"),
    Assignment("tau", BinOp("*", Float(2.0), Name("pi"))),
    Print(Name("tau")),
]

print("\n\n2\n-----------------------------------------------------------\n")
print(source2)
print()
print(to_source(model2))
print()

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

model3 = [
    VarDef("a", "int", 2),
    VarDef("b", "int", 3),
    If(BinOp("<", Name("a"), Name("b")), Print(Name("a")), Print(Name("b"))),
]

print("\n\n3\n-----------------------------------------------------------\n")
print(source3)
print()
print(to_source(model3))
print()

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

model4 = None
# print(to_source(model4))

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
