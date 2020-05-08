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

from .model import *
from functools import singledispatch
from collections import ChainMap

_unary_ops = {
    ("+", "int"): "int",
    ("-", "int"): "int",
    ("+", "float"): "float",
    ("-", "float"): "float",
    ("!", "bool"): "bool",
}
_bin_ops = {
    # Integer operations
    ("+", "int", "int"): "int",
    ("-", "int", "int"): "int",
    ("*", "int", "int"): "int",
    ("/", "int", "int"): "int",
    ("<", "int", "int"): "bool",
    ("<=", "int", "int"): "bool",
    (">", "int", "int"): "bool",
    (">=", "int", "int"): "bool",
    ("==", "int", "int"): "bool",
    ("!=", "int", "int"): "bool",
    # Float operations
    ("+", "float", "float"): "float",
    ("-", "float", "float"): "float",
    ("*", "float", "float"): "float",
    ("/", "float", "float"): "float",
    ("<", "float", "float"): "bool",
    ("<=", "float", "float"): "bool",
    (">", "float", "float"): "bool",
    (">=", "float", "float"): "bool",
    ("==", "float", "float"): "bool",
    ("!=", "float", "float"): "bool",
    # Char operations
    ("<", "char", "char"): "bool",
    ("<=", "char", "char"): "bool",
    (">", "char", "char"): "bool",
    (">=", "char", "char"): "bool",
    ("==", "char", "char"): "bool",
    ("!=", "char", "char"): "bool",
    # Bool operations
    ("==", "bool", "bool"): "bool",
    ("!=", "bool", "bool"): "bool",
    ("&&", "bool", "bool"): "bool",
    ("||", "bool", "bool"): "bool",
}

# Top-level function used to check programs
def check_program(model):
    env = ChainMap()
    check(model, env)
    # Maybe return True/False if there are errors
    return env


# Internal function used to check nodes with an environment
@singledispatch
def check(node, env):
    raise RuntimeError(f"Don't know how to typecheck {node}")


rule = check.register


@rule(Statements)
def check_Statements(node, env):
    for statement in node.statements:
        check(statement, env)


@rule(Float)
def check_Float(node, env):
    node.type = "float"
    return "float"


@rule(Return)
def check_Return(node, env):
    value_type = check(node.value, env)

    node.type = value_type
    return value_type


@rule(Integer)
def check_Integer(node, env):
    node.type = "int"
    return "int"


@rule(BinOp)
def check_BinOp(node, env):
    left_type = check(node.left, env)
    right_type = check(node.right, env)

    result_type = _bin_ops.get((node.op, left_type, right_type))
    if not result_type:
        raise SyntaxError(
            f"Unknown operator {node.op} for {left_type} and {right_type}"
        )

    node.type = result_type
    return result_type


@rule(Var)
def check_Var(node, env):
    if node.type is None and node.value is None:
        raise SyntaxError(
            f"Var declaration for {node.name} is missing one of (type, value))"
        )

    if node.value is None:
        env[node.name] = node.type
        return node.type

    value_type = check(node.value, env)

    if node.type and node.type != value_type:
        raise SyntaxError(
            f"Var declaration type mismatch. Type {node.type} does not match type {value_type}"
        )

    env[node.name] = value_type
    node.type = value_type
    return value_type


@rule(Return)
def check_Return(node, env):
    check(node.value, env)

    node.type = "empty"
    return "empty"


@rule(FunctionCall)
def check_FunctionCall(node, env):
    func_return_type = env[node.name]
    node.type = func_return_type

    return func_return_type


@rule(FunctionDefinition)
def check_FunctionDefinition(node, env):
    check(node.args, env)
    check(node.body, env)

    env[node.name] = node.return_type

    node.type = node.return_type
    return node.return_type


@rule(Arguments)
def check_Arguments(node, env):
    for arg in node.args:
        check(arg, env)


@rule(If)
def check_If(node, env):
    check(node.test, env)
    check(node.when_true, env.new_child())
    if node.when_false:
        check(node.when_false, env.new_child())


@rule(Argument)
def check_Argument(node, env):
    env[node.name] = node.type
    return node.type


@rule(Variable)
def check_Variable(node, env):
    variable_type = env.get(node.name)

    if not variable_type:
        raise SyntaxError(f"Variable {node.name} not found in scope")

    node.type = variable_type
    return variable_type


# Sample main program
def main(filename):
    from .parse import parse_file

    model = parse_file(filename)
    check_program(model)


if __name__ == "__main__":
    import sys

    main(sys.argv[1])

