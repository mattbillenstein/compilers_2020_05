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

expr_model  = BinOp('+', Integer(2),
                         BinOp('*', Integer(3), Integer(4)))

# Can you turn it back into source code?
print('0')
print(to_source(expr_model))
print()

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

model1 = Statements([
    PrintStatement(BinOp('+', Integer(2), BinOp('*', Integer(3), Integer(-4)))),
    PrintStatement(BinOp('-', Float(2.0), BinOp('/', Float(3.0), Float(-4.0)))),
    PrintStatement(BinOp('+', Integer(-2), Integer(3))),
    PrintStatement(BinOp('*', Integer(2), BinOp('+', Integer(3), Integer(-4)))),
])

print('1')
print(to_source(model1))
print()

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

model2 = Statements([
    Const('pi', Float(3.14159)),
    Var('tau', 'float'),
    Assign(Variable('tau'), BinOp('*', Float(2.0), Variable('pi'))),
    PrintStatement(Variable('tau')),
])

print('2')
print(to_source(model2))
print()

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

model3 = Statements([
    Assign(Var('a', 'int'), Integer(2)),
    Assign(Var('b', 'int'), Integer(3)),
    IfElse(BinOp('<', Variable('a') , Variable('b')), Statements([PrintStatement(Variable('a')),]), Statements([PrintStatement(Variable('b')),])),
])

print(3)
print(to_source(model3))
print()

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

model4 = Statements([
    Const('n', Integer(10)),
    Assign(Var('x', 'int'), Integer(1)),
    Assign(Var('fact', 'int'), Integer(1)),
    While(BinOp('<', Variable('x'), Variable('n')), Statements([
        Assign(Variable('fact'), BinOp('*', Variable('fact'), Variable('x'))),
        PrintStatement(Variable('x')),
        Assign(Variable('x'), BinOp('+', Variable('x'), Integer(1))),
        ])),
    ])
print(4)
print(to_source(model4))
print()

# ----------------------------------------------------------------------
# Program 5: Compound Expressions.  This program swaps the values of
# two variables using a single expression.
#

source5 = '''
    var x = 37;
    var y = 42;
    x = { var t = y; y = x; t; };     // Compound expression.
    print x;
    print y;
'''

model5 = Statements([
    Assign(Var('x', None), Integer(37)),
    Assign(Var('y', None), Integer(42)),
    Assign(Variable('x'), CompoundExpression(Statements([
        Assign(Var('t', None), Variable('y')),
        Assign(Variable('y'), Variable('x')),
        Variable('t'),
    ]))),
    PrintStatement(Variable('x')),
    PrintStatement(Variable('y')),
])

print(5)
print(to_source(model5))
print()

# ----------------------------------------------------------------------
# What's next?  If you've made it here are are looking for more,
# proceed to the file "func_models.py" and continue.

