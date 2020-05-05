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

from .model import *
from functools import singledispatch

# Top level function that interprets an entire program. It creates the
# initial environment that's used for storing variables.

def interpret_program(model):
    # Make the initial environment (a dict)
    env = { }
    interpret(model, env)


@singledispatch
def interpret(node, env):
    raise RuntimeError(f"Can't interpret {node}")

@interpret.register(Integer)
def _(node, env):
    return node.value

@interpret.register(BinOp)
def _(node, env):
    left = interpret(node.left, env)
    right = interpret(node.right, env)
    assert(type(left) == type(right))
    if node.op == '+':
        return left + right
    elif node.op == '*':
        return left * right
    elif node.op == '/':
        return left / right
    elif node.op == '-':
        return left - right
    elif node.op == '<':
        return left < right
    else:
        raise RuntimeError(f'unsupported op: {node.op}')

@interpret.register(Statements)
def _(node, env):
    [interpret(n, env) for n in node.children]

@interpret.register(PrintStatement)
def _(node, env):
    print(interpret(node.child, env))

@interpret.register(Float)
def _(node, env):
    return node.value

@interpret.register(Const)
def _(node, env):
    env[node.name] = interpret(node.value, env)

@interpret.register(Var)
def _(node, env):
    # only declaring, it's a scope thing
    # TODO make work with scope (ChainMap)
    # TODO abandoning type
    env[node.name] = None # TODO should be None? or other special value?

@interpret.register(Assign)
def _(node, env):
    #lhs must BE a Variable (or actually apparently also a var) (TODO: it could also be a location)
    name = node.name
    assert(isinstance(name, Variable) or isinstance(name, Var))
    # rhs must be an expression ie should interpret to a literal, or Variable
    value = interpret(node.value, env)
    if isinstance(value, Variable):
        # look up the value in the env
        value = interpret(value.value)
    env[name.name] = value

@interpret.register(Variable)
def _(node, env):
    return env[node.name]

@interpret.register(IfElse)
def _(node, env):
    return env[node.name]

    # elif isinstance(node, If):
        # return f'''if {to_source(node.condition)} {{
# {to_source_nested_body(node.consequence)}
# }}'''
    # elif isinstance(node, IfElse):
        # return f'''if {to_source(node.condition)} {{
# {to_source_nested_body(node.consequence)}
# }} else {{
# {to_source_nested_body(node.otherwise)}
# }}'''
    # elif isinstance(node, While):
        # return f'''while {to_source(node.condition)} {{
# {to_source_nested_body(node.body)}
# }}'''
    # elif isinstance(node, CompoundExpression):
        # return f'{{ {"; ".join([to_source(each) for each in node.statements.statements])}; }}'
    # elif isinstance(node, Function):
        # return f'''func {node.name}({to_source(node.arguments)}) {node.returnType} {{
# {to_source_nested_body(node.body)}
# }}'''
    # elif isinstance(node, Arguments):
        # return ', '.join([to_source(each) for each in node.arguments])
    # elif isinstance(node, Argument):
        # return f'{node.name} {node.myType}'
    # elif isinstance(node, Return):
        # return f'return {to_source(node.node)}'
    # elif isinstance(node, FunctionInvocation):
        # return f'{node.name}({to_source(node.arguments)})'
    # elif isinstance(node, InvokingArguments):
        # return ', '.join([to_source(a) for a in node.arguments])
    # elif isinstance(node, InvokingArgument):
        # return to_source(node.node)
    # raise RuntimeError(f"Can't interpret {node}")







