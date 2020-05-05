# func_models.py
#
# The WabbitFunc language extends WabbitScript with support for
# user-defined functions.  This requires additional support
# for the following constructs:
#
#     1. Function definitions.
#     2. Function application.
#     3. The return statement.
# 
# This file contains a single example that you should represent
# using your model.  Please see the following document for more information.
#
# https://github.com/dabeaz/compilers_2020_05/wiki/WabbitFunc.md

from wabbit.model import *
from wabbit.decompiler import Decompiler
from textwrap import dedent
import unittest

class FuncModels(unittest.TestCase):
    def setUp(self):
        self.decompiler = Decompiler()
        self.maxDiff = None

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
        
        model = [
                FuncDeclStatement('add', [['x', 'int'], ['y', 'int']], 'int', [
                    ReturnStatement(BinOp('+', Location('x'), Location('y'))),
                ]),
                FuncDeclStatement('mul', [['x', 'int'], ['y', 'int']], 'int', [
                    ReturnStatement(BinOp('*', Location('x'), Location('y'))),
                ]),
                FuncDeclStatement('factorial', [['n', 'int']], 'int', [
                    ConditionalStatement(BinOp('==', Location('n'), Int(0)), [
                        ReturnStatement(Int(1)),
                    ], [
                        ReturnStatement(FuncCall('mul', [Location('n'), FuncCall('factorial', [FuncCall('add', [Location('n'), UnOp('-', Int(1))])])]))
                    ]),
                ]),
                FuncDeclStatement('print_factorials', [['last', 'int']], 'int', [
                    AssignStatement(DeclLocation('x', False), Int(0)),
                    ConditionalLoopStatement(BinOp('<', Location('x'), Location('last')), [
                        PrintStatement(FuncCall('factorial', [Location('x')])),
                        AssignStatement(Location('x'), FuncCall('add', [Location('x'), Int(1)]))
                    ])
                ]),
                FuncDeclStatement('main', [], 'int', [
                    AssignStatement(DeclLocation('result', False), FuncCall('print_factorials', [Int(10)])),
                    ReturnStatement(Int(0))
                ]),
        ]
        self.assertEqual(self.decompiler.to_source(model), source)

if __name__ == '__main__':
    unittest.main()
