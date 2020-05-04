# script_models.py
#
# Within the bowels of your compiler, you need to represent programs
# as data structures.   In this file, you will manually encode
# some simple Wabbit programs using the data model you're creating
# in the file wabbit/model.py
#
# The purpose of this exercise is two-fold:
#
#   1. Make sure you understand the data model of your compiler.
#   2. Have some program structures that you can use for later testing
#      and experimentation.
#
# This file is broken into sections. Follow the instructions for
# each part.  Parts of this file might be referenced in later
# parts of the project.  Plan to have a lot of discussion.
#
# Note: This file only includes examples for WabbitScript.  See
#
# https://github.com/dabeaz/compilers_2020_05/wiki/WabbitScript.md


from wabbit.model import *

# ----------------------------------------------------------------------
# Simple Expression
#
# This one is given to you as an example. You might need to adapt it
# according to the names/classes you defined in wabbit.model

expr_source = "2 + 3 * 4;"

expr_model = BinOp("+", Integer(2), BinOp("*", Integer(3), Integer(4)))

# Can you turn it back into source code?
# print(to_source(expr_model))

# ----------------------------------------------------------------------
# Program 1: Printing
#
# Encode the following program which tests printing and evaluates some
# simple expressions.
#

source1 = """
    print 2 + 3 * -4;
    print 2.0 - 3.0 / -4.0;
    print -2 + 3;
    print 2 * 3 + -4;
"""

# model1 = [PrintStatement(BinOp("*", BinOp("+", Integer(2), Integer(3)), Integer(-4))),
#           PrintStatement(BinOp('/', BinOp('-', Float(2.0), Float(3.0), Float('-4.0')))),
#           PrintStatement(BinOp('+', Integer(-2), Integer(3))),
#           PrintStatement(BinOp('*', Integer('')))
#           ]

model1 = Program(
    PrintStatement(BinOp.mult(BinOp.add(Integer(2), Integer(3)), Integer(-4))),
    PrintStatement(BinOp.div(BinOp.subtract(Float(2.0), Float(3.0)), Float(-4.0))),
    PrintStatement(BinOp.add(Integer(-2), Integer(3))),
    PrintStatement(BinOp.add(BinOp.mult(Integer(2), Integer(3)), Integer(-4))),
)

print(repr(model1))
print(to_source(model1))

# ----------------------------------------------------------------------
# Program 2: Variable and constant declarations.
#            Expressions and assignment.
#
# Encode the following statements.

source2 = """
    const pi = 3.14159;  
    var tau float;
    tau = 2.0 * pi;
    print tau;
"""

model2 = Program(
    Const("pi", Float(3.14159)),
    VarDeclaration("tau", type="float"),
    Var("tau", BinOp.mult(Float(2.0), Identifier("pi"))),
    PrintStatement(Identifier("tau")),
)

print(repr(model2))
print(to_source(model2))

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

model3 = Program(
    Var(left="a", value=Integer(2), type_="int"),
    Var(left="b", value=Integer(3), type_="int"),
    IfStatement(
        condition=LessThan(Identifier("a"), Identifier("b")),
        body=PrintStatement(Identifier("a")),  # Maybe body should be a 'Clause' instead
        else_clause=PrintStatement(Identifier("b")),
    ),
)

print(repr(model3))
print(to_source(model3))

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

model4 = Program(
    Const(left="n", value=Integer(10)),
    Var(left="x", value=Integer(1), type_="int"),
    Var(left="fact", value=Integer(1), type_="int"),
    WhileLoop(
        condition=LessThan(Identifier("x"), Identifier("n")),
        body=Clause(
            Assignment(left="fact", value=BinOp.mult(Identifier("fact"), Identifier("x"))),
            PrintStatement(Identifier("fact")),
            Assignment(left="x", value=BinOp.add(Identifier("x"), Integer(1))),
        ),
    ),
)

print(repr(model4))
print(to_source(model4))

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

model5 = Program(
    Var(left="x", value=Integer(37)),
    Var(left="y", value=Integer(42)),
    Assignment(
        left="x",
        value=CompoundExpr(
            Var(left="t", value=Identifier("y")),
            Assignment(left="y", value=Identifier("x")),
            Identifier("t"),
        ),
    ),
    PrintStatement(Identifier('x')),
    PrintStatement(Identifier('y'))
)
print(repr(model5))
print(to_source(model5))

# ----------------------------------------------------------------------
# What's next?  If you've made it here are are looking for more,
# proceed to the file "func_models.py" and continue.
