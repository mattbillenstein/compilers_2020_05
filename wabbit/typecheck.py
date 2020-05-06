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
    result = None
    for stmt in node.statements:
        result = check(stmt, env)
    return result

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

# Capability/type table
_bin_ops = {
    ('+', 'int', 'int') : 'int',
    ('-', 'int', 'int') : 'int',
}

@rule(BinOp)
def check_binop(node, env):
    lefttype = check(node.left, env)     # Type of doing the left
    righttype = check(node.right, env)   # Type of doing the right
    # Can I do the operation?  If so, what's the result type?
    result_type = _bin_ops.get((node.op, lefttype, righttype))      # float + char --> Error. (not in table)
    if result_type is None:
        print(f"type error. Can't do {lefttype} {node.op} {righttype}")
    return result_type

@rule(UnaryOp)
def check_unary_op(node, env):
    opval = check(node.operand, env)
    if node.op == '+':
        return opval
    elif node.op == '-':
        return -opval
    else:
        raise RuntimeError(f'Unsupported operator {node.op}')

@rule(Grouping)
def check_group(node, env):
    return check(node.expression, env)

@rule(Compound)
def check_compound(node, env):
    return check(node.statements, env.new_child())

@rule(LoadLocation)
def check_load_location(node, env):
    # Feels wrong. Having to look inside location to get a name.
    # Think about.
    return env[node.location.name]

@rule(PrintStatement)
def check_print_statement(node, env):
    value = check(node.expression, env)
    print(value)

@rule(ConstDefinition)
def check_const_definition(node, env):
    # const pi int = 3.14159;      // Allowed in the grammar/parser
    value_type = check(node.value, env)   // --> float
    if node.type and node.type != value_type:
        print(f"Error: {node.name} is not declared as {value_type}")
    env[node.name] = node     # Put the ConstDefinition node in the environment

@rule(VarDefinition)
def check_var_definition(node, env):
    # var x int;
    if node.value:
        value_type = check(node.value, env)
    env[node.name] = node    # Put the VarDefinition node in environment

@rule(AssignmentStatement)
def check_assignment(node, env):
    '''
    location = expression;
    '''
    expr_type = check(node.expression, env)     # Right side
    defn = env.get(node.location.name)    # What is it????
    if defn is None:
        print("Error: undefined location!")

    if isinstance(defn, ConstDefinition):
        print("Error: Can't assign to const")
    
    if expr_type != defn.type:
        print("Error. Incompatible types in assignment")

@rule(IfStatement)
def check_if_statement(node, env):
    # if test { consequence }
    testtype = check(node.test, env)     # Figure out the type of the test expression
    if testtype != 'bool':
        print("Expected a bool for test")
    check(node.consequence, env.new_child())   # Create a nested environment (new_child)
    check(node.alternative, env.new_child())

@rule(WhileStatement)
def check_while_statement(node, env):
    testtype = check(node.test, env)
    if testtype != 'bool':
        print("Error")
    check(nody.body, env.new_child())

@rule(ExpressionStatement)
def check_expr_statement(node, env):
    return check(node.expression, env)

# Sample main program
def main(filename):
    from .parse import parse_file
    model = parse_file(filename)
    check_program(model)

if __name__ == '__main__':
    import sys
    main(sys.argv[1])



        


        
