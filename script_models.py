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

import sys
from wabbit.model import *
from wabbit.interp import Interpreter
from wabbit.parse import parse_source

# ----------------------------------------------------------------------
# Simple Expression
#
# This one is given to you as an example. You might need to adapt it
# according to the names/classes you defined in wabbit.model

expr_source = "2 + 3 * 4;"

#expr_model  = BinOp('+', Integer(2),
#                         BinOp('*', Integer(3), Integer(4)))


expr_model = parse_source(expr_source)
#print(expr_model)
# Can you turn it back into source code?
print(to_source(expr_model))
print(Interpreter().interpret(expr_model))

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

"""
model1 = Statements(
			PrintStatement(BinOp('+', Integer(2), BinOp("*", Integer(3), UnaryOp("-", Integer(4))))),
			PrintStatement(BinOp('-', Float(2.0), BinOp("*", Float(3.0), UnaryOp("-", Float(4.0))))),
			PrintStatement(BinOp('+', UnaryOp("-", Integer(2)), Integer(3))),
			PrintStatement(BinOp("+", BinOp("*", Integer(2), Integer(3)), UnaryOp("-", Integer(4))))
)
"""

model1 = parse_source(source1)
print("\n\nsource1:")
print(to_source(model1))
print(Interpreter().interpret(model1))

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

model2 = Statements(
	ConstDef("pi", None, Float(3.14159)),
	VarDef("tau", "float"),
	Assignment(Var("tau"), BinOp("*", Float(2.0), LocationLookup(Var("pi")))),
	PrintStatement(LocationLookup(Var("tau")))
)

model2 = parse_source(source2)
print("\n\nsource2:")
print(to_source(model2))
print(Interpreter().interpret(model2))

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
"""
model3 = Statements(
	VarDef("a", "int", Integer(2)),
	VarDef("b", "int", Integer(3)),
	IfConditional(BinOp("<", LocationLookup(Var("a")), LocationLookup(Var("b"))), 
				  Block(PrintStatement(LocationLookup(Var("a")))),
				  Block(PrintStatement(LocationLookup(Var("b")))))

)
"""
model3 = parse_source(source3)
print("\n\nsource3:")
print(to_source(model3))
print(Interpreter().interpret(model3))

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

"""
model4 = Statements(
			ConstDef("n", None, Integer(10)), 
			VarDef("x", "int", Integer(1)),
			VarDef("fact", "int", Integer(1)),
			While(BinOp("<", LocationLookup(Var("x")), LocationLookup(Var("n"))), 
				Block(
					Assignment(Var("fact"), BinOp("*", LocationLookup(Var("fact")), LocationLookup(Var("x")))),
					PrintStatement(LocationLookup(Var("fact"))),
					Assignment(Var("x"), BinOp("+", LocationLookup(Var("x")), Integer(1)))
				)
			)
)
"""

model4 = parse_source(source4)
print("\n\nsource4:")
print(to_source(model4))
print(Interpreter().interpret(model4))


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

"""model5 = Statements(
	VarDef("x", None,  Integer(37)),
	VarDef("y", None, Integer(42)),
	Assignment(Var("x"), 
				Compound(Statements(
						VarDef("t", None, LocationLookup(Var("y"))), 
						Assignment(Var("y"), LocationLookup(Var("x"))), 
						ExpressionStatement(LocationLookup(Var("t")))
						)
					)
			  ),
	PrintStatement(LocationLookup(Var("x"))),
	PrintStatement(LocationLookup(Var("y")))
)"""
model5 = parse_source(source5)


print("\n\nModel5:")
print(to_source(model5))
print(Interpreter().interpret(model5))


# ----------------------------------------------------------------------
# What's next?  If you've made it here are are looking for more,
# proceed to the file "func_models.py" and continue.

