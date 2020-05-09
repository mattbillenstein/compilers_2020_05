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
    ("<", "int", "int"): "ibool",
    ("<=", "int", "int"): "ibool",
    (">", "int", "int"): "ibool",
    (">=", "int", "int"): "ibool",
    ("==", "int", "int"): "ibool",
    ("!=", "int", "int"): "ibool",
    # Float operations
    ("+", "float", "float"): "float",
    ("-", "float", "float"): "float",
    ("*", "float", "float"): "float",
    ("/", "float", "float"): "float",
    ("<", "float", "float"): "fbool",
    ("<=", "float", "float"): "fbool",
    (">", "float", "float"): "fbool",
    (">=", "float", "float"): "fbool",
    ("==", "float", "float"): "fbool",
    ("!=", "float", "float"): "fbool",
    # Char operations
    ("<", "char", "char"): "ibool",
    ("<=", "char", "char"): "ibool",
    (">", "char", "char"): "ibool",
    (">=", "char", "char"): "ibool",
    ("==", "char", "char"): "ibool",
    ("!=", "char", "char"): "ibool",
    # Bool operations
    ("==", "ibool", "ibool"): "ibool",
    ("!=", "ibool", "ibool"): "ibool",
    ("&&", "ibool", "ibool"): "ibool",
    ("||", "ibool", "ibool"): "ibool",
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
    type = None
    for statement in node.statements:
        type = check(statement, env)

    node.type = type
    return type


@rule(Float)
def check_Float(node, env):
    node.type = "float"
    return "float"


@rule(Return)
def check_Return(node, env):
    if node.value is not None:
        value_type = check(node.value, env)
    else:
        value_type = "unit"

    node.type = value_type
    return value_type


@rule(Break)
def check_Break(node, env):
    node.type = "unit"
    return "unit"


@rule(UnaryOp)
def check_UnaryOp(node, env):
    check(node.target, env)

    # + op does nothing
    if node.op == "+":
        node.type = node.target.type
        return node.type

    # perform integer divison on integers so we never get floats
    if node.op in ["-", "*", "/"]:
        node.type = node.target.type
        return node.type

    # creates a bool
    if node.op == "!":
        return "bool"


@rule(Integer)
def check_Integer(node, env):
    node.type = "int"
    return "int"


@rule(BinOp)
def check_BinOp(node, env):
    check(node.left, env)
    check(node.right, env)

    result_type = _bin_ops.get((node.op, node.left.type, node.right.type))
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


@rule(FunctionCall)
def check_FunctionCall(node, env):
    for argument in node.args:
        check(argument, env)
    func_return_type = env[node.name]
    node.type = func_return_type

    return func_return_type


@rule(FunctionDefinition)
def check_FunctionDefinition(node, env):
    if node.args:
        check(node.args, env)

    check(node.body, env)

    env[node.name] = node.return_type

    node.type = node.return_type
    return node.return_type


@rule(Arguments)
def check_Arguments(node, env):
    for arg in node.args:
        check(arg, env)


@rule(While)
def check_While(node, env):
    check(node.test, env)
    check(node.consequence, env)


@rule(Assignment)
def check_Assignment(node, env):
    check(node.location, env)
    check(node.expression, env)
    node.type = node.expression.type


@rule(Truthy)
@rule(Falsey)
def check_Boolean(node, env):
    return node.type


@rule(If)
def check_If(node, env):
    check(node.test, env)
    check(node.consequence, env.new_child())
    if node.alternative:
        check(node.alternative, env.new_child())
    node.type = "int"


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

