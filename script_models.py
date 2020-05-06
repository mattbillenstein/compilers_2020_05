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
from wabbit.parse import parse_tokens
from wabbit.tokenize import to_tokens, Token
from textwrap import dedent
import unittest


class ScriptModels(unittest.TestCase):
    def setUp(self):
        self.decompiler = WabbitDecompiler()
        self.maxDiff = None

    def test_simple(self):
        # ----------------------------------------------------------------------
        # Simple Expression
        #
        # This one is given to you as an example. You might need to adapt it
        # according to the names/classes you defined in wabbit.model
        
        source = "2 + 3 * 4"
        tokens = [
            Token(type='INTEGER', value='2', lineno=1, index=0),
            Token(type='PLUS', value='+', lineno=1, index=2),
            Token(type='INTEGER', value='3', lineno=1, index=4),
            Token(type='TIMES', value='*', lineno=1, index=6),
            Token(type='INTEGER', value='4', lineno=1, index=8)
        ]
        model = [BinOp('+', Int(2), BinOp('*', Int(3), Int(4)))]
        self.assertEqual(self.decompiler.to_source(model), source)
        self.assertEqual(list(to_tokens(source)), tokens)
        self.assertEqual(parse_tokens(iter(tokens)), model)

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

        tokens = [
            Token(type='PRINT', value='print', lineno=1, index=0),
            Token(type='INTEGER', value='2', lineno=1, index=6),
            Token(type='PLUS', value='+', lineno=1, index=8),
            Token(type='INTEGER', value='3', lineno=1, index=10),
            Token(type='TIMES', value='*', lineno=1, index=12),
            Token(type='MINUS', value='-', lineno=1, index=14),
            Token(type='INTEGER', value='4', lineno=1, index=15),
            Token(type='SEMI', value=';', lineno=1, index=16),
            Token(type='PRINT', value='print', lineno=1, index=18),
            Token(type='FLOAT', value='2.0', lineno=1, index=24),
            Token(type='MINUS', value='-', lineno=1, index=28),
            Token(type='FLOAT', value='3.0', lineno=1, index=30),
            Token(type='DIVIDE', value='/', lineno=1, index=34),
            Token(type='MINUS', value='-', lineno=1, index=36),
            Token(type='FLOAT', value='4.0', lineno=1, index=37),
            Token(type='SEMI', value=';', lineno=1, index=40),
            Token(type='PRINT', value='print', lineno=1, index=42),
            Token(type='MINUS', value='-', lineno=1, index=48),
            Token(type='INTEGER', value='2', lineno=1, index=49),
            Token(type='PLUS', value='+', lineno=1, index=51),
            Token(type='INTEGER', value='3', lineno=1, index=53),
            Token(type='SEMI', value=';', lineno=1, index=54),
            Token(type='PRINT', value='print', lineno=1, index=56),
            Token(type='INTEGER', value='2', lineno=1, index=62),
            Token(type='TIMES', value='*', lineno=1, index=64),
            Token(type='INTEGER', value='3', lineno=1, index=66),
            Token(type='PLUS', value='+', lineno=1, index=68),
            Token(type='MINUS', value='-', lineno=1, index=70),
            Token(type='INTEGER', value='4', lineno=1, index=71),
            Token(type='SEMI', value=';', lineno=1, index=72),
        ]
        
        model = [
            PrintStatement(BinOp('+', Int(2), BinOp('*', Int(3), UnOp('-', Int(4))))),
            PrintStatement(BinOp('-', Float(2.0), BinOp('/', Float(3.0), UnOp('-', Float(4.0))))),
            PrintStatement(BinOp('+', UnOp('-', Int(2)), Int(3))),
            PrintStatement(BinOp('+', BinOp('*', Int(2), Int(3)), UnOp('-', Int(4)))),
            ]
        
        self.assertEqual(self.decompiler.to_source(model), source)
        self.assertEqual(list(to_tokens(source)), tokens)
        self.assertEqual(parse_tokens(iter(tokens)), model)

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
        
        tokens = [
            Token(type='CONST', value='const', lineno=1, index=0),
            Token(type='NAME', value='pi', lineno=1, index=6),
            Token(type='ASSIGN', value='=', lineno=1, index=9),
            Token(type='FLOAT', value='3.14159', lineno=1, index=11),
            Token(type='SEMI', value=';', lineno=1, index=18),
            Token(type='VAR', value='var', lineno=1, index=20),
            Token(type='NAME', value='tau', lineno=1, index=24),
            Token(type='NAME', value='float', lineno=1, index=28),
            Token(type='SEMI', value=';', lineno=1, index=33),
            Token(type='NAME', value='tau', lineno=1, index=35),
            Token(type='ASSIGN', value='=', lineno=1, index=39),
            Token(type='FLOAT', value='2.0', lineno=1, index=41),
            Token(type='TIMES', value='*', lineno=1, index=45),
            Token(type='NAME', value='pi', lineno=1, index=47),
            Token(type='SEMI', value=';', lineno=1, index=49),
            Token(type='PRINT', value='print', lineno=1, index=51),
            Token(type='NAME', value='tau', lineno=1, index=57),
            Token(type='SEMI', value=';', lineno=1, index=60)
        ]
        model = [
            AssignStatement(DeclStorageLocation('pi', None, True), Float(3.14159)),
            AssignStatement(DeclStorageLocation('tau', 'float', False), value=None),
            AssignStatement(StorageLocation('tau'), BinOp('*', Float(2.0), StorageLocation('pi'))),
            PrintStatement(StorageLocation('tau'))
            ]

        self.assertEqual(self.decompiler.to_source(model), source)
        self.assertEqual(list(to_tokens(source)), tokens)
        self.assertEqual(parse_tokens(iter(tokens)), model)

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
       
        tokens = [
            Token(type='VAR', value='var', lineno=1, index=0),
            Token(type='NAME', value='a', lineno=1, index=4),
            Token(type='NAME', value='int', lineno=1, index=6),
            Token(type='ASSIGN', value='=', lineno=1, index=10),
            Token(type='INTEGER', value='2', lineno=1, index=12),
            Token(type='SEMI', value=';', lineno=1, index=13),
            Token(type='VAR', value='var', lineno=1, index=15),
            Token(type='NAME', value='b', lineno=1, index=19),
            Token(type='NAME', value='int', lineno=1, index=21),
            Token(type='ASSIGN', value='=', lineno=1, index=25),
            Token(type='INTEGER', value='3', lineno=1, index=27),
            Token(type='SEMI', value=';', lineno=1, index=28),
            Token(type='IF', value='if', lineno=1, index=30),
            Token(type='NAME', value='a', lineno=1, index=33),
            Token(type='LT', value='<', lineno=1, index=35),
            Token(type='NAME', value='b', lineno=1, index=37),
            Token(type='LBRACE', value='{', lineno=1, index=39),
            Token(type='PRINT', value='print', lineno=1, index=42),
            Token(type='NAME', value='a', lineno=1, index=48),
            Token(type='SEMI', value=';', lineno=1, index=49),
            Token(type='RBRACE', value='}', lineno=1, index=51),
            Token(type='ELSE', value='else', lineno=1, index=53),
            Token(type='LBRACE', value='{', lineno=1, index=58),
            Token(type='PRINT', value='print', lineno=1, index=61),
            Token(type='NAME', value='b', lineno=1, index=67),
            Token(type='SEMI', value=';', lineno=1, index=68),
            Token(type='RBRACE', value='}', lineno=1, index=70),
        ]

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
        self.assertEqual(list(to_tokens(source)), tokens)
        self.assertEqual(parse_tokens(iter(tokens)), model)

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

        tokens = [
            Token(type='CONST', value='const', lineno=1, index=0),
            Token(type='NAME', value='n', lineno=1, index=6),
            Token(type='ASSIGN', value='=', lineno=1, index=8),
            Token(type='INTEGER', value='10', lineno=1, index=10),
            Token(type='SEMI', value=';', lineno=1, index=12),
            Token(type='VAR', value='var', lineno=1, index=14),
            Token(type='NAME', value='x', lineno=1, index=18),
            Token(type='NAME', value='int', lineno=1, index=20),
            Token(type='ASSIGN', value='=', lineno=1, index=24),
            Token(type='INTEGER', value='1', lineno=1, index=26),
            Token(type='SEMI', value=';', lineno=1, index=27),
            Token(type='VAR', value='var', lineno=1, index=29),
            Token(type='NAME', value='fact', lineno=1, index=33),
            Token(type='NAME', value='int', lineno=1, index=38),
            Token(type='ASSIGN', value='=', lineno=1, index=42),
            Token(type='INTEGER', value='1', lineno=1, index=44),
            Token(type='SEMI', value=';', lineno=1, index=45),
            Token(type='WHILE', value='while', lineno=1, index=47),
            Token(type='NAME', value='x', lineno=1, index=53),
            Token(type='LT', value='<', lineno=1, index=55),
            Token(type='NAME', value='n', lineno=1, index=57),
            Token(type='LBRACE', value='{', lineno=1, index=59),
            Token(type='NAME', value='fact', lineno=1, index=62),
            Token(type='ASSIGN', value='=', lineno=1, index=67),
            Token(type='NAME', value='fact', lineno=1, index=69),
            Token(type='TIMES', value='*', lineno=1, index=74),
            Token(type='NAME', value='x', lineno=1, index=76),
            Token(type='SEMI', value=';', lineno=1, index=77),
            Token(type='PRINT', value='print', lineno=1, index=80),
            Token(type='NAME', value='fact', lineno=1, index=86),
            Token(type='SEMI', value=';', lineno=1, index=90),
            Token(type='NAME', value='x', lineno=1, index=93),
            Token(type='ASSIGN', value='=', lineno=1, index=95),
            Token(type='NAME', value='x', lineno=1, index=97),
            Token(type='PLUS', value='+', lineno=1, index=99),
            Token(type='INTEGER', value='1', lineno=1, index=101),
            Token(type='SEMI', value=';', lineno=1, index=102),
            Token(type='RBRACE', value='}', lineno=1, index=104),
        ]
        
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
        self.assertEqual(list(to_tokens(source)), tokens)
        self.assertEqual(parse_tokens(iter(tokens)), model)

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

        tokens = [
            Token(type='VAR', value='var', lineno=1, index=0),
            Token(type='NAME', value='x', lineno=1, index=4),
            Token(type='ASSIGN', value='=', lineno=1, index=6),
            Token(type='INTEGER', value='37', lineno=1, index=8),
            Token(type='SEMI', value=';', lineno=1, index=10),
            Token(type='VAR', value='var', lineno=1, index=12),
            Token(type='NAME', value='y', lineno=1, index=16),
            Token(type='ASSIGN', value='=', lineno=1, index=18),
            Token(type='INTEGER', value='42', lineno=1, index=20),
            Token(type='SEMI', value=';', lineno=1, index=22),
            Token(type='NAME', value='x', lineno=1, index=24),
            Token(type='ASSIGN', value='=', lineno=1, index=26),
            Token(type='LBRACE', value='{', lineno=1, index=28),
            Token(type='VAR', value='var', lineno=1, index=30),
            Token(type='NAME', value='t', lineno=1, index=34),
            Token(type='ASSIGN', value='=', lineno=1, index=36),
            Token(type='NAME', value='y', lineno=1, index=38),
            Token(type='SEMI', value=';', lineno=1, index=39),
            Token(type='NAME', value='y', lineno=1, index=41),
            Token(type='ASSIGN', value='=', lineno=1, index=43),
            Token(type='NAME', value='x', lineno=1, index=45),
            Token(type='SEMI', value=';', lineno=1, index=46),
            Token(type='NAME', value='t', lineno=1, index=48),
            Token(type='SEMI', value=';', lineno=1, index=49),
            Token(type='RBRACE', value='}', lineno=1, index=51),
            Token(type='SEMI', value=';', lineno=1, index=52),
            Token(type='PRINT', value='print', lineno=1, index=54),
            Token(type='NAME', value='x', lineno=1, index=60),
            Token(type='SEMI', value=';', lineno=1, index=61),
            Token(type='PRINT', value='print', lineno=1, index=63),
            Token(type='NAME', value='y', lineno=1, index=69),
            Token(type='SEMI', value=';', lineno=1, index=70),
        ]
        
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
        self.assertEqual(list(to_tokens(source)), tokens)
        self.assertEqual(parse_tokens(iter(tokens)), model)


if __name__ == '__main__':
    unittest.main()
