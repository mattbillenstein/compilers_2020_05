# interp.py
# flake8: noqa
#
# In order to write a compiler for a programming language, it helps to
# have some kind of specification of how programs written in the
# programming language are actually supposed to work. A language is
# more than just "syntax" or a data model.  There has to be some kind
# of operational semantics that describe what happens when a program
# runs.
#
# One way to specify the operational semantics is to write a so-called
# "definitional interpreter" that directly executes the data
# model. This might seem like cheating--after all, our final goal is
# not to write an interpreter, but a compiler. However, if you can't
# write an interpreter, chances are you can't write a compiler either.
# So, the purpose of doing this is to pin down fine details as well as
# our overall understanding of what needs to happen when programs run.
#
# We'll write our interpreter in Python.  The idea is relatively
# straightforward.  For each class in the model.py file, you're
# going to write a function similar to this:
#
#    def interpret_node_name(node, env):
#        # Execute "node" in the environment "env"
#        ...
#        return result
#
# The input to the function will be an object from model.py (node, env)
# along with an object respresenting the execution environment (env).
# The function will then execute the node in the environment and return
# a result.  It might also modify the environment (for example,
# when executing assignment statements, variable definitions, etc.).
#
# For the purposes of this projrect, assume that all programs provided
# as input are "sound"--meaning that there are no programming errors
# in the input.  Our purpose is not to create a "production grade"
# interpreter.  We're just trying to understand how things actually
# work when a program runs.
#
# For testing, try running your interpreter on the models you
# created in the example_models.py file.
#

from collections import ChainMap
from functools import singledispatch
from .model import *

# Top level function that interprets an entire program. It creates the
# initial environment that's used for storing variables.

# TODO: use chainmap

def interpret_program(model):
    # Make the initial environment (a dict)
    from wabbit.parse import parse_source
    env = ChainMap()
    interpret(model, env)

@singledispatch
def interpret(node, env):
    raise RuntimeError(f"Can't interpret {node}")

add = interpret.register

# Order alphabetically so that they are easier to find

@add(Assignment)
def interpret_Assignment(node, env):
    value = interpret(node.expression, env)
    name = node.location.name
    # find the nearest environment in which this variable is known.
    for e in env.maps:
        if name in e:
            e[name] = value
            return

@add(BinOp)
def interpret_BinOp(node, env):
    left = interpret(node.left, env)
    right = interpret(node.right, env)
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

@add(Bool)
def interpret_Bool(node, env):
    return node.value

@add(Char)
def interpret_Char(node, env):
    return node.value

@add(Const)
def interpret_Const(node, env):
    name = node.name
    value = interpret(node.value, env)
    env[name] = value

@add(Compound)
def interpret_Compound(node, env):
    new_env = env.new_child()
    for s in node.statements:
        result = interpret(s, new_env)
    return result

@add(ExpressionStatement)
def interpret_ExpressionStatement(node, env):
    return interpret(node.expression, env)

@add(Float)
def interpret_Float(node, env):
    return node.value

@add(If)
def interpret_If(node, env):
    condition = interpret(node.condition, env)
    if condition in [True, 'true']:
        interpret(node.result, env.new_child())
    elif node.alternative is not None:
        interpret(node.alternative, env.new_child())

@add(Integer)
def interpret_Integer(node, env):
    return node.value

@add(Group)
def interpret_Group(node, env):
    return interpret(node.expression, env)

@add(Name)
def interpret_Name(node, env):
    return env[node.name]

@add(Print)
def interpret_Print(node, env):
    value = interpret(node.expression, env)
    if 'capture_print' in env:
        env['capture_print'].append(value)
    if isinstance(value, str):
        if value == "\\n":
            print()
        else:
            print(value, end='')
    else:
        print(value)


@add(Statements)
def interpret_Statements(node, env):
    for s in node.statements:
        interpret(s, env)

@add(Type)
def interpret_Type(node, env):
    return node.type

@add(UnaryOp)
def interpret_UnaryOp(node, env):
    value = interpret(node.value, env)
    if node.op == "-":
        return -value
    else:
        return value

@add(Var)
def interpret_Var(node, env):
    # Assign default values of 0 if none are given
    # This is not defined in the specs.
    type = node.type
    if node.value:
        value = interpret(node.value, env)
    elif type == 'float':
        value = 0.0
    else:
        value = 0
    env[node.name] = value


@add(While)
def interpret_While(node, env):
    while True:
        condition = interpret(node.condition, env)
        if condition in [True, 'true']:
            interpret(node.statements, env.new_child())
        else:
            break
