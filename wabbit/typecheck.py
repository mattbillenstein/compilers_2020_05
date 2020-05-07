# typecheck.py
# flake8: noqa
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
from collections import ChainMap

from .model import *

def check_program(model):
    # Make the initial environment (a dict)
    env = ChainMap()     # Use instead of dict
    return check(model, env)


@singledispatch
def check(node, env):
    raise RuntimeError(f"Can't check {node}")

add = check.register

# Order alphabetically so that they are easier to find

@add(Assignment)
def check_Assignment(node, env):
    value = check(node.expression, env)
    name = node.location.name
    # find the nearest environment in which this variable is known.
    for e in env.maps:
        if name in e:
            e[name] = value
            return

@add(BinOp)
def check_BinOp(node, env):
    left = check(node.left, env)
    right = check(node.right, env)
    if node.op == "+":
        return left + right
    elif node.op == "-":
        return left - right
    elif node.op == "*":
        return left * right
    elif node.op == "/":
        if isinstance(left, int):
            return left // right
        else:
            return left / right
    elif node.op == ">":
        return left > right
    elif node.op == ">=":
        return left >= right
    elif node.op == "<":
        return left < right
    elif node.op == ">=":
        return left >= right
    elif node.op == "==":
        return left == right
    elif node.op == "!=":
        return left != right
    else:
        raise RuntimeError(f"Unsupported operator {node.op}")

@add(Const)
def check_Const(node, env):
    name = node.name
    value = check(node.expression, env)
    env[name] = value

@add(Compound)
def check_Compound(node, env):
    new_env = env.new_child()
    for s in node.statements:
        result = check(s, new_env)
    return result

@add(ExpressionStatement)
def check_ExpressionStatement(node, env):
    return check(node.expression, env)

@add(Float)
def check_Float(node, env):
    return node.value

@add(If)
def check_If(node, env):
    condition = check(node.condition, env)
    if condition:
        check(node.result, env.new_child())
    elif node.alternative is not None:
        check(node.alternative, env.new_child())

@add(Integer)
def check_Integer(node, env):
    return "int"

@add(Group)
def check_Group(node, env):
    return check(node.expression, env)


@add(Name)
def check_Name(node, env):
    return env[node.name]

@add(Print)
def check_Print(node, env):
    expr = check(node.expression, env)
    if 'capture_print' in env:
        env['capture_print'].append(expr)
    print(expr)


@add(Statements)
def check_Statements(node, env):
    for s in node.statements:
        check(s, env)

@add(Type)
def check_Type(node, env):
    return node.type

@add(UnaryOp)
def check_UnaryOp(node, env):
    value = check(node.value, env)
    if node.op == "-":
        return -value
    else:
        return value

@add(Var)
def check_Var(node, env):
    # Assign default values of 0 if none are given
    # This is not defined in the specs.
    type = check(node.type, env)
    if node.expression:
        value = check(node.expression, env)
    elif type == 'float':
        value = 0.0
    else:
        value = 0
    env[node.name] = value


@add(While)
def check_While(node, env):
    while True:
        condition = check(node.condition, env)
        if condition:
            check(node.statements, env.new_child())
        else:
            break






# Sample main program
def main(filename):
    from .parse import parse_file

    model = parse_file(filename)
    check_program(model)


if __name__ == "__main__":
    import sys

    main(sys.argv[1])
