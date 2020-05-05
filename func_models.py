#!/usr/bin/env python3

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
from wabbit.source_visitor import compare_source

# ----------------------------------------------------------------------
# Program 6: Functions.  The program prints out the first factorials
# with various function definitions.
#

source6 = '''
func add(x int, y int) int {
    return x + y;
}

func mul(x int, y int) int {
    return x * y;
}

func factorial(n int) int {
    if n == 0 {
        return 1;
    } else {
        return mul(n, factorial(add(n, -1)));
    }
}

func print_factorials(last int) {
    var x = 0;
    while x < last {
        print factorial(x);
        x = add(x, 1);
    }
}

func main() int {
    var result = print_factorials(10);
    return 0;
}
'''

model6 = Block([
    Func(Name('add'),
        Block([
            Return(BinOp('+', Name('x'), Name('y'))),
        ], indent=' '*4),
        [Arg(Name('x'), 'int'), Arg(Name('y'), 'int')],
        'int',
    ),
    Func(Name('mul'),
        Block([
            Return(BinOp('*', Name('x'), Name('y'))),
        ], indent=' '*4),
        [Arg(Name('x'), 'int'), Arg(Name('y'), 'int')],
        'int',
    ),
    Func(Name('factorial'),
        Block([
            If(BinOp('==', Name('n'), Integer(0)),
                Block([
                    Return(Integer(1)),
                ], indent=' '*4),
                Block([
                    Return(
                        Call(Name('mul'), [
                            Name('n'),
                            Call(Name('factorial'), [
                                Call(Name('add'), [
                                    Name('n'), Integer(-1),
                                ]),
                            ]),
                        ]),
                    ),
                ], indent=' '*4),
            ),
        ], indent=' '*4),
        [Arg(Name('n'), 'int')],
        'int',
    ),
    Func(Name('print_factorials'),
        Block([
            Var(Name('x'), Integer(0)),
            While(BinOp('<', Name('x'), Name('last')),
                Block([
                    Print(Call(Name('factorial'), [Name('x')])),
                    Assign(Name('x'), Call(Name('add'), [Name('x'), Integer(1)])),
                ], indent=' '*4),
            ),
        ], indent=' '*4),

        [Arg(Name('last'), 'int')],
    ),
    Func(Name('main'),
        Block([
            Var(Name('result'), Call(Name('print_factorials'), [Integer(10)])),
            Return(Integer(0)),
        ], indent=' '*4),
        ret_type='int',
    ),
])

compare_source(model6, source6)

# ----------------------------------------------------------------------
# Bring it!  If you're here wanting even more, proceed to the file 
# "type_models.py".
