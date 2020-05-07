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

    def __init__(self, module, env_name, name, arg_types, return_types):
        self.module = module
        self.env_name = env_name
        self.name = name
        self.arg_types = arg_types
        self.return_types = return_types

        self.idx = len(module.imported_functions)
        module.imported_functions.append(self)


class WasmFunction:
    """
    A natively defined Wasm function
    """

    def __init__(self, module, name, arg_types, return_types):
        self.module = module
        self.name = name
        self.arg_types = arg_types
        self.return_types = return_types

        self.idx = len(module.imported_functions) + len(module.functions)
        module.functions.append(self)

        # Code generation
        self.code = b""

        # Types of local variables
        self.local_types = []

    def iconst(self, value):
        self.code += i32const + encode_signed(value)

    def iadd(self):
        self.code += i32add

    def imul(self):
        self.code += i32mul

    def call(self, func):
        self.code += b"\x10" + encode_unsigned(func.idx)

    def ret(self):
        self.code += return_type

    def alloca(self, type):
        idx = len(self.local_types) + len(self.arg_types)
        self.local_types.append(self)
        return idx

    def local_get(self, idx):
        self.code += local_get + encode_unsigned(idx)

    def local_set(self, idx):
        self.code += local_set + encode_unsigned(idx)

    def global_get(self, gvar):
        self.code += global_get + encode_unsigned(gvar.idx)

    def global_set(self, gvar):
        self.code += global_set + encode_unsigned(gvar.idx)


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
    mod = WabbitWasmModule()
    generate(model, mod)
    return mod


# Internal function for generating code on each node
def generate(node, mod):
    raise RuntimeError(f"Can't generate {node}")


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

