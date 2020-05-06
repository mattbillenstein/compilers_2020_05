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
from collections import ChainMap

# Top level function that interprets an entire program. It creates the
# initial environment that's used for storing variables.

def interpret_program(model):
    # Make the initial environment (a dict)
    env = ChainMap()     # Use instead of dict
    return interpret(model, env)

@singledispatch
def interpret(node, env):
    raise RuntimeError(f"Can't interpret {node}")

rule = interpret.register     # Decorator shortcut

@rule(Statements)
def interpret_statements(node, env):
    result = None
    for stmt in node.statements:
        result = interpret(stmt, env)
    return result

@rule(Integer)
def interpret_integer(node, env):
    # Do the operation
    return node.value

@rule(Float)
def interpret_float(node, env):
    return node.value

@rule(Bool)
def interpret_bool(node, env):
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
        # Caution: Behavior of division on integers vs floats. (What does Wabbit spec say?)
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
    elif node.op == '&&':
        return leftval and rightval     # Leave for now. Short-circuit evaluation (later)
    elif node.op == '||':
        return leftval or rightval
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

@rule(Grouping)
def interpret_group(node, env):
    return interpret(node.expression, env)

@rule(Compound)
def interpret_compound(node, env):
    return interpret(node.statements, env.new_child())

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
    # var x int;
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

    # This gets tricky with nested environments/scopes.

    # In what environment does this change the value?   It has to change the
    # same environment where the variable was defined originally.

    # env[node.location.name] = exprval

    # Search all of the scopes for the location of the variable
    for e in env.maps:
        if node.location.name in e:
            e[node.location.name] = exprval    # <<<< Bothered. Violation of encapsulation. (node.location.name)
            return

    # Make it here... undefined variable name.  In reality, we're going to catch
    # this somewhere else (in the type checker), but raising an exception is fine.
    raise RuntimeError("Undefined variable name")
    '''
    var x int = 0;  # env = [ {'x': 0 } ]
    if x == 0 {
                    # env = [ { }, {'x': 0} ]
        x = 10;     # NOT: [ {'x': 10}, {'x': 0} ]
                    # YES: [ {}, {'x': 10} ]    # Change original x.
    }
    '''

@rule(IfStatement)
def interprete_if_statement(node, env):
    # if test { consequence }
    testval = interpret(node.test, env)     # Figure out the test
    # If you return a value, is that a semantic feature of Wabbit? Could it be? Yes.
    if testval:
        return interpret(node.consequence, env.new_child())   # Create a nested environment (new_child)
    else:
        return interpret(node.alternative, env.new_child())

@rule(WhileStatement)
def interpret_while_statement(node, env):
    while True:
        testval = interpret(node.test, env)
        if not testval:
            break
        interpret(node.body, env.new_child())

@rule(ExpressionStatement)
def interpret_expr_statement(node, env):
    return interpret(node.expression, env)
