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
print(to_source(expr_model))

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

model1 = Program([Statement(PrintStatement(BinOp('+', Integer(2), BinOp("*", Integer(3), UnaryOp("-", Integer(4)))))),
				Statement(PrintStatement(BinOp('-', Float(2.0), BinOp("*", Float(3.0), UnaryOp("-", Float(4.0)))))),
				Statement(PrintStatement(BinOp('+', UnaryOp("-", Integer(2)), Integer(3)))),
				Statement(PrintStatement(BinOp("+", BinOp("*", Integer(2), Integer(3)), UnaryOp("-", Integer(4)))))
])

print("\n\nsource1:")
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

model2 = Program([
	Statement(Assignment(ConstDef(Var("pi")), Float(3.14159))),
	Statement(VarDef("tau", "float")),
	Statement(Assignment(Var("tau"), BinOp("+", Float(2.0), Var("pi")))),
	Statement(PrintStatement(Var("tau")))
])

print("\n\nsource2:")
print(to_source(model2))

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

model3 = Program([
	Statement(Assignment(VarDef("a", "int"), Integer(2))),
	Statement(Assignment(VarDef("b", "int"), Integer(3))),
	IfConditional(BinOp("<", Var("a"), Var("b")), 
				  Block([Statement(PrintStatement(Var("a")))]),
				  Block([Statement(PrintStatement(Var("b")))]))

])

print("\n\nsource3:")
print(to_source(model3))

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

model4 = Program([

])

# print(to_source(model4))

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

model5 = Program([
	Statement(Assignment(VarDef("x"), Integer(37))),
	Statement(Assignment(VarDef("y"), Integer(42))),
	Statement(Assignment(Var("x"), Block([Statement(Assignment(VarDef("t"), Var("y"))), Statement(Assignment(Var("x"), Var("y"))), Statement(Var("t"))]))),
	Statement(PrintStatement(Var("x"))),
	Statement(PrintStatement(Var("y")))

])

print("\n\nModel5:")
print(to_source(model5))

# ----------------------------------------------------------------------
# What's next?  If you've made it here are are looking for more,
# proceed to the file "func_models.py" and continue.

