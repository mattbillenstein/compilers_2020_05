# wasm.py
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

from collections import ChainMap
from functools import singledispatch
from wabbit.model import *
from wabbit.wasm_helpers import *
from wabbit.typecheck import check_program


class WasmModule:
    def __init__(self, name):
        self.name = name
        self.imported_functions = []
        self.functions = []
        self.global_variables = []


class WasmImportedFunction:
    """
    A function defined outside of the Wasm environment
    """

    def __init__(self, module, envname, name, argtypes, rettypes):
        self.module = module
        self.envname = envname
        self.name = name
        self.argtypes = argtypes
        self.rettypes = rettypes
        self.idx = len(module.imported_functions)
        module.imported_functions.append(self)


class WasmFunction:
    """
    A natively defined Wasm function
    """

    def __init__(self, module, name, argtypes, rettypes):
        self.module = module
        self.name = name
        self.argtypes = argtypes
        self.rettypes = rettypes
        self.idx = len(module.imported_functions) + len(module.functions)
        module.functions.append(self)

        # Code generation
        self.code = b""

        # Types of local variables
        self.local_types = []

    def iconst(self, value):
        self.code += b"\x41" + encode_signed(value)

    def fconst(self, value):
        self.code += b"\x44" + encode_FLOAT64(value)

    def iadd(self):
        self.code += b"\x6a"

    def fadd(self):
        self.code += b"\xa0"

    def imul(self):
        self.code += b"\x6c"

    def fmul(self):
        self.code += b"\xa2"

    def ret(self):
        self.code += b"\x0f"

    def call(self, func):
        self.code += b"\x10" + encode_unsigned(func.idx)

    def alloca(self, type):
        idx = len(self.argtypes) + len(self.local_types)
        self.local_types.append(type)
        return idx

    def local_get(self, idx):
        self.code += b"\x20" + encode_unsigned(idx)

    def local_set(self, idx):
        self.code += b"\x21" + encode_unsigned(idx)

    def global_get(self, gvar):
        self.code += b"\x23" + encode_unsigned(gvar.idx)

    def global_set(self, gvar):
        self.code += b"\x24" + encode_unsigned(gvar.idx)


class WasmGlobalVariable:
    """
    A natively defined Wasm global variable
    """

    def __init__(self, module, name, type, initializer):
        self.module = module
        self.name = name
        self.type = type
        self.initializer = initializer
        self.idx = len(module.global_variables)
        module.global_variables.append(self)


# Class representing the world of Wasm
class WabbitWasmModule:
    def __init__(self):
        self.module = WasmModule("wabbit")
        # Current function (temporary hack. Set to main)
        self.function = WasmFunction(self.module, "main", [], [INT32])

        # Environment for tracking symbols
        self.env = ChainMap()


# Top-level function for generating code from the model
def generate_program(model):
    module = WabbitWasmModule()

    # Typecheck. Annotates nodes with types.
    check_program(model)

    generate(model, module)
    return module


# Internal function for generating code on each node
@singledispatch
def generate(node, func):
    raise RuntimeError(f"Can't generate {node}")


rule = generate.register

_bin_op_methods = {
    # Integer operations
    ("+", "int", "int"): "iadd",
    ("-", "int", "int"): "int",
    ("*", "int", "int"): "int",
    ("/", "int", "int"): "int",
    ("<", "int", "int"): "bool",
    ("<=", "int", "int"): "bool",
    (">", "int", "int"): "bool",
    (">=", "int", "int"): "bool",
    ("==", "int", "int"): "bool",
    ("!=", "int", "int"): "bool",
    # Float operations
    ("+", "float", "float"): "float",
    ("-", "float", "float"): "float",
    ("*", "float", "float"): "float",
    ("/", "float", "float"): "float",
    ("<", "float", "float"): "bool",
    ("<=", "float", "float"): "bool",
    (">", "float", "float"): "bool",
    (">=", "float", "float"): "bool",
    ("==", "float", "float"): "bool",
    ("!=", "float", "float"): "bool",
    # Char operations
    ("<", "char", "char"): "bool",
    ("<=", "char", "char"): "bool",
    (">", "char", "char"): "bool",
    (">=", "char", "char"): "bool",
    ("==", "char", "char"): "bool",
    ("!=", "char", "char"): "bool",
    # Bool operations
    ("==", "bool", "bool"): "bool",
    ("!=", "bool", "bool"): "bool",
    ("&&", "bool", "bool"): "bool",
    ("||", "bool", "bool"): "bool",
}

_type_methname_map = {"int": "iconst", "float": "fconst"}

_type_type_map = {"int": INT32, "float": FLOAT64}

_op_methname_map = {
    ("+", "int"): "iadd",
    ("*", "int"): "imul",
}


@rule(If)
def generate_If(mod, func):
    # do the test
    generate(mod.test)


@rule(Statements)
def generate_Statements(node, mod):
    for s in node.statements:
        generate(s, mod)


@rule(Integer)
def generate_Integer(node, mod):
    mod.function.iconst(int(node.value))


@rule(Float)
def generate_Float(node, mod):
    mod.function.fconst(float(node.value))


@rule(Char)
def generate_Char(node, mod):
    mod.function.fconst(ord(node.char))


@rule(Var)
def generate_Var(node, mod):
    v_idx = mod.function.alloca(_type_type_map.get(node.type))
    # e.g. put float on stack
    generate(node.value, mod)

    mod.function.local_set(v_idx)
    mod.function.local_get(v_idx)
    mod.env[node.name] = v_idx


@rule(Variable)
def generate_Variable(node, mod):
    idx = mod.env.get(node.name)
    if idx:
        mod.function.local_get(idx)


# if test {
#    when_true
# } else {
#    when_false
# }
@rule(If)
def generate_If(node, mod):
    generate(node.test, mod)
    mod.function._if()
    generate(node.when_true, mod)
    mod.function._else()
    generate(node.when_false, mod)


@rule(BinOp)
def generate_BinOp(node, mod):
    generate(node.left, mod)
    generate(node.right, mod)

    op_methname = _op_methname_map.get((node.op, node.left.type))

    method = getattr(mod.function, op_methname)
    if method is None:
        raise SyntaxError(
            f"Cannot perform {node.op} operation on {node.left.type} and {node.right.type}"
        )

    method()


def main(filename):
    from .parse import parse_file
    from .typecheck import check_program

    model = parse_file(filename)
    check_program(model)
    mod = generate_program(model)
    with open("out.wasm", "wb") as file:
        file.write(encode_module(mod.module))
    print("Wrote out.wasm")


if __name__ == "__main__":
    import sys

    main(sys.argv[1])

