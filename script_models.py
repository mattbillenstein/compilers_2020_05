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

from collections import ChainMap
from wabbit.model import *
from wabbit.interp import interpret
from wabbit.parse import parse_source

# ----------------------------------------------------------------------
# Simple Expression
#
# This one is given to you as an example. You might need to adapt it
# according to the names/classes you defined in wabbit.model

expr_source = "2 + 3 * 4"

expr_model = BinOp("+", Integer(2), BinOp("*", Integer(3), Integer(4)))
expr_model_a = Print(expr_model)  # for automated test with interpreter

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

print(parse_source("print 2.0 - 3.0 / -4.0;"))


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

# print("model1: expect the 4 following values:", -10, 2.75, 1, 2, "\n")
# interpret(model1, {})

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

# print(parse_source(source2))

expr1 = Const('pi', Type(None), Float(3.14159))
expr2 = Var('tau', Type('float'))
expr3 = Assignment(NamedLocation('tau'),
                   BinOp("*", Float(2.0),
                   LoadLocation(NamedLocation('pi'))))
expr4 = Print(LoadLocation(NamedLocation('tau')))
model2 = Statements(expr1, expr2, expr3, expr4)

# print(to_source(model2))

# print("\n\nmodel2: expect the following value:", 6.28318, "\n")
# interpret(model2, {})

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

expr1 = Var('a', Type('int'), Integer(2))
expr2 = Var('b', Type('int'), Integer(3))
expr3 = If(BinOp('<', LoadLocation(NamedLocation('a')),
                    LoadLocation(NamedLocation('b'))),
            Print(LoadLocation(NamedLocation('a'))),
            Print(LoadLocation(NamedLocation('b'))))

model3 = Statements(expr1, Statements(expr2), Statements(expr3))

# print(to_source(model3))

# print("\n\nmodel3: expect the following value:", 2, "\n")
# interpret(model3, {})

# ----------------------------------------------------------------------
# Program 4: Loops.  This program prints out the first 9 factorials.
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

expr1 = Const('n', Type(None), Integer(10))
expr2 = Var('x', Type('int'), Integer(1))
expr3 = Var('fact', Type('int'), Integer(1))

expr4 = Assignment(NamedLocation('fact'),
                   BinOp("*", LoadLocation(NamedLocation('fact')),
                         LoadLocation(NamedLocation('x'))))
expr5 = Print(LoadLocation(NamedLocation('fact')))
expr6 = Assignment(NamedLocation('x'),
                   BinOp("+", LoadLocation(NamedLocation('x')), Integer(1)))

expr7 = While(BinOp('<', LoadLocation(NamedLocation('x')),
                    LoadLocation(NamedLocation('n'))),
Statements(expr4, expr5, expr6))

model4 = Statements(expr1, expr2, expr3, expr7)
# print(to_source(model4))

# print("\n\nmodel4: expect factorials, from 1 to 362880", "\n")
# interpret(model4, {})

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

expr1 = Var('x', Type(None), Integer(37))
expr2 = Var('y', Type(None), Integer(42))

expr3a = Var('t', Type(None), LoadLocation(NamedLocation('y')))
expr3b = Assignment(NamedLocation('y'), LoadLocation(NamedLocation('x')))
expr3c = ExpressionStatement(LoadLocation(NamedLocation('t')))
expr3 = Assignment(NamedLocation('x'), Compound(expr3a, expr3b, expr3c))

expr4 = Print(LoadLocation(NamedLocation('x')))
expr5 = Print(LoadLocation(NamedLocation('y')))


model5 = Statements(expr1, expr2, expr3, expr4, expr5)
# print(to_source(model5))

# print("\n\nmodel5: expect the values 42 followed by 37", "\n")
# interpret(model5, {})

# ----------------------------------------------------------------------
# What's next?  If you've made it here are are looking for more,
# proceed to the file "func_models.py" and continue.


# Let's add a few examples for getting the scoping right for the
# interpreter, even though it is not required to do.

source_if_block = """
    var x int = 1;
    var y int = 37;
    print x;
    if x < 5 {
        var x int = 10;
        print x;
        print y;
        x = x + 10;
        print x;
    }
    print x;
    print y;
"""

var_x_1 = Var('x', Type('int'), Integer(1))
var_x_10 = Var('x', Type('int'), Integer(10))
var_x_100 = Var('x', Type('int'), Integer(100))

var_y_37 = Var('y', Type('int'), Integer(37))

print_x = Print(LoadLocation(NamedLocation('x')))
print_y = Print(LoadLocation(NamedLocation('y')))


x_inc_10 = Assignment(NamedLocation('x'),
                   BinOp("+", LoadLocation(NamedLocation('x')), Integer(10)))

expr_if = If(BinOp('<', LoadLocation(NamedLocation('x')), Integer(5)),
            Statements(var_x_10, print_x, print_y, x_inc_10, print_x))


model_if_block = Statements(var_x_1, var_y_37, print_x, expr_if, print_x, print_y)

# print("\n\nmodel_if_block: expect the values 1, 10, 37, 20, 1, 37", "\n")
# env = ChainMap()
# interpret(model_if_block, env)

source_else_block = """
    var x int = 1;
    var y int = 37;
    print x;
    if x > 5 {
        var x int = 10;
        print x;
        print y;
        x = x + 10;
        print x;
    } else {
        var x int = 100;
        print x;
    }
    print x;
    print y;
"""

# else block
# end else block

expr_else = If(BinOp('>', LoadLocation(NamedLocation('x')), Integer(5)),
            Statements(var_x_10, print_x, print_y, x_inc_10, print_x),
            Statements(var_x_100, print_x))

model_else_block = Statements(var_x_1, var_y_37, print_x, expr_else, print_x, print_y)

# print("\n\nmodel_if_block: expect the values 1, 100, 1, 37", "\n")
# env = ChainMap()
# interpret(model_else_block, env)


# add example of grouping variable with parens

source_group = "3 * (3 + 4)"
model_group = BinOp('*', Integer(3), Group(BinOp('+', Integer(3), Integer(4))))
model_group_print = Print(model_group)  # for automated test with interpreter
