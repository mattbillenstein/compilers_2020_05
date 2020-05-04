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

s = to_source(expr_model)
assert s.strip('\n') == expr_source.strip('\n'), (s, expr_source)

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

s = to_source(model1) 
assert s.strip('\n') == source1.strip('\n'), (s, source1)

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
    Const('pi', Float(3.14159)),
    Var('tau', type='float'),
    Assign('tau', BinOp('*', Float(2.0), 'pi')),
    Print('tau'),
], indent=' '*4)

s = to_source(model2)
assert s.strip('\n') == source2.strip('\n'), (s, source2)

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
    Var('a', Integer(2), type='int'),
    Var('b', Integer(3), type='int'),
    If(
        BinOp('<', 'a', 'b'),
        Block([Print('a')], indent=' '*4),
        Block([Print('b')], indent=' '*4),
    )
], indent=' '*4)

s = to_source(model3)
assert s.strip('\n') == source3.strip('\n'), (s, source3)

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
    Const('n', Integer(10)),
    Var('x', Integer(1), type='int'),
    Var('fact', Integer(1), type='int'),
    While(
        BinOp('<', 'x', 'n'),
        Block([
            Assign('fact', BinOp('*', 'fact', 'x')),
            Print('fact'),
            Assign('x', BinOp('+', 'x', Integer(1))),
        ], indent=' '*4),
    )
], indent=' '*4)

s = to_source(model4)
assert s.strip('\n') == source4.strip('\n'), (s, source4)

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
    Var('x', Integer(37)),
    Var('y', Integer(42)),
    Assign('x', Compound([
            Var('t', 'y'),
            Assign('y', 'x'),
            't',
        ]),
    ),
    Print('x'),
    Print('y'),
], indent=' '*4)

s = to_source(model5)
assert s.strip('\n') == source5.strip('\n'), (s, source5)

# ----------------------------------------------------------------------
# What's next?  If you've made it here are are looking for more,
# proceed to the file "func_models.py" and continue.

