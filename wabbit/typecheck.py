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
from collections import ChainMap

# Dedicated error handler.  Easier to redefine. Expand later.

have_errors = False

def error(lineno, msg):
    global have_errors
    print(f'{lineno}:{msg}')
    have_errors = True

# Code almost identical to interpreter

def check_program(model):
    # Make the initial environment (a dict)
    env = ChainMap()     # Use instead of dict
    return check(model, env)

@singledispatch
def check(node, env):
    raise RuntimeError(f"Can't check {node}")

rule = check.register     # Decorator shortcut

@rule(Statements)
def check_statements(node, env):
    resulttype = None
    for stmt in node.statements:
        resulttype = check(stmt, env)
    return resulttype if resulttype else "unit"

@rule(Integer)
def check_integer(node, env):
    # Return the type that results from doing the operation. 
    return "int"

@rule(Float)
def check_float(node, env):
    return "float"

@rule(Bool)
def check_bool(node, env):
    return "bool"

@rule(Char)
def check_char(node, env):
    return "char"

# Capability/type table
_bin_ops = {
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
    ('<', 'char', 'char') : 'bool',
    ('<=', 'char', 'char') : 'bool',
    ('>', 'char', 'char') : 'bool',
    ('>=', 'char', 'char') : 'bool',
    ('==', 'char', 'char') : 'bool',
    ('!=', 'char', 'char') : 'bool',

    # Bool operations
    ('==', 'bool', 'bool') : 'bool',
    ('!=', 'bool', 'bool') : 'bool',
    ('&&', 'bool', 'bool') : 'bool',
    ('||', 'bool', 'bool') : 'bool',
}

@rule(BinOp)
def check_binop(node, env):
    lefttype = check(node.left, env)     # Type of doing the left
    righttype = check(node.right, env)   # Type of doing the right
    # Can I do the operation?  If so, what's the result type?
    result_type = _bin_ops.get((node.op, lefttype, righttype))      # float + char --> Error. (not in table)
    if result_type is None:
        error(node.lineno, f"Unsupported operation. {lefttype}{node.op}{righttype}")
    # Annotate the node
    node.type = result_type
    return result_type

_unary_ops = {
    ('+', 'int') : 'int',
    ('-', 'int') : 'int',
    ('+', 'float') : 'float',
    ('-', 'float') : 'float',
    ('!', 'bool') : 'bool',
    }

@rule(UnaryOp)
def check_unary_op(node, env):
    optype = check(node.operand, env)
    resulttype = _unary_ops.get((node.op, optype))
    if not resulttype:
        error(node.lineno, f"Unsupported operation. {node.op}{optype}")
    node.type = resulttype
    return resulttype

@rule(Grouping)
def check_group(node, env):
    return check(node.expression, env)

@rule(Compound)
def check_compound(node, env):
    return check(node.statements, env.new_child())

@rule(LoadLocation)
def check_load_location(node, env):
    # Feels wrong. Having to look inside location to get a name.
    loc = check(node.location, env)
    if loc:
        node.type = loc.type
        return loc.type

@rule(PrintStatement)
def check_print_statement(node, env):
    check(node.expression, env)

@rule(ConstDefinition)
def check_const_definition(node, env):
    value_type = check(node.value, env)
    if node.type and node.type != value_type:
        error(node.lineno, f"Type error {node.type} = {value_type}")

    # Fill in the type of the const definition
    if not node.type:
        node.type = value_type

    env[node.name] = node     # Put the ConstDefinition itself node in the environment

@rule(VarDefinition)
def check_var_definition(node, env):
    if node.value:
        value_type = check(node.value, env)
        if node.type and node.type != value_type:
            error(node.lineno, f"Type error {node.type} = {value_type}")

        if not node.type:
            node.type = value_type

    # A variable must have a type assigned
    if not node.type:
        error(node.lineno, f"Can't determine type of {node.name}")

    env[node.name] = node    # Put the VarDefinition node in environment

@rule(AssignmentStatement)
def check_assignment(node, env):
    '''
    location = expression;
    '''
    expr_type = check(node.expression, env)     # Right side
    defn = check(node.location, env)

    if isinstance(defn, ConstDefinition):
        error(node.lineno, "Can't assign to const")
    
    if expr_type != defn.type:
        error(node.lineno, "Type error. {defn.type} = {expr_type}")

@rule(IfStatement)
def check_if_statement(node, env):
    # if test { consequence }
    testtype = check(node.test, env)     # Figure out the type of the test expression
    if testtype != 'bool':
        error(node.lineno, "Expected a bool for test")
    check(node.consequence, env.new_child())   # Create a nested environment (new_child)
    check(node.alternative, env.new_child())

@rule(WhileStatement)
def check_while_statement(node, env):
    testtype = check(node.test, env)
    if testtype != 'bool':
        error(node.lineno, "Expected a bool for test")
    check(node.body, env.new_child())

@rule(ExpressionStatement)
def check_expr_statement(node, env):
    return check(node.expression, env)

@rule(NamedLocation)
def check_location(node, env):
    defn = env.get(node.name)
    if not defn:
        error(node.lineno, "{node.name} not defined!")
    return defn

# Sample main program
def main(filename):
    from .parse import parse_file
    model = parse_file(filename)
    check_program(model)

if __name__ == '__main__':
    import sys
    main(sys.argv[1])



        


        
