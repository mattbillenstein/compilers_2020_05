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

func main() int {
    var result = print_factorials(10);
    return 0;
}
'''

model6 = Program(
    FunctionDefinition(name='add',
                       parameters=(
                           Parameter(name='x', type='int'),
                           Parameter(name='y', type='int'),
                       ),
                       rtype='int',
                       body=Clause(
                            ReturnStatement(expression=BinOp.add(left=Identifier('x'), right=Identifier('y')))
                       )
                       ),
    FunctionDefinition(name='mul',
                       parameters=(
                           Parameter(name='x', type='int'),
                           Parameter(name='y', type='int'),
                       ),
                       rtype='int',
                       body=Clause(
                           ReturnStatement(expression=BinOp.mult(left=Identifier('x'), right=Identifier('y')))
                       )
                       ),
    FunctionDefinition(name='factorial',
                       parameters=(
                           Parameter(name='n', type='int'),
                       ),
                       rtype='int',
                       body=Clause(
                           IfStatement(
                               condition=Compare.eq(left=Identifier('n'), right=Integer(0)),
                               consequent=Clause(
                                   ReturnStatement(expression=Integer(1))
                               ),
                               alternative=Clause(
                                   ReturnStatement(expression=FunctionCall(name='mul', arguments=(
                                       Identifier('n'),
                                       FunctionCall(name='factorial', arguments=(
                                           FunctionCall(name='add', arguments=(
                                               Identifier('n'),
                                               Integer(-1)
                                           )),
                                       ))
                                   )))
                               )
                           )
                       )
                       ),
    FunctionDefinition(name='print_factorials',
                       parameters=(
                           Parameter(name='last', type='int'),
                       ),
                       rtype=None,
                       body=Clause(
                           VariableDefinition(name='x', type=None, value=Integer(0)),
                           WhileLoop(condition=Compare.lt(left=Identifier('x'), right=Identifier('last')),
                                     body=Clause(
                                         PrintStatement(expression=FunctionCall(name='factorial',
                                                                                arguments=(
                                                                                    Identifier('x'),
                                                                                ))),
                                         Assignment(location=Identifier('x'), value=FunctionCall(name='add',
                                                                                                 arguments=(
                                                                                                     Identifier('x'),
                                                                                                     Integer(1)
                                                                                                 )))
                                     ))
                       )
                       ),
    FunctionDefinition(name='main',
                       parameters=None,
                       rtype='int',
                       body=Clause(
                           VariableDefinition(name='result', type=None, value=FunctionCall(name='print_factorials',
                                                                                           arguments=(
                                                                                               Integer(10),
                                                                                           ))),
                           ReturnStatement(expression=Integer(0))
                       ))
)

print(repr(model6))
print(to_source(model6))

# ----------------------------------------------------------------------
# Bring it!  If you're here wanting even more, proceed to the file 
# "type_models.py".
