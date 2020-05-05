# script_models.py
# flake8: noqa
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

expr_source = "2 + 3 * 4"

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

expr1 = BinOp("+", Integer(2), BinOp("*", Integer(3), UnaryOp("-", Integer(4))))
expr2 = BinOp("-", Float(2.0), BinOp("/", Float(3.0), UnaryOp("-", Float(4.0))))
expr3 = BinOp("+", UnaryOp("-", Integer(2)), Integer(3))
expr4 = BinOp("+", BinOp("*", Integer(2), Integer(3)), UnaryOp("-", Integer(4)))

model1 = Statements(
    Print(expr1),
    Print(expr2),
    Print(expr3),
    Print(expr4)
    )

# print(to_source(model1))

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

expr1 = Const(Name('pi'), Type(None), Float(3.14159))
expr2 = Var(Name('tau'), Type('float'))
expr3 = Assignment(Name('tau'), BinOp("*", Float(2.0), Name('pi')))
expr4 = Print(Name('tau'))
model2 = Statements(expr1, expr2, expr3, expr4)

# print(to_source(model2))

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

expr1 = Var(Name('a'), Type('int'), Integer(2))
expr2 = Var(Name('b'), Type('int'), Integer(3))
expr3 = If(BinOp('<', Name('a'), Name('b')),
                    Print(Name('a')),
                    Print(Name('b')))

model3 = Statements(expr1, Statements(expr2), Statements(expr3))

# print(to_source(model3))

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

expr1 = Const(Name('n'), Type(None), Integer(10))
expr2 = Var(Name('x'), Type('int'), Integer(1))
expr3 = Var(Name('fact'), Type('int'), Integer(1))

expr4 = Assignment(Name('fact'), BinOp("*", Name('fact'), Name('x')))
expr5 = Print(Name('fact'))
expr6 = Assignment(Name('x'), BinOp("+", Name('x'), Integer(1)))

expr7 = While(BinOp('<', Name('x'), Name('n')), Statements(expr4, expr5, expr6))

model4 = Statements(expr1, expr2, expr3, expr7)
# print(to_source(model4))

# ----------------------------------------------------------------------
# Program 5: Compound Expressions.  This program swaps the values of
# two variables using a single expression.
#

source5 = """
    var x = 37;
    var y = 42;
    x = { var t = y; y = x; t; };
    print x;
    print y;
"""

expr1 = Var(Name('x'), Type(None), Integer(37))
expr2 = Var(Name('y'), Type(None), Integer(42))

expr3a = Var(Name('t'), Type(None), Name('y'))
expr3b = Assignment(Name('y'), Name('x'))
expr3c = Name('t')
expr3 = Assignment(Name('x'), Compound(expr3a, expr3b, expr3c))

expr4 = Print(Name('x'))
expr5 = Print(Name('y'))


model5 = Statements(expr1, expr2, expr3, expr4, expr5)
print(to_source(model5))

# ----------------------------------------------------------------------
# What's next?  If you've made it here are are looking for more,
# proceed to the file "func_models.py" and continue.
