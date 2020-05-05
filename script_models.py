#!/usr/bin/env python3

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
from wabbit.source_visitor import to_source

def compare_source(source, expected):
    if source.strip('\n') != expected.strip('\n'):
        print(repr(source.strip('\n')))
        print(repr(expected.strip('\n')))
        raise ValueError('Mismatched Source')

# ----------------------------------------------------------------------
# Simple Expression
#
# This one is given to you as an example. You might need to adapt it
# according to the names/classes you defined in wabbit.model

expr_source = "2 + 3 * 4;"

expr_model  = Block([
    BinOp('+',
        Integer(2),
        BinOp('*', Integer(3), Integer(4)),
    ),
])

compare_source(to_source(expr_model), expr_source)

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

model1 = Block([
    Print(BinOp('+', Integer(2), BinOp('*', Integer(3), Integer(-4)))),
    Print(BinOp('-', Float(2.0), BinOp('/', Float(3.0), Float(-4.0)))),
    Print(BinOp('+', Integer(-2), Integer(3))),
    Print(BinOp('+', BinOp('*', Integer(2), Integer(3)), Integer(-4))),
], indent=' '*4)

compare_source(to_source(model1), source1)

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

model2 = Block([
    Const(Name('pi'), Float(3.14159)),
    Var(Name('tau'), type='float'),
    Assign(Name('tau'), BinOp('*', Float(2.0), Name('pi'))),
    Print(Name('tau')),
], indent=' '*4)

compare_source(to_source(model2), source2)

# ----------------------------------------------------------------------
# Program 3: Conditionals.  This program prints out the minimum of
# two values.
#
source3 = '''
    var a int = 2;
    var b int = 3;
    if a < b {
        print a;
    } else {
        print b;
    }
'''

model3 = Block([
    Var(Name('a'), Integer(2), type='int'),
    Var(Name('b'), Integer(3), type='int'),
    If(
        BinOp('<', Name('a'), Name('b')),
        Block([Print(Name('a'))], indent=' '*4),
        Block([Print(Name('b'))], indent=' '*4),
    )
], indent=' '*4)

compare_source(to_source(model3), source3)

# ----------------------------------------------------------------------
# Program 4: Loops.  This program prints out the first 10 factorials.
#

source4 = '''
    const n = 10;
    var x int = 1;
    var fact int = 1;
    while x < n {
        fact = fact * x;
        print fact;
        x = x + 1;
    }
'''

model4 = Block([
    Const(Name('n'), Integer(10)),
    Var(Name('x'), Integer(1), type='int'),
    Var(Name('fact'), Integer(1), type='int'),
    While(
        BinOp('<', Name('x'), Name('n')),
        Block([
            Assign(Name('fact'), BinOp('*', Name('fact'), Name('x'))),
            Print(Name('fact')),
            Assign(Name('x'), BinOp('+', Name('x'), Integer(1))),
        ], indent=' '*4),
    )
], indent=' '*4)

compare_source(to_source(model4), source4)

# ----------------------------------------------------------------------
# Program 5: Compound Expressions.  This program swaps the values of
# two variables using a single expression.
#

source5 = '''
    var x = 37;
    var y = 42;
    x = { var t = y; y = x; t; };
    print x;
    print y;
'''

model5 = Block([
    Var(Name('x'), Integer(37)),
    Var(Name('y'), Integer(42)),
    Assign(Name('x'), Compound([
            Var(Name('t'), Name('y')),
            Assign(Name('y'), Name('x')),
            Name('t'),
        ]),
    ),
    Print(Name('x')),
    Print(Name('y')),
], indent=' '*4)

compare_source(to_source(model5), source5)

# ----------------------------------------------------------------------
# What's next?  If you've made it here are are looking for more,
# proceed to the file "func_models.py" and continue.
