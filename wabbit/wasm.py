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

from wabbit.model import *
from wabbit.wasm_helpers import *
from functools import singledispatch


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
    pass


# Top-level function for generating code from the model
def generate_program(model):
    mod = WasmModule("example")
    _print = WasmImportedFunction(mod, "runtime", "_print", [FLOAT64], [])
    main = WasmFunction(mod, "main", [], [])

    generate(model, main)

    main.call(_print)
    main.ret()
    return mod


# Internal function for generating code on each node
@singledispatch
def generate(node, mod):
    raise RuntimeError(f"Can't generate {node}")


rule = generate.register


@rule(Statements)
def generate_Statements(node, func):
    for s in node.statements:
        generate(s, func)


@rule(Float)
def generate_Float(node, func):
    print("fconst")
    func.fconst(float(node.value))


@rule(BinOp)
def generate_BinOp(node, func):
    func.fadd()


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

