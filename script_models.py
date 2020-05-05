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
from wabbit.decompiler import Decompiler
from textwrap import dedent
import unittest

class ScriptModels(unittest.TestCase):
    def setUp(self):
        self.decompiler = Decompiler()

    def test_simple(self):
        # ----------------------------------------------------------------------
        # Simple Expression
        #
        # This one is given to you as an example. You might need to adapt it
        # according to the names/classes you defined in wabbit.model
        
        expr_source = "2 + 3 * 4"
        expr_model = BinOp('+', Int(2),
                                 BinOp('*', Int(3), Int(4)))
        self.assertEqual(self.decompiler.to_source(expr_model), expr_source)

    def test_print(self):
        
        # ----------------------------------------------------------------------
        # Program 1: Printing
        #
        # Encode the following program which tests printing and evaluates some
        # simple expressions.
        #
        
        source = dedent("""\
        print 2 + 3 * -4;
        print 2.0 - 3.0 / -4.0;
        print -2 + 3;
        print 2 * 3 + -4;""")
        
        model = [
            PrintStatement(BinOp('+', Int(2), BinOp('*', Int(3), UnOp('-', Int(4))))),
            PrintStatement(BinOp('-', Float(2.0), BinOp('/', Float(3.0), UnOp('-', Float(4.0))))),
            PrintStatement(BinOp('+', UnOp('-', Int(2)), Int(3))),
            PrintStatement(BinOp('+', BinOp('*', Int(2), Int(3)), UnOp('-', Int(4)))),
        ]
        
        self.assertEqual(self.decompiler.to_source(model), source)

    def test_var(self):
        # ----------------------------------------------------------------------
        # Program 2: Variable and constant declarations. 
        #            Expressions and assignment.
        #
        # Encode the following statements.
        
        source = dedent("""\
        const pi = 3.14159;
        var tau float;
        tau = 2.0 * pi;
        print tau;""")
        
        model = [
            AssignStatement(DeclLocation('pi', None, True), Float(3.14159)),
            ExpressionStatement(DeclLocation('tau', 'float', False)),
            AssignStatement(Location('tau'), BinOp('*', Float(2.0), Location('pi'))),
            PrintStatement(Location('tau'))
        ]
        self.assertEqual(self.decompiler.to_source(model), source)

    def test_conditional(self):
        # ----------------------------------------------------------------------
        # Program 3: Conditionals.  This program prints out the minimum of
        # two values.
        #
        source = dedent('''\
        var a int = 2;
        var b int = 3;
        if a < b {
        \tprint a;
        } else {
        \tprint b;
        }''')
        
        model = [
            AssignStatement(DeclLocation('a', 'int', False), Int(2)),
            AssignStatement(DeclLocation('b', 'int', False), Int(3)),
            ConditionalStatement(BinOp('<', Location('a'), Location('b')), [
                    PrintStatement(Location('a'))
                ], [
                    PrintStatement(Location('b'))
                ]
            ),
        ]
        self.assertEqual(self.decompiler.to_source(model), source)

    def test_loop(self):
        # ----------------------------------------------------------------------
        # Program 4: Loops.  This program prints out the first 10 factorials.
        #
        
        source = dedent('''\
        const n = 10;
        var x int = 1;
        var fact int = 1;
        while x < n {
        \tfact = fact * x;
        \tprint fact;
        \tx = x + 1;
        }''')
        
        model = [
                AssignStatement(DeclLocation('n', None, True), Int(10)),
                AssignStatement(DeclLocation('x', 'int', False), Int(1)),
                AssignStatement(DeclLocation('fact', 'int', False), Int(1)),
                ConditionalLoopStatement(BinOp('<', Location('x'), Location('n')), [
                    AssignStatement(Location('fact'), BinOp('*', Location('fact'), Location('x'))),
                    PrintStatement(Location('fact')),
                    AssignStatement(Location('x'), BinOp('+', Location('x'), Int(1)))
                ]),
        ]
        
        self.assertEqual(self.decompiler.to_source(model), source)

    def test_compexpr(self):
        # ----------------------------------------------------------------------
        # Program 5: Compound Expressions.  This program swaps the values of
        # two variables using a single expression.
        #
        
        source = dedent('''\
        var x = 37;
        var y = 42;
        x = { var t = y; y = x; t; };
        print x;
        print y;''')
        
        model = [
            AssignStatement(DeclLocation('x'), Int(37)),
            AssignStatement(DeclLocation('y'), Int(42)),
            AssignStatement(Location('x'), BlockExpression([
                AssignStatement(DeclLocation('t'), Location('y')),
                AssignStatement(Location('y'), Location('x')),
                ExpressionStatement(Location('t')),
                ])),
            PrintStatement(Location('x')),
            PrintStatement(Location('y')),
                ]
        self.assertEqual(self.decompiler.to_source(model), source)


if __name__ == '__main__':
    unittest.main()
