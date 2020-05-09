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

from .model import *
from .typecheck import check_program
from collections import ChainMap
from functools import singledispatch

# ---- Wasm Encoding code --- from the tutorial


def encode_unsigned(value):
    """
    Produce an LEB128 encoded unsigned integer.
    """
    parts = []
    while value:
        parts.append((value & 0x7F) | 0x80)
        value >>= 7
    if not parts:
        parts.append(0)
    parts[-1] &= 0x7F
    return bytes(parts)


def encode_signed(value):
    """
    Produce a LEB128 encoded signed integer.
    """
    parts = []
    if value < 0:
        # Sign extend the value up to a multiple of 7 bits
        value = (1 << (value.bit_length() + (7 - value.bit_length() % 7))) + value
        negative = True
    else:
        negative = False
    while value:
        parts.append((value & 0x7F) | 0x80)
        value >>= 7
    if not parts or (not negative and parts[-1] & 0x40):
        parts.append(0)
    parts[-1] &= 0x7F
    return bytes(parts)


assert encode_unsigned(624485) == bytes([0xE5, 0x8E, 0x26])
assert encode_unsigned(127) == bytes([0x7F])
assert encode_signed(-624485) == bytes([0x9B, 0xF1, 0x59])
assert encode_signed(127) == bytes([0xFF, 0x00])

import struct


def encode_f64(value):
    """
    Encode a 64-bit float point as little endian
    """
    return struct.pack("<d", value)


def encode_vector(items):
    """
    A size-prefixed collection of objects.  If items is already
    bytes, it is prepended by a length and returned.  If items
    is a list of byte-strings, the length of the list is prepended
    to byte-string formed by concatenating all of the items.
    """
    if isinstance(items, bytes):
        return encode_unsigned(len(items)) + items
    else:
        return encode_unsigned(len(items)) + b"".join(items)


def encode_string(text):
    """
    Encode a text string as a UTF-8 vector
    """
    return encode_vector(text.encode("utf-8"))


# Wasm Type names
i32 = b"\x7f"  # (32-bit int)
i64 = b"\x7e"  # (64-bit int)
f32 = b"\x7d"  # (32-bit float)
f64 = b"\x7c"  # (64-bit float)


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

        # Local variable types
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


def encode_section(sectnum, contents):
    return bytes([sectnum]) + encode_unsigned(len(contents)) + contents


def encode_signature(func):
    return b"\x60" + encode_vector(func.argtypes) + encode_vector(func.rettypes)


def encode_import_function(func):
    return (
        encode_string(func.envname)
        + encode_string(func.name)
        + b"\x00"
        + encode_unsigned(func.idx)
    )


def encode_global(gvar):
    if gvar.type == i32:
        return i32 + b"\x01\x41" + encode_signed(gvar.initializer) + b"\x0b"
    elif gvar.type == f64:
        return f64 + b"\x01\x44" + encode_f64(gvar.initializer) + b"\x0b"


def encode_export_function(func):
    return encode_string(func.name) + b"\x00" + encode_unsigned(func.idx)


def encode_function_code(func):
    localtypes = [b"\x01" + ltype for ltype in func.local_types]
    if not func.code[-1:] == b"\x0b":
        func.code += b"\x0b"
    code = encode_vector(localtypes) + func.code
    return encode_unsigned(len(code)) + code


def encode_module(module):
    # section 1 - signatures
    all_funcs = module.imported_functions + module.functions
    signatures = [encode_signature(func) for func in all_funcs]
    section1 = encode_section(1, encode_vector(signatures))

    # section 2 - Imports
    all_imports = [encode_import_function(func) for func in module.imported_functions]
    section2 = encode_section(2, encode_vector(all_imports))

    # section 3 - Functions
    section3 = encode_section(
        3, encode_vector([encode_unsigned(f.idx) for f in module.functions])
    )

    # section 7 - Exports
    all_exports = [encode_export_function(func) for func in module.functions]
    section7 = encode_section(7, encode_vector(all_exports))

    # section 6 - Globals
    all_globals = [encode_global(gvar) for gvar in module.global_variables]
    section6 = encode_section(6, encode_vector(all_globals))

    # section 10 - Code
    all_code = [encode_function_code(func) for func in module.functions]
    section10 = encode_section(10, encode_vector(all_code))

    return b"".join(
        [
            b"\x00asm\x01\x00\x00\x00",
            section1,
            section2,
            section3,
            section6,
            section7,
            section10,
        ]
    )


# ----------------- END Tutorial code

# Class representing the world of Wasm
class WabbitWasmModule:
    def __init__(self):
        # You need to set up the Wasm code generation parts here.
        # Similar to the tutorial
        self.module = WasmModule("wabbit")

        # Declare runtime functions (from javascript)
        # self._printi = WasmImportedFunction(
        #     self.module, "runtime", "_printi", [i32], []
        # )
        # self._printf = WasmImportedFunction(
        #     self.module, "runtime", "_printf", [f64], []
        # )
        # self._printb = WasmImportedFunction(
        #     self.module, "runtime", "_printb", [i32], []
        # )
        # self._printc = WasmImportedFunction(
        #     self.module, "runtime", "_printc", [i32], []
        # )

        # Current function (temporary hack. Set to _init)
        self.function = self._init_function = WasmFunction(self.module, "_init", [], [])

        # Environment for tracking symbols
        self.env = ChainMap()

    # Functions for creating, popping environments
    def new_env(self):
        self.env = self.env.new_child()
        return self

    def pop_env(self):
        self.env = self.env.parents


# Mapping of Wabbit types to Wasm types
_typemap = {"int": i32, "float": f64, "bool": i32, "char": i32}

# Top-level function for generating code from the model
def generate_program(model):
    mod = WabbitWasmModule()
    check_program(model)
    generate(model, mod)

    # If there's no main function... generate an empty one just to get the
    # global init code to run (see hack in generate_function_definition below)
    if "main" not in mod.env:
        generate(
            FunctionDefinition("main", [], "int", Statements([Return(Integer(0))])),
            mod,
        )
    mod.function.end_block()

    return mod


# Internal function for generating code on each node


@singledispatch
def generate(node, mod):
    raise RuntimeError(f"Can't generate {node}")


rule = generate.register


@rule(Statements)
def generate_statements(node, mod):
    for stmt in node.statements:
        generate(stmt, mod)


@rule(Integer)
def generate_integer(node, mod: WabbitWasmModule):
    mod.function.iconst(node.value)


@rule(Float)
def generate_float(node, mod):
    mod.function.fconst(float(node.value))


@rule(Truthy)
def generate_Truthy(node, mod):
    mod.function.iconst(1)


@rule(Falsey)
def generate_Falsey(node, mod):
    mod.function.iconst(0)


@rule(Char)
def generate_float(node, mod):
    mod.function.iconst(ord(node.value))


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
def generate_binop(node, mod):
    generate(node.left, mod)
    generate(node.right, mod)
    if node.left.type == "float":
        prefix = "f"
    else:
        prefix = "i"
    inst = f"{prefix}{_ops[node.op]}"
    getattr(mod.function, inst)()


@rule(UnaryOp)
def generate_unaryop(node, mod):
    # - op.   Could I recast as 0 - op?
    if node.op == "-":
        if node.target.type == "int":
            left = Integer(0)
        elif node.target.type == "float":
            left = Float("0.0")
        generate_binop(BinOp("-", left, node.target), mod)
        return
    # + op    -- Does nothing
    generate(node.target, mod)
    if node.op == "+":
        return
    if node.op == "!":
        mod.function.lnot()


@rule(Grouping)
def generate_grouping(node, mod):
    generate(node.expression, mod)


@rule(Var)
@rule(Const)
def generate_var_definition(node, mod):
    # Need to declare as a Wasm global variable
    # (or local variable if in function)
    wtype = _typemap[node.type]

    if len(mod.env.maps) == 1:
        vardecl = WasmGlobalVariable(mod.module, node.name, wtype, 0)
    else:
        vardecl = mod.function.alloca(wtype)

    mod.env[node.name] = vardecl
    if node.value:
        generate(node.value, mod)
        if isinstance(vardecl, WasmGlobalVariable):
            mod.function.global_set(vardecl)
        else:
            mod.function.local_set(vardecl)


@rule(Variable)
def generate_variable(node, mod):
    wdecl = mod.env[node.name]

    if isinstance(wdecl, WasmGlobalVariable):
        mod.function.global_get(wdecl)
    else:
        mod.function.local_get(wdecl)


@rule(Assignment)
def generate_assignment(node, mod):
    generate(node.location, mod)
    wdecl = mod.env[node.location.name]

    generate(node.expression, mod)
    if isinstance(wdecl, WasmGlobalVariable):
        mod.function.global_set(wdecl)
    else:
        mod.function.local_set(wdecl)


@rule(Print)
def generate_print_statement(node, mod):
    generate(node.value, mod)
    # ty = node.expression.type
    # if ty == "int":
    #     mod.function.call(
    #         mod._printi
    #     )  # These functions are imported from Javascript environment
    # elif ty == "float":
    #     mod.function.call(mod._printf)
    # elif ty == "bool":
    #     mod.function.call(mod._printb)
    # elif ty == "char":
    #     mod.function.call(mod._printc)
    # else:
    #     assert False


# if test {
#    consequence;
# } else {
#    altenrative.
# }


@rule(If)
def generate_if_statement(node, mod):
    generate(node.test, mod)
    mod.function.if_()
    generate(node.consequence, mod.new_env())
    mod.pop_env()
    if node.alternative:
        mod.function.else_()
        generate(node.alternative, mod.new_env())
        mod.pop_env()
    mod.function.end_block()


# while test {
#    body
# }
#
# In Wasm, while loops are encoded in a very strange way...
#
# block {
#    loop {
#        not test
#        br_if 1   # 1 refers to "block"
#        body
#        br 0      # 0 refers to "loop"
#    }
# }


@rule(While)
def generate_while_statement(node, mod):
    mod.function.block()  # block
    mod.function.loop()
    generate(node.test, mod)
    mod.function.lnot()
    mod.function.br_if(1)
    generate(node.consequence, mod.new_env())
    mod.pop_env()
    mod.function.br(0)
    mod.function.end_block()  # loop
    mod.function.end_block()  # block


@rule(Break)
def generate_Break(node, mod):
    mod.function.br(2)


# ---------------- Functions


@rule(FunctionDefinition)
def generate_function_definition(node, mod):
    # Discussion.... There is an implicit "outer" function being created that's
    # used to initialize the global variables and run scripting-level statements.
    # When a function definition is encountered, we have to temporarily suspend
    # what we're doing with that and start creating a new function.

    # Save the current function
    current_function = mod.function

    # Map the function parameters to web assembly types
    argtypes = [_typemap[parm.type] for parm in node.args]

    # Map the function return type to a web assembly type
    rettype = [_typemap[node.return_type]]

    # Create the new Wasm function
    mod.function = WasmFunction(mod.module, node.name, argtypes, rettype)
    mod.env[node.name] = mod.function

    # Now have create a new environment and set it up for visit the function body
    mod.new_env()
    # Bind function arguments
    for n, parm in enumerate(node.args):
        mod.env[parm.name] = n  # Local variables are referenced by numeric index

    # Hack alert.  If main(), we inject a call to _init() to set up the globals
    if node.name == "main":
        mod.function.call(mod._init_function)

    generate(node.body, mod)
    mod.pop_env()

    # Restore the previous function
    mod.function = current_function


@rule(FunctionCall)
def generate_function_application(node, mod):
    for arg in node.args:
        generate(arg, mod)
    mod.function.call(mod.env[node.name])


@rule(Return)
def generate_return_statement(node, mod):
    if node.value:
        generate(node.value, mod)
    mod.function.return_()


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

