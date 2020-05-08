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
    check(model, env, None)
    if ERRORS:
        raise TypeError("\n\n".join(ERRORS))
    return True

ERRORS = []

def record_error(message, statement_info):
    ERRORS.append(statement_info + message +"\n" + "="*60 + "\n")

def clear_errors():
    '''Used by testing framework when calling multiple times
       to insure we only capture the correct error(s).
    '''
    ERRORS.clear()

@singledispatch
def check(node, env, statement_info):
    # this should not happen
    raise RuntimeError(f"Can't check {node} on line {node.lineno}.")

add = check.register

# Order alphabetically so that they are easier to find

@add(Assignment)
def check_Assignment(node, env, statement_info):
    expression_type = check(node.expression, env, statement_info)
    var = check(node.location, env, statement_info)

    if isinstance(var, Const):
        record_error(f"Cannot change value of constant {node.location.name}.",
                     statement_info)

    if var.type != expression_type:
        record_error(f"Incompatible types: {var.type} != {expression_type}",
                     statement_info)

valid_binop = {
    # Integer operations
    ('+', 'int', 'int') : 'int',
    ('-', 'int', 'int') : 'int',
    ('*', 'int', 'int') : 'int',
    ('/', 'int', 'int') : 'int',
    ('<', 'int', 'int') : 'bool',
    ('<=', 'int', 'int') : 'bool',
    ('>', 'int', 'int') : 'bool',
    ('>=', 'int', 'int') : 'bool',
    ('==', 'int', 'int') : 'bool',
    ('!=', 'int', 'int') : 'bool',

    # Float operations
    ('+', 'float', 'float') : 'float',
    ('-', 'float', 'float') : 'float',
    ('*', 'float', 'float') : 'float',
    ('/', 'float', 'float') : 'float',
    ('<', 'float', 'float') : 'bool',
    ('<=', 'float', 'float') : 'bool',
    ('>', 'float', 'float') : 'bool',
    ('>=', 'float', 'float') : 'bool',
    ('==', 'float', 'float') : 'bool',
    ('!=', 'float', 'float') : 'bool',

    # Char operations
    ('==', 'char', 'char') : 'bool',
    ('!=', 'char', 'char') : 'bool',

    # Bool operations
    ('==', 'bool', 'bool') : 'bool',
    ('!=', 'bool', 'bool') : 'bool',
    ('&&', 'bool', 'bool') : 'bool',
    ('||', 'bool', 'bool') : 'bool',
}

@add(BinOp)
def check_BinOp(node, env, statement_info):
    try:
        return valid_binop[(node.op,
                            check(node.left, env, statement_info),
                            check(node.right, env, statement_info))]
    except KeyError:
        record_error("Incompatible types for operation:\n" +
            f"     {to_source(node.left)} {node.op} {to_source(node.right)}",
            statement_info)

@add(Bool)
def check_Bool(node, env, statement_info):
    if node == 'bool' or node.value in ['true', 'false']:
        return 'bool'
    else:
        record_error(f"Expected 'true' or 'false'; got {node.value}",
                     statement_info)

@add(Char)
def check_Char(node, env, statement_info):
    if isinstance(node.value, str) and len(node.value) == 1:
        return 'char'
    else:
        record_error(f"Expected a 'char'; got {node.value}", statement_info)


@add(Const)
def check_Const(node, env, statement_info):

    value_type = check(node.value, env, statement_info)
    if node.type and node.type != value_type:
        record_error(f"Wrong type declaration: {node.type} != {value_type}.",
         statement_info)

    node.is_constant = True
    env[node.name] = node
    return node


@add(Compound)
def check_Compound(node, env, statement_info):
    new_env = env.new_child()
    for s in node.statements:
        result = check(s, new_env, statement_info)
    return result

@add(ExpressionStatement)
def check_ExpressionStatement(node, env, statement_info):
    return check(node.expression, env, statement_info)

@add(Float)
def check_Float(node, env, statement_info):
    if not isinstance(node.value, float):
        record_error(f"Argument of Float is not a float: {node.value}",
                     statement_info)
        return
    return 'float'

@add(If)
def check_If(node, env, statement_info):
    condition = check(node.condition, env, statement_info)

    if condition != 'bool':
        record_error(f"Expected a boolean for if condition; got {condition}",
                     statement_info)
    check(node.result, env.new_child(), statement_info)

    if node.alternative is not None:
        check(node.alternative, env.new_child(), statement_info)

@add(Integer)
def check_Integer(node, env, statement_info):
    if not isinstance(node.value, int):
        record_error(f"Argument of Integer is not an int: {node.value}",
                     statement_info)
        return
    return "int"

@add(Group)
def check_Group(node, env, statement_info):
    return check(node.expression, env, statement_info)

@add(Name)
def check_Name(node, env, statement_info):
    return env[node.name]

@add(Print)
def check_Print(node, env, statement_info):
    expr = check(node.expression, env, statement_info)


@add(Statements)
def check_Statements(node, env, statement_info):
    for s in node.statements:
        statement = to_source(s)
        statement_info = (f"TypeError found for statement on line {s.lineno}:\n" +
                          "-"*20 + f"\n\n{statement}\n\n" + "-"*20 +"\n")
        check(s, env, statement_info)


@add(Type)
def check_Type(node, env, statement_info):
    return node.type

@add(UnaryOp)
def check_UnaryOp(node, env, statement_info):
    value = check(node.value, env, statement_info)
    if node.op in ['+', '-'] and value in ['float', 'int']:
        return value

    if node.op == "!" and value in ['bool']:
        return value
    record_error(
        f"Incompatible type for unary operation: {node.op} {to_source(node.value)}",
        statement_info)

@add(Var)
def check_Var(node, env, statement_info):
    # Assign default values of 0 if none are given
    # This is not defined in the specs.
    if node.value:
        value_type = check(node.value, env, statement_info)
        if node.type and node.type != value_type:
            record_error(f"Wrong type declaration: {node.type} != {value_type}.",
                         statement_info)

        if not node.type:  # deduce the type
            node.type = value_type

    # A variable must have a type assigned
    if not node.type:
        record_error(f"Cannot determine type of {node.name}", statement_info)

    env[node.name] = node    # Put the VarDefinition node in environment


@add(While)
def check_While(node, env, statement_info):
    condition = check(node.condition, env, statement_info)
    if condition != 'bool':
        record_error(f"Expected a boolean for while condition; got {condition}",
                     statement_info)
    check(node.statements, env.new_child(), statement_info)


# Sample main program
def main(filename):
    from .parse import parse_file

    model = parse_file(filename)
    check_program(model)


if __name__ == "__main__":
    import sys

    main(sys.argv[1])
