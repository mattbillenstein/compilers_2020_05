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

# Top level function that interprets an entire program. It creates the
# initial environment that's used for storing variables.

def interpret_program(model):
    # Make the initial environment (a dict)
    env = { }
    return interpret(model, env)

@singledispatch
def interpret(node, env):
    raise RuntimeError(f"Can't interpret {node}")

rule = interpret.register     # Decorator shortcut

@rule(Statements)
def interpret_statements(node, env):
    for stmt in node.statements:
        interpret(stmt, env)

@rule(Integer)
def interpret_integer(node, env):
    # Do the operation
    return node.value

@rule(Float)
def interpret_float(node, env):
    return node.value

@rule(BinOp)
def interpet_binop(node, env):
    leftval = interpret(node.left, env)     # Do the left
    rightval = interpret(node.right, env)   # Do the right
    # Do the operation
    if node.op == '+':
        return leftval + rightval
    elif node.op == '-':
        return leftval - rightval
    elif node.op == '*':
        return leftval * rightval
    elif node.op == '/':
        # Caution: Behavior of division on integers vs floats. (What is Wabbit spec)
        return leftval / rightval
    elif node.op == '<':
        return leftval < rightval
    elif node.op == '<=':
        return leftval <= rightval
    elif node.op == '>':
        return leftval > rightval
    elif node.op == '>=':
        return leftval >= rightval
    elif node.op == '==':
        return leftval == rightval
    elif node.op == '!=':
        return leftval != rightval
    else:
        raise RuntimeError(f'Unsupported operator {node.op}')

@rule(UnaryOp)
def interpret_unary_op(node, env):
    opval = interpret(node.operand, env)
    if node.op == '+':
        return opval
    elif node.op == '-':
        return -opval
    else:
        raise RuntimeError(f'Unsupported operator {node.op}')

@rule(LoadLocation)
def interpret_load_location(node, env):
    # Feels wrong. Having to look inside location to get a name.
    # Think about.
    return env[node.location.name]

@rule(PrintStatement)
def interpret_print_statement(node, env):
    value = interpret(node.expression, env)
    print(value)

@rule(ConstDefinition)
def interpret_const_definition(node, env):
    value = interpret(node.value, env)
    env[node.name] = value

@rule(VarDefinition)
def interpret_var_definition(node, env):
    if node.value:
        value = interpret(node.value, env)
    else:
        # What if there's no value????
        # Is there a default value?  If so, what is it?
        value = 0   # ???
    env[node.name] = value

@rule(AssignmentStatement)
def interpret_assignment(node, env):
    '''
    location = expression;
    '''
    exprval = interpret(node.expression, env)     # Right side
    # This feels wrong.  Having to go down two levels into a "location"
    # to get the name.  Think about.
    env[node.location.name] = exprval

@rule(IfStatement)
def interprete_if_statement(node, env):
    # if test { consequence }
    testval = interpret(node.test, env)     # Figure out the test
    if testval:
        interpret(node.consequence, env)
    else:
        interpret(node.alternative, env)



                             

        
        
        
