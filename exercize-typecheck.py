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
harness('0 1', '1+1.;')
harness('0 2', '1+1.;')
harness('0 3', '1.+1.+2;')
# harness('0 4', '1 && 2;') TODO Oh huh expr && expr doesn't parse...
# TODO UnaryOp



# harness('1 0', "print 2 + 3 * -4;")
s = """
    print 2 + 3 * -4;
    print 2.0 - 3.0 / -4.0;
    print -2 + 3;
    print 2 * 3 + -4;
"""
