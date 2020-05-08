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

    # Webassembly "op codes" (machine code)
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

    def iconst(self, value):
        self.code += b"\x41" + encode_signed(value)

    def iadd(self):
        self.code += b"\x6a"

    def isub(self):
        self.code += b"\x6b"

    def imul(self):
        self.code += b"\x6c"

    def idiv(self):
        self.code += b"\x6d"

    def ieq(self):
        self.code += b"\x46"

    def ine(self):
        self.code += b"\x47"

    def ilt(self):
        self.code += b"\x48"

    def ile(self):
        self.code += b"\x4c"

    def igt(self):
        self.code += b"\x4a"

    def ige(self):
        self.code += b"\x4e"

    def fconst(self, value):
        self.code += b"\x44" + encode_f64(value)

    def fadd(self):
        self.code += b"\xa0"

    def fsub(self):
        self.code += b"\xa1"

    def fmul(self):
        self.code += b"\xa2"

    def fdiv(self):
        self.code += b"\xa3"

    def feq(self):
        self.code += b"\x61"

    def fne(self):
        self.code += b"\x62"

    def flt(self):
        self.code += b"\x63"

    def fle(self):
        self.code += b"\x65"

    def fgt(self):
        self.code += b"\x64"

    def fge(self):
        self.code += b"\x66"

    def ret(self):
        self.code += b"\x0f"

    def call(self, func):
        self.code += b"\x10" + encode_unsigned(func.idx)

    def return_(self):
        self.code += b"\x0f"

    def if_(self):
        self.code += b"\x04\x40"

    def else_(self):
        self.code += b"\x05"

    def end_block(self):
        self.code += b"\x0b"

    def br(self, idx):
        self.code += b"\x0c" + encode_unsigned(idx)

    def br_if(self, idx):
        self.code += b"\x0d" + encode_unsigned(idx)

    def block(self):
        self.code += b"\x02\x40"

    def loop(self):
        self.code += b"\x03\x40"

    # Logical not
    def lnot(self):
        self.iconst(1)
        self.code += b"\x73"  # XOR


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
    def __init__(self, return_type):
        self.module = WasmModule("wabbit")
        # Current function (temporary hack. Set to main)
        self.function = WasmFunction(self.module, "main", [], [return_type])

        # Environment for tracking symbols
        self.env = ChainMap()
        self.prev = None

    def new_scope(self):
        self.prev = self.env
        self.env = self.env.new_child()
        return

    def previous_scope(self):
        self.env = self.prev
        return


# Top-level function for generating code from the model
def generate_program(model):
    # Typecheck. Annotates nodes with types.
    check_program(model)

    module = WabbitWasmModule(_type_type_map.get(model.type))

    generate(model, module)
    module.function.ret()
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
    ("<", "int", "int"): "ibool",
    ("<=", "int", "int"): "ibool",
    (">", "int", "int"): "ibool",
    (">=", "int", "int"): "ibool",
    ("==", "int", "int"): "ibool",
    ("!=", "int", "int"): "ibool",
    # Float operations
    ("+", "float", "float"): "float",
    ("-", "float", "float"): "float",
    ("*", "float", "float"): "float",
    ("/", "float", "float"): "float",
    ("<", "float", "float"): "fbool",
    ("<=", "float", "float"): "fbool",
    (">", "float", "float"): "fbool",
    (">=", "float", "float"): "fbool",
    ("==", "float", "float"): "fbool",
    ("!=", "float", "float"): "fbool",
    # Char operations
    ("<", "char", "char"): "ibool",
    ("<=", "char", "char"): "ibool",
    (">", "char", "char"): "ibool",
    (">=", "char", "char"): "ibool",
    ("==", "char", "char"): "ibool",
    ("!=", "char", "char"): "ibool",
    # Bool operations
    ("==", "ibool", "ibool"): "ibool",
    ("!=", "ibool", "ibool"): "ibool",
    ("&&", "ibool", "ibool"): "ibool",
    ("||", "ibool", "ibool"): "ibool",
}

_type_methname_map = {"int": "iconst", "float": "fconst"}

_type_type_map = {"int": INT32, "float": FLOAT64, "ibool": INT32, "fbool": FLOAT64}

_op_methname_map = {
    ("+", "int"): "iadd",
    ("*", "int"): "imul",
    ("/", "int"): "idiv",
    ("-", "int"): "isub",
    (">", "int"): "igt",
    ("<", "int"): "ilt",
    (">", "float"): "fgt",
    ("<", "float"): "flt",
}


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
    mod.env[node.name] = v_idx


@rule(Variable)
def generate_Variable(node, mod):
    idx = mod.env.get(node.name)
    print("idx", node.name, idx)
    if idx is None:
        raise SyntaxError(f"Cannot find variable {node.name} in scope")

    mod.function.local_get(idx)


@rule(FunctionDefinition)
def generate_FunctionDefinition(node, mod):
    arg_types = [_type_type_map.get(a.type) for a in node.args.args]
    return_types = [_type_type_map.get(node.type)]

    main = mod.function
    f_def = WasmFunction(mod.module, node.name, arg_types, return_types)
    mod.function = f_def

    mod.new_scope()
    for i, param in enumerate(node.args.args):
        mod.env[param.name] = i

    for statement in node.body:
        generate(statement, mod)
    mod.previous_scope()

    mod.function = main

    # set function as a local variable
    mod.env[node.name] = f_def


@rule(FunctionCall)
def generate_FunctionCall(node, mod):
    func = mod.env[node.name]

    # put args onto stack
    for argument in node.args:
        generate(argument, mod)

    mod.function.call(func)


@rule(Return)
def generate_Return(node, mod):
    generate(node.value, mod)
    mod.function.ret()


# if test {
#    when_true
# } else {
#    when_false
# }
@rule(If)
def generate_If(node, mod):
    generate(node.test, mod)

    mod.function.if_()

    mod.new_scope()
    generate(node.when_true, mod)
    mod.previous_scope()

    mod.function.else_()

    if node.when_false:
        mod.new_scope()
        generate(node.when_false, mod)
        mod.previous_scope()

    mod.function.end_block()


# Instruction table for binops
_ops = {
    "+": "add",
    "-": "sub",
    "*": "mul",
    "/": "div",
    "<": "lt",
    "<=": "le",
    ">": "gt",
    ">=": "ge",
    "==": "eq",
    "!=": "ne",
}


@rule(BinOp)
def generate_BinOp(node, mod):
    generate(node.left, mod)
    generate(node.right, mod)
    # Emit the appropriate opcode
    if node.left.type == "int":
        prefix = "i"
    else:
        prefix = "f"
    inst = f"{prefix}{_ops[node.op]}"
    getattr(mod.function, inst)()


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

