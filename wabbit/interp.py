# interp.py
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
# The input to the function will be an object from model.py (node)
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

from functools import singledispatch
from collections import ChainMap
from .model import *
from .errors import InterpreterException

# Top level function that interprets an entire program. It creates the
# initial environment that's used for storing variables.
def get_default_value(type):
    assert isinstance(type, str)
    if type == "int":
        return int(0)
    if type == "float":
        return float(0.0)
    return InterpreterException(f"Default value for type {type} not specified")


def interpret_program(node, env: ChainMap = None) -> ChainMap:
    if env is None:
        env = ChainMap({})
    interpret(node, env)
    # helpful for testing
    return env


# Internal function to interpret a node in the environment
@singledispatch
def interpret(node, env):
    # Expand to check for different node types
    ...
    raise InterpreterException(f"Can't interpret {repr(node)}")


rule = interpret.register


@rule(Integer)
def interpret_Integer(node, env):
    return int(node.value)


@rule(If)
def interpret_If(node, env):
    test = interpret(node.test, env)
    if test:
        interpret(node.when_true, env)
    else:
        interpret(node.when_false, env)


@rule(While)
def interpret_While(node, env):
    test = True
    while test:
        test = interpret(node.test, env)
        interpret(node.when_true, env)


@rule(Variable)
def interpret_Variable(node, env):
    loc_type, loc_value = env[node.name]
    return loc_value


@rule(Block)
def interpret_Block(node, env):
    value = None
    for statement in node.statements:
        value = interpret(statement, env)
    return value


@rule(Assignment)
def interpret_Assignment(node, env):
    rhs = interpret(node.expression, env)
    loc_type, old_value = env[node.location.name]
    if loc_type == "var":
        env[node.location.name] = ("var", rhs)
    else:
        raise InterpreterException("Can't modify const")


@rule(Const)
def interpret_Const(node, env):
    value = interpret(node.value, env)
    env[node.name] = ("const", value)
    return


@rule(Var)
def interpret_Var(node, env):
    if env.get(node.name) is not None:
        raise InterpreterException(f"Attempting to re-declare var {node.name}")
    if node.value is not None:
        value = interpret(node.value, env)
        env[node.name] = ("var", value)
    else:
        env[node.name] = ("var", get_default_value(node.type))
    return


@rule(Float)
def interpret_Float(node, env):
    return float(node.value)


@rule(Statements)
def interpret_Statements(node, env):
    for statement in node.statements:
        interpret(statement, env)
    return


@rule(Print)
def interpret_Print(node, env):
    print(interpret(node.value, env))
    return


@rule(UnaryOp)
def interpret_UnaryOp(node, env):
    value = interpret(node.target, env)
    if node.op == "-":
        return -1 * value
    raise InterpreterException(f"UnaryOp operation {node.op} not recognised")


@rule(BinOp)
def interpret_BinOp(node, env):
    lhs = interpret(node.left, env)
    rhs = interpret(node.right, env)
    assert type(lhs) == type(rhs)
    if node.op == "+":
        return lhs + rhs
    elif node.op == "*":
        return lhs * rhs
    elif node.op == "/":
        return lhs / rhs
    elif node.op == "-":
        return lhs - rhs
    elif node.op == "<":
        return lhs < rhs
    elif node.op == ">":
        return lhs > rhs
    raise InterpreterException(f"BinOp operation {node.op} not recognised")

