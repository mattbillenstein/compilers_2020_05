from wabbit.typecheck import check, FranError
from wabbit.model import *
from wabbit.parse import parse_source

def harness(name, s):
    print(name)
    env = {}
    node = parse_source(s)
    print('source:', s)
    print('model:', node)
    try:
        print('returned:', check(node, env))
    except FranError as e:
        print('TYPE CHECKED!', e)
    print()

harness('0', '1+1;')
harness('0 0.5', '1.+1.;')
harness('0 1', '1+1.;')
harness('0 2', '1+1.;')
harness('0 2.5', '1.+1.+2.;')
harness('0 3', '1.+1.+2;')
harness('0 4', '1 && 2;')
harness('0 5', 'true && false;')
harness('0 5', 'true && false || 3;')
# TODO rest of BinOp
# TODO UnaryOp
# TODO Statements
# TODO PrintStatement
harness('Const 0', 'const woo = 1;')
harness('Const 1', '''
    const woo = 1;
    woo = 2;
        ''')
# TODO rest of Const (what?)
# TODO Var
# TODO Assign
# TODO Variable
# TODO If
# TODO IfElse
# TODO While
# TODO CompoundExpression
# TODO Function
# TODO Arguments
# TODO Argument
# TODO Return
# TODO FunctionInvocation
# TODO InvokingArguments
# TODO InvokingArgument



# harness('1 0', "print 2 + 3 * -4;")
s = """
    print 2 + 3 * -4;
    print 2.0 - 3.0 / -4.0;
    print -2 + 3;
    print 2 * 3 + -4;
"""
