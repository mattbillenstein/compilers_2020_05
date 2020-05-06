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
from wabbit.check import check_program
from wabbit.interp import interpret_program
from textwrap import dedent
import unittest

if 'unittest.util' in __import__('sys').modules:
    # Show full diff in self.assertEqual.
    __import__('sys').modules['unittest.util']._MAX_LENGTH = 999999999


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
        
        source = "2 + 3 * 4;"
        output = '14'
        tokens = [
            Token(type='INTEGER', value='2', lineno=1, index=0),
            Token(type='PLUS', value='+', lineno=1, index=2),
            Token(type='INTEGER', value='3', lineno=1, index=4),
            Token(type='TIMES', value='*', lineno=1, index=6),
            Token(type='INTEGER', value='4', lineno=1, index=8),
            Token(type='SEMI', value=';', lineno=1, index=9),
        ]
        model = [ExpressionStatement(BinOp('+', Int(2), BinOp('*', Int(3), Int(4))))]
        output = '14'
        self.assertEqual(self.decompiler.to_source(model), source)
        self.assertEqual(list(to_tokens(source)), tokens)
        self.assertEqual(parse_tokens(iter(tokens)), model)
        self.assertTrue(check_program(model))
        self.assertEqual(interpret_program(model), output)

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
        output = '14'

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
        self.assertTrue(check_program(model))
        self.assertEqual(interpret_program(model), output)

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
        output = '14'
        
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
            AssignStatement(DeclStorageLocation(StorageIdentifier('pi'), None, True), Float(3.14159)),
            AssignStatement(DeclStorageLocation(StorageIdentifier('tau'), 'float', False), value=None),
            AssignStatement(StorageIdentifier('tau'), BinOp('*', Float(2.0),
                StorageLocation(StorageIdentifier('pi')))),
            PrintStatement(StorageLocation(StorageIdentifier('tau')))
            ]

        self.assertEqual(self.decompiler.to_source(model), source)
        self.assertEqual(list(to_tokens(source)), tokens)
        self.assertEqual(parse_tokens(iter(tokens)), model)
        self.assertTrue(check_program(model))
        self.assertEqual(interpret_program(model), output)

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
        output = '14'
       
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
            AssignStatement(DeclStorageLocation(StorageIdentifier('a'), 'int', False), Int(2)),
            AssignStatement(DeclStorageLocation(StorageIdentifier('b'), 'int', False), Int(3)),
            ConditionalStatement(BinOp('<', StorageLocation(StorageIdentifier('a')),
                StorageLocation(StorageIdentifier('b'))), [
                    PrintStatement(StorageLocation(StorageIdentifier('a')))
                ], [
                    PrintStatement(StorageLocation(StorageIdentifier('b')))
                ]
            ),
            ]
        self.assertEqual(self.decompiler.to_source(model), source)
        self.assertEqual(list(to_tokens(source)), tokens)
        self.assertEqual(parse_tokens(iter(tokens)), model)
        self.assertTrue(check_program(model))
        self.assertEqual(interpret_program(model), output)

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
        output = '14'

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
                AssignStatement(DeclStorageLocation(StorageIdentifier('n'), None, True), Int(10)),
                AssignStatement(DeclStorageLocation(StorageIdentifier('x'), 'int', False), Int(1)),
                AssignStatement(DeclStorageLocation(StorageIdentifier('fact'), 'int', False), Int(1)),
                ConditionalLoopStatement(BinOp('<', StorageLocation(StorageIdentifier('x')),
                    StorageLocation(StorageIdentifier('n'))), [
                    AssignStatement(StorageIdentifier('fact'), BinOp('*',
                        StorageLocation(StorageIdentifier('fact')),
                        StorageLocation(StorageIdentifier('x')))),
                    PrintStatement(StorageLocation(StorageIdentifier('fact'))),
                    AssignStatement(StorageIdentifier('x'), BinOp('+',
                        StorageLocation(StorageIdentifier('x')), Int(1)))
                ]),
                ]
        self.assertEqual(self.decompiler.to_source(model), source)
        self.assertEqual(list(to_tokens(source)), tokens)
        self.assertEqual(parse_tokens(iter(tokens)), model)
        self.assertTrue(check_program(model))
        self.assertEqual(interpret_program(model), output)

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
        output = '14'

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
            AssignStatement(DeclStorageLocation(StorageIdentifier('x')), Int(37)),
            AssignStatement(DeclStorageLocation(StorageIdentifier('y')), Int(42)),
            AssignStatement(StorageIdentifier('x'), BlockExpression([
                AssignStatement(DeclStorageLocation(StorageIdentifier('t')), StorageLocation(StorageIdentifier('y'))),
                AssignStatement(StorageIdentifier('y'), StorageLocation(StorageIdentifier('x'))),
                ExpressionStatement(StorageLocation(StorageIdentifier('t'))),
                ])),
            PrintStatement(StorageLocation(StorageIdentifier('x'))),
            PrintStatement(StorageLocation(StorageIdentifier('y'))),
            ]
        self.assertEqual(self.decompiler.to_source(model), source)
        self.assertEqual(list(to_tokens(source)), tokens)
        self.assertEqual(parse_tokens(iter(tokens)), model)
        self.assertTrue(check_program(model))
        self.assertEqual(interpret_program(model), output)


class FuncModels(unittest.TestCase):
    def setUp(self):
        self.decompiler = WabbitDecompiler()
        self.maxDiff = None

    @unittest.skip
    def test_func(self):
        # ----------------------------------------------------------------------
        # Program 6: Functions.  The program prints out the first factorials
        # with various function definitions.
        #
        
        source = dedent('''\
        func add(x int, y int) int {
        \treturn x + y;
        }
        func mul(x int, y int) int {
        \treturn x * y;
        }
        func factorial(n int) int {
        \tif n == 0 {
        \t\treturn 1;
        \t} else {
        \t\treturn mul(n, factorial(add(n, -1)));
        \t}
        }
        func print_factorials(last int) int {
        \tvar x = 0;
        \twhile x < last {
        \t\tprint factorial(x);
        \t\tx = add(x, 1);
        \t}
        }
        func main() int {
        \tvar result = print_factorials(10);
        \treturn 0;
        }''')
        output = ''
        tokens = []
        model = [
                FuncDeclStatement('add', [['x', 'int'], ['y', 'int']], 'int', [
                    ReturnStatement(BinOp('+', StorageLocation('x'), StorageLocation('y'))),
                ]),
                FuncDeclStatement('mul', [['x', 'int'], ['y', 'int']], 'int', [
                    ReturnStatement(BinOp('*', StorageLocation('x'), StorageLocation('y'))),
                ]),
                FuncDeclStatement('factorial', [['n', 'int']], 'int', [
                    ConditionalStatement(BinOp('==', StorageLocation('n'), Int(0)), [
                        ReturnStatement(Int(1)),
                    ], [
                        ReturnStatement(FuncCall('mul', [StorageLocation('n'), FuncCall('factorial', [FuncCall('add', [StorageLocation('n'), UnOp('-', Int(1))])])]))
                    ]),
                ]),
                FuncDeclStatement('print_factorials', [['last', 'int']], 'int', [
                    AssignStatement(DeclStorageLocation('x', False), Int(0)),
                    ConditionalLoopStatement(BinOp('<', StorageLocation('x'), StorageLocation('last')), [
                        PrintStatement(FuncCall('factorial', [StorageLocation('x')])),
                        AssignStatement(StorageLocation('x'), FuncCall('add', [StorageLocation('x'), Int(1)]))
                    ])
                ]),
                FuncDeclStatement('main', [], 'int', [
                    AssignStatement(DeclStorageLocation('result', False), FuncCall('print_factorials', [Int(10)])),
                    ReturnStatement(Int(0))
                ]),
        ]
        self.assertEqual(self.decompiler.to_source(model), source)
        self.assertEqual(list(to_tokens(source)), tokens)
        self.assertEqual(parse_tokens(iter(tokens)), model)
        self.assertTrue(check_program(model))
        self.assertEqual(interpret_program(model), output)


    @unittest.skip
    def test_struct(self):
        # -----------------------------------------------------------------------------
        # Program 7: Structures.  The following program defines and uses a structure.
        #
        # You'll need to support structure definition, creation, and usage with other
        # parts of your language such as functions.
        
        source = '''
        struct Fraction {
           numerator int;
           denominator int;
        }
        
        func frac_mul(a Fraction, b Fraction) Fraction {
            return Fraction(a.numerator * b.numerator, a.denominator * b.denominator);
        }
        
        var x = Fraction(1, 4);
        var y = Fraction(3, 8);
        var c = frac_mul(x, y);
        print c.numerator;
        print c.denominator;
        c.numerator = c.numerator / 4;
        c.denominator = c.denominator / 4;
        print c.numerator;
        print c.denominator;
        '''
        output = ''
        tokens = []
        model = []
        self.assertEqual(self.decompiler.to_source(model), source)
        self.assertEqual(list(to_tokens(source)), tokens)
        self.assertEqual(parse_tokens(iter(tokens)), model)
        self.assertTrue(check_program(model))
        self.assertEqual(interpret_program(model), output)
        
    @unittest.skip
    def test_enums(self):
        # -----------------------------------------------------------------------------
        # Program 8: Enums.  The following program defines and uses an enum.
        #
        # To this, you'll need to support the enum definition, enum values,
        # and various forms of pattern matching including match, if let, and
        # while let.
        
        source = '''
        enum MaybeNumber {
            No;
            Integer(int);
            Float(float);
        }
        
        func add(a Number, b Number) Number {
           return match(a) {
                     No => Number::No;
                     Integer(x) => match(b) {
                           Integer(y) => Number::Integer(x + y);
                           Float(y) => Number::Float(float(x) + y);
                     };
                     Float(x) => match(b) {
                           Integer(y) => Number::Float(x + float(x));
                           Float(y) => Number::Float(x + y);
                     };
           };
        }
        
        var a = Number::Integer(42);
        var b = Number::Float(3.7);
        var c = add(a, b);
        
        if let Float(x) = c {
            print x;
        } else {
            print 0.0;
        }
        
        while let Integer(x) = a {
            print x;
            if x > 0 {
                a = Number::Integer(x-1);
            } else {
                a = Number::No;
            }
        }
        '''
        output = ''
        tokens = []
        model = []
        self.assertEqual(self.decompiler.to_source(model), source)
        self.assertEqual(list(to_tokens(source)), tokens)
        self.assertEqual(parse_tokens(iter(tokens)), model)
        self.assertTrue(check_program(model))
        self.assertEqual(interpret_program(model), output)
