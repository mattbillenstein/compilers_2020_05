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
from wabbit.parse import parse_source
from wabbit.hardparse import parse_source
from wabbit.interp import interpret_program

# ----------------------------------------------------------------------
# Simple Expression
#
# This one is given to you as an example. You might need to adapt it
# according to the names/classes you defined in wabbit.model

expr_source = "2 + 3 * 4;"

expr_model  = BinOp('+', Integer(2),
                         BinOp('*', Integer(3), Integer(4)))

# Can you turn it back into source code?
print('------ Simple Expression')
print(to_source(expr_model))
print("------ Interpret Expression")
print(interpret_program(expr_model))

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

# Are we allowed to use built-in types like list, tuple, for the model?
# Should everything be represented by a class definition (for consistency)?

model1 = Statements([      
    PrintStatement(BinOp('+',
                         Integer(2),
                         BinOp('*',
                               Integer(3),
                               UnaryOp('-', Integer(4))))),
    PrintStatement(BinOp('-',
                         Float(2.0),
                         BinOp('/',
                               Float(3.0),
                               UnaryOp('-', Float(4.0))))),
    PrintStatement(BinOp('+',
                         UnaryOp('-', Integer(2)),
                         Integer(3))),

    PrintStatement(BinOp('+',
                         BinOp('*', Integer(2), Integer(3)),
                         UnaryOp('-', Integer(4)))),
])

# Try parsing the source instead.
model1 = parse_source(source1)

# print(to_source(model1))
print('------ Model 1')
print(to_source(model1))
print("------ Interpret 1")
interpret_program(model1)

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
   ConstDefinition("pi", None, Float(3.14159)),
   VarDefinition("tau", "float", None),
   AssignmentStatement(NamedLocation("tau"), BinOp('*', Float(2.0), LoadLocation(NamedLocation("pi")))),
   PrintStatement(LoadLocation(NamedLocation("tau"))),
])

model2 = parse_source(source2);
print('------ Model 2')
print(to_source(model2))
print('------ Interpret 2')
interpret_program(model2)

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
        VarDefinition("a", "int", Integer(2)),
        VarDefinition("b", "int", Integer(3)),
        IfStatement(BinOp("<", LoadLocation(NamedLocation("a")), LoadLocation(NamedLocation("b"))),
                    Statements([
                       PrintStatement(LoadLocation(NamedLocation("a")))
                       ]),
                    Statements([
                       PrintStatement(LoadLocation(NamedLocation("b")))
                       ])
                    ),
        ])

model3 = parse_source(source3)
print('------ Model 3')
print(to_source(model3))
print('------ Interpret 3')
interpret_program(model3)

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
        ConstDefinition('n', None, Integer(10)),
        VarDefinition('x', 'int', Integer(1)),
        VarDefinition('fact', 'int', Integer(1)),
        WhileStatement(
            BinOp('<', LoadLocation(NamedLocation('x')), LoadLocation(NamedLocation('n'))),
            Statements([
                    AssignmentStatement(NamedLocation('fact'),
                                        BinOp('*',
                                              LoadLocation(NamedLocation('fact')),
                                              LoadLocation(NamedLocation('x')))),
                    PrintStatement(LoadLocation(NamedLocation('fact'))),
                    AssignmentStatement(NamedLocation('x'),
                                        BinOp('+',
                                              LoadLocation(NamedLocation('x')),
                                              Integer(1))),
                    ])
            ),
        ])

model4 = parse_source(source4)
print('------ Model 4')
print(to_source(model4))
print('------ Interpret 4')
interpret_program(model4)

# ----------------------------------------------------------------------
# Program 5: Compound Expressions.  This program swaps the values of
# two variables using a single expression.
#

source5 = '''
    var x = 37;
    var y = 42;
    x = { var t = y; y = x; t; };     // Compound expression.  What is scope of t?
    print x;
    print y;
'''

model5 = Statements([
        VarDefinition('x', None, Integer(37)),
        VarDefinition('y', None, Integer(42)),
        AssignmentStatement(NamedLocation('x'),
                            Compound(Statements([
                                VarDefinition('t', None, LoadLocation(NamedLocation('y'))),
                                AssignmentStatement(NamedLocation('y'), LoadLocation(NamedLocation('x'))),
                                ExpressionStatement(LoadLocation(NamedLocation('t'))),
                                ]))),
        PrintStatement(LoadLocation(NamedLocation('x'))),
        PrintStatement(LoadLocation(NamedLocation('y')))
        ])

model5 = parse_source(source5)

print('------ Model 5')
print(to_source(model5))
print('------ Interpret 5')
interpret_program(model5)

# ----------------------------------------------------------------------
# What's next?  If you've made it here are are looking for more,
# proceed to the file "func_models.py" and continue.

