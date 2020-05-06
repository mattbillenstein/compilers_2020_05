# typecheck.py
#
# Type Checking
# =============
# This file implements type checking. Wabbit uses what's known as
# "nomimal typing."  That means that types are given unique
# names such as "int", "float", "bool", etc. Two types are the same
# if they have exactly the same name.  That's it.
#
# In implementing the type checker, the best strategy might be to
# not overthink the problem at hand. Basically, you have type names.
# You can represent these names using Python strings and compare them
# using string comparison. This gives you most of what you need.
#
# In some cases, you might need to check combinations of types against a
# large number of cases (such as when implementing the math operators).
# For that, it helps to make lookup tables.  For example, you can use
# Python dictionaries to build lookup tables that encode valid
# combinations of binary operators.  For example:
#
# _binops = {
#     # ('lefttype', 'op', 'righttype') : 'resulttype'
#     ('int', '+', 'int') : 'int',
#     ('int', '-', 'int') : 'int',
#     ...
# }
#
# The directory tests/Errors has Wabbit programs with various errors.

from functools import singledispatch
from .model import *

class FranError(Exception):
    ...

# Internal function used to check nodes with an environment
@singledispatch
def check(node, env):
    raise RuntimeError(f"Can't interpret {node}")

@check.register(Statements)
def _(node, env):
    [check(n, env) for n in node.children]

@check.register(BinOp)
def _(node, env):
    left = check(node.left, env)
    right = check(node.right, env)
    if left != right:
        raise FranError(f'Type inconsistency: {left} and {right} for {node.op}')
    return left # TODO assumes BinOp returns the left type but sometimes (eg compare) it changes

@check.register(Integer)
def _(node, env):
    return 'Integer'

@check.register(Float)
def _(node, env):
    return 'Float'

@check.register(PrintStatement)
def _(node, env):
    return

















# Top-level function used to check programs
def check_program(model):
    env = { }
    check(model, env)
    # Maybe return True/False if there are errors


# Sample main program
def main(filename):
    from .parse import parse_file
    model = parse_file(filename)
    check_program(model)

if __name__ == '__main__':
    import sys
    main(sys.argv[1])







