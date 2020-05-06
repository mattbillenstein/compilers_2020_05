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
from wabbit.decompile import WabbitDecompiler
from wabbit.parse import WabbitParser
from textwrap import dedent
import unittest

class ScriptModels(unittest.TestCase):
    def setUp(self):
        self.decompiler = WabbitDecompiler()
        self.parser = WabbitParser()

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
        self.assertEqual(self.parser.to_model(source), model)

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
        self.assertEqual(self.parser.to_model(source), model)

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
            AssignStatement(DeclStorageLocation('pi', None, True), Float(3.14159)),
            ExpressionStatement(DeclStorageLocation('tau', 'float', False)),
            AssignStatement(StorageLocation('tau'), BinOp('*', Float(2.0), StorageLocation('pi'))),
            PrintStatement(StorageLocation('tau'))
        ]
        self.assertEqual(self.decompiler.to_source(model), source)
        self.assertEqual(self.parser.to_model(source), model)

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
            AssignStatement(DeclStorageLocation('a', 'int', False), Int(2)),
            AssignStatement(DeclStorageLocation('b', 'int', False), Int(3)),
            ConditionalStatement(BinOp('<', StorageLocation('a'), StorageLocation('b')), [
                    PrintStatement(StorageLocation('a'))
                ], [
                    PrintStatement(StorageLocation('b'))
                ]
            ),
        ]
        self.assertEqual(self.decompiler.to_source(model), source)
        self.assertEqual(self.parser.to_model(source), model)

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
                AssignStatement(DeclStorageLocation('n', None, True), Int(10)),
                AssignStatement(DeclStorageLocation('x', 'int', False), Int(1)),
                AssignStatement(DeclStorageLocation('fact', 'int', False), Int(1)),
                ConditionalLoopStatement(BinOp('<', StorageLocation('x'), StorageLocation('n')), [
                    AssignStatement(StorageLocation('fact'), BinOp('*', StorageLocation('fact'), StorageLocation('x'))),
                    PrintStatement(StorageLocation('fact')),
                    AssignStatement(StorageLocation('x'), BinOp('+', StorageLocation('x'), Int(1)))
                ]),
        ]
        
        self.assertEqual(self.decompiler.to_source(model), source)
        self.assertEqual(self.parser.to_model(source), model)

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
            AssignStatement(DeclStorageLocation('x'), Int(37)),
            AssignStatement(DeclStorageLocation('y'), Int(42)),
            AssignStatement(StorageLocation('x'), BlockExpression([
                AssignStatement(DeclStorageLocation('t'), StorageLocation('y')),
                AssignStatement(StorageLocation('y'), StorageLocation('x')),
                ExpressionStatement(StorageLocation('t')),
                ])),
            PrintStatement(StorageLocation('x')),
            PrintStatement(StorageLocation('y')),
                ]
        self.assertEqual(self.decompiler.to_source(model), source)
        self.assertEqual(self.parser.to_model(source), model)


if __name__ == '__main__':
    unittest.main()
