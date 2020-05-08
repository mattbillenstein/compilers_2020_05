# wabbit/llvm.py
# flake8: noqa
#
# In this file you will have your compiler generate LLVM output.  Don't
# start this unless you have first worked through the LLVM Tutorial:
#
#     https://github.com/dabeaz/compilers_2020_05/wiki/LLVM-Tutorial
#
# Once you have done that, come back here.
#
# The overall strategy here is going to be very similar to how type
# checking works. Recall, in type checking, there was an environment
# and functions like this:
#
#    def generate_expression(node, env):
#        ...
#
# It's going to be almost exactly the same idea here. Instead of an
# environment, define a class that represents an LLVM Module:
#
#    class LLVMModule:
#        ...
#
# This module will contain everything that's needed to output LLVM
# code. Build it from what you learned in the LLVM tutorial (i.e.,
# you'll have a function, an IRBuilder, a basic block, etc.).
#
# Write functions that accept the LLVM module as an argument.  For
# example:
#
#    def generate_expression(node, mod):
#       ...
#
# In these functions, you will produce code by interacting with the
# module in some way.
#
# One somewhat messy bit concerns the mapping of Wabbit types to
# LLVM types. You'll probably want to make some type objects to help.
# (see below)

from collections import ChainMap
from llvmlite import ir
from .model import *

# Define LLVM types corresponding to Wabbit types
int_type = ir.IntType(32)
float_type = ir.DoubleType()
bool_type = ir.IntType(1)
char_type = ir.IntType(8)

map_types = {
    'int': int_type,
    'float': float_type,
    'bool': bool_type,
    'char': char_type
}

# The LLVM world that Wabbit is populating
class WabbitLLVMModule:
    def __init__(self):
        self.mod = ir.Module('hello')
        # Environment for tracking symbols
        self.env = ChainMap()

        void_type = ir.VoidType()

        self.env["_print_int"] = ir.Function(self.mod,
                             ir.FunctionType(void_type, [int_type]),
                             name='_print_int')

        hello_func = ir.Function(self.mod,
                    ir.FunctionType(int_type, []), name='hello')
        block = hello_func.append_basic_block('entry')
        self.builder = ir.IRBuilder(block)


    # Functions for creating, popping environments
    def new_env(self):
        self.env = self.env.new_child()
        return self

    def pop_env(self):
        self.env = self.env.parents

# Top-level function
def generate_program(model):
    mod = WabbitLLVMModule()
    generate(model, mod)
    mod.builder.ret(ir.Constant(ir.IntType(32), 0))
    return mod

# Internal function to to generate code for each node type
@singledispatch
def generate(node, mod):
    raise RuntimeError(f"Can't generate code for {node}")


###################################
#
#
#  The code below has initially be copied from the
#  Typechecker, which itself has been copied from the
#  interpreter.  Not everything below makes sense in
# the context of this program.
#
#  THIS IS VERY MUCH WORK IN PROGRESS
#
###############################################

add = generate.register
# Order alphabetically so that they are easier to find

@add(Assignment)
def generate_Assignment(node, mod):
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
def generate_BinOp(node, mod):
    try:
        return valid_binop[(node.op,
                            check(node.left, env, statement_info),
                            check(node.right, env, statement_info))]
    except KeyError:
        record_error("Incompatible types for operation:\n" +
            f"     {to_source(node.left)} {node.op} {to_source(node.right)}",
            statement_info)

@add(Bool)
def generate_Bool(node, mod):
    if node == 'bool' or node.value in ['true', 'false']:
        return 'bool'
    else:
        record_error(f"Expected 'true' or 'false'; got {node.value}",
                     statement_info)

@add(Char)
def generate_Char(node, mod):
    if isinstance(node.value, str) and len(node.value) == 1:
        return 'char'
    else:
        record_error(f"Expected a 'char'; got {node.value}", statement_info)


@add(Const)
def generate_Const(node, mod):

    value_type = check(node.value, env, statement_info)
    if node.type and node.type != value_type:
        record_error(f"Wrong type declaration: {node.type} != {value_type}.",
         statement_info)

    node.is_constant = True
    env[node.name] = node
    return node


@add(Compound)
def generate_Compound(node, mod):
    new_env = env.new_child()
    for s in node.statements:
        result = check(s, new_env, statement_info)
    return result

@add(ExpressionStatement)
def generate_ExpressionStatement(node, mod):
    return check(node.expression, env, statement_info)

@add(Float)
def generate_Float(node, mod):
    if not isinstance(node.value, float):
        record_error(f"Argument of Float is not a float: {node.value}",
                     statement_info)
        return
    return 'float'

@add(If)
def generate_If(node, mod):
    condition = check(node.condition, env, statement_info)

    if condition != 'bool':
        record_error(f"Expected a boolean for if condition; got {condition}",
                     statement_info)
    check(node.result, env.new_child(), statement_info)

    if node.alternative is not None:
        check(node.alternative, env.new_child(), statement_info)

@add(Integer)
def generate_Integer(node, mod):
    if not isinstance(node.value, int):
        record_error(f"Argument of Integer is not an int: {node.value}",
                     statement_info)
        return
    return "int"

@add(Group)
def generate_Group(node, mod):
    return check(node.expression, env, statement_info)

@add(Name)
def generate_Name(node, mod):
    return env[node.name]

@add(Print)
def generate_Print(node, mod):
    value = node.expression
    if isinstance(value, Name):
        name = value.name
        var = mod.env[name]
        mod.builder.call(mod.env["_print_int"], [mod.builder.load(var)])

@add(Statements)
def generate_Statements(node, mod):
    for s in node.statements:
        generate(s, mod)


@add(Type)
def generate_Type(node, mod):
    return node.type

@add(UnaryOp)
def generate_UnaryOp(node, mod):
    value = check(node.value, env, statement_info)
    if node.op in ['+', '-'] and value in ['float', 'int']:
        return value

    if node.op == "!" and value in ['bool']:
        return value
    record_error(
        f"Incompatible type for unary operation: {node.op} {to_source(node.value)}",
        statement_info)



@add(Var)
def generate_Var(node, mod):
    name = node.name
    type = map_types[node.type]
    value = node.value.value

    print("name=", name, "type=", type, "value=", value)


    var = mod.env[name] = mod.builder.alloca(type, name=name)

    # assume only literal assignments.
    if not value:
        if type == 'float':  # undefined behaviour for wabbit
            value = 0.0
        else:
            value = 0
    mod.builder.store(ir.Constant(type, value), var)


@add(While)
def generate_While(node, mod):
    condition = check(node.condition, env, statement_info)
    if condition != 'bool':
        record_error(f"Expected a boolean for while condition; got {condition}",
                     statement_info)
    check(node.statements, env.new_child(), statement_info)






# Sample main program that runs the compiler
def main(filename):
    from .parse import parse_file
    from .typecheck import check_program

    model = parse_file(filename)
    check_program(model)
    print("program checked")

    mod = generate_program(model)
    with open('hello.ll', 'w') as file:
        file.write(str(mod.mod))
    print('Wrote hello.ll')

if __name__ == '__main__':
    import sys
    main(sys.argv[1])

