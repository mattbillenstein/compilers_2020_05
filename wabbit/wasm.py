# wasm.py
# flake8: noqa
#
# Generate WebAssembly from the Wabbit model.  Don't even attempt this
# unless you have first worked through the WebAssembly tutorial.
#
#     https://github.com/dabeaz/compilers_2020_05/wiki/WebAssembly-Tutorial
#
# The overall strategy here is going to be very similar to how type
# checking works.  Recall, in type checking, there was an environment
# and functions like this:
#
#    def check_expression(node, env):
#        ...
#
# It's going to be almost exactly the same idea here. Instead of an
# environment, define a class that represents a Wasm Module:
#
#    class WasmWabbit:
#        ...
#
# This module will contain everything that's needed to output Wasm
# code. Build it from what you learned in the Wasm tutorial (i.e.,
# you'll have a WasmModule, WasmFunction, etc.).
#
# Write functions that accept the WasmWabbit module as an argument.  For
# example:
#
#    def generate_expression(node, mod):
#       ...
#
# In these functions, you will produce code by interacting with the
# Wasm module in various ways.
#

#######################################
#
#    CHEATING
#
#  Not following the instructions, doing something simpler
#
#######################################


simple_wasm_template = """
from wasm_compiler import *

mod = WasmModule("{filename}")

_print = WasmImportedFunction(mod, "runtime", "_print", [i32], [])
main = WasmFunction(mod, "main", [], [])

{code}

with open("{filename}.wasm", "wb") as file:
    file.write(encode_module(mod))
"""

from collections import ChainMap
from .model import *

# # Class representing the world of Wasm
# class WabbitWasmModule:
#     pass

# # Top-level function for generating code from the model
# def generate_program(model):
#     mod = WabbitWasmModule()
#     generate(model, mod)
#     return mod

# # Internal function for generating code on each node
# def generate(node, mod):
#     raise RuntimeError(f"Can't generate {node}")


# Top-level function to handle an entire program.
def generate_program(model, filename):

    print("filename = ", filename)
    env = ChainMap()  # is this needed?
    lines = []
    code = to_pre_wasm(model)
    return simple_wasm_template.format(code=code, filename=filename)


@singledispatch
def to_pre_wasm(node):
    raise RuntimeError("Can't generate source for {node}")

add = to_pre_wasm.register

# Order alphabetically so that they are easier to find

@add(Assignment)
def to_pre_wasm_Assignment(node):
    return f"{to_pre_wasm(node.location)} = {to_pre_wasm(node.expression)};"

ops = {
    "+": "main.iadd()\n",
    "-": "main.isub()\n",
    "*": "main.imul()\n",
    "/": "main.idiv()\n"
}


@add(BinOp)
def to_pre_wasm_BinOp(node):
    left = to_pre_wasm(node.left)
    right = to_pre_wasm(node.right)
    op = ops[node.op]

    return left + right + op


    # return f"{to_pre_wasm(node.left)} {node.op} {to_pre_wasm(node.right)}"


@add(Bool)
def to_pre_wasm_Bool(node):
    return str(node.value)

@add(Char)
def to_pre_wasm_Char(node):
    return node.value

@add(Const)
def to_pre_wasm_Const(node):
    type = f' {node.type}' if node.type else ''
    return f'const {node.name}{type} = {to_pre_wasm(node.value)};'

@add(Compound)
def to_pre_wasm_Compound(node):
    statements = [to_pre_wasm(s) for s in node.statements]
    return "{ " + " ".join(statements) + " }"

@add(Float)
def to_pre_wasm_Float(node):
    return repr(node.value)

@add(ExpressionStatement)
def to_pre_wasm_ExpressionStatement(node):
    return f"{to_pre_wasm(node.expression)};"

@add(Group)
def to_pre_wasm_Group(node):
    return f"({to_pre_wasm(node.expression)})"

@add(If)
def to_pre_wasm_If(node):
    result = f"if {to_pre_wasm(node.condition)} {{\n{to_pre_wasm(node.result)}\n}}"
    if node.alternative is not None:
        result += f" else {{\n {to_pre_wasm(node.alternative)}\n}}"
    return result +"\n"

@add(Integer)
def to_pre_wasm_Integer(node):
    return f"main.iconst({node.value})\n"

@add(Name)
def to_pre_wasm_Name(node):
    return f"{node.name}"

@add(Print)
def to_pre_wasm_Print(node):
    return f"{to_pre_wasm(node.expression)}main.call(_print)\n"

@add(Statements)
def to_pre_wasm_Statements(node):
    statements = [to_pre_wasm(s) for s in node.statements]
    return "\n".join(statements)

@add(UnaryOp)
def to_pre_wasm_UnaryOp(node):
    return f"{node.op}{to_pre_wasm(node.value)}"

@add(Var)
def to_pre_wasm_Var(node):
    type = f' {node.type}' if node.type else ''
    value = f' = {to_pre_wasm(node.value)}' if node.value else ''
    return f'var {node.name}{type}{value};'

@add(While)
def to_pre_wasm_While(node):
    return f"while {to_pre_wasm(node.condition)} {{\n{to_pre_wasm(node.statements)}\n}}"



##########################################################################


def main(filename):
    from .parse import parse_file
    import os

    # from .typecheck import check_program
    model = parse_file(filename)

    fname = os.path.basename(filename)[:-3] # remove extension


    print("fname = ", fname)

    # check_program(model):
    mod = generate_program(model, fname)

    target = filename[:-3] # remove extension, put in same location as source

    with open(f'{target}.py', 'w') as file:
        file.write(mod)

    # with open(f'{filename}.wasm', 'wb') as file:
    #     file.write(encode_module(mod.module))
    # print(f"Wrote{filename}.wasm")

if __name__ == '__main__':
    import sys
    main(sys.argv[1])
