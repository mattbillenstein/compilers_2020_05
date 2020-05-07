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
from collections import ChainMap
from functools import singledispatch

# ---- Wasm Encoding code --- from the tutorial

def encode_unsigned(value):
    '''
    Produce an LEB128 encoded unsigned integer.
    '''
    parts = []
    while value:
        parts.append((value & 0x7f) | 0x80)
        value >>= 7
    if not parts:
        parts.append(0)
    parts[-1] &= 0x7f
    return bytes(parts)

def encode_signed(value):
    '''
    Produce a LEB128 encoded signed integer.
    '''
    parts = [ ]
    if value < 0:
        # Sign extend the value up to a multiple of 7 bits
        value = (1 << (value.bit_length() + (7 - value.bit_length() % 7))) + value
        negative = True
    else:
        negative = False
    while value:
        parts.append((value & 0x7f) | 0x80)
        value >>= 7
    if not parts or (not negative and parts[-1] & 0x40):
        parts.append(0)
    parts[-1] &= 0x7f
    return bytes(parts)

assert encode_unsigned(624485) == bytes([0xe5, 0x8e, 0x26])
assert encode_unsigned(127) == bytes([0x7f])
assert encode_signed(-624485) == bytes([0x9b, 0xf1, 0x59])
assert encode_signed(127) == bytes([0xff, 0x00])

import struct

def encode_f64(value):
    '''
    Encode a 64-bit float point as little endian
    '''
    return struct.pack('<d', value)

def encode_vector(items):
    '''
    A size-prefixed collection of objects.  If items is already
    bytes, it is prepended by a length and returned.  If items
    is a list of byte-strings, the length of the list is prepended
    to byte-string formed by concatenating all of the items.
    '''
    if isinstance(items, bytes):
        return encode_unsigned(len(items)) + items
    else:
        return encode_unsigned(len(items)) + b''.join(items)

def encode_string(text):
    '''
    Encode a text string as a UTF-8 vector
    '''
    return encode_vector(text.encode('utf-8'))

# Wasm Type names
i32 = b'\x7f'   # (32-bit int)
i64 = b'\x7e'   # (64-bit int)
f32 = b'\x7d'   # (32-bit float)
f64 = b'\x7c'   # (64-bit float)

class WasmModule:
    def __init__(self, name):
        self.name = name
        self.imported_functions = [ ]
        self.functions = [ ]
        self.global_variables = [ ]

class WasmImportedFunction:
    '''
    A function defined outside of the Wasm environment
    '''
    def __init__(self, module, envname, name, argtypes, rettypes):
        self.module = module
        self.envname = envname
        self.name = name
        self.argtypes = argtypes
        self.rettypes = rettypes
        self.idx = len(module.imported_functions)
        module.imported_functions.append(self)

class WasmFunction:
    '''
    A natively defined Wasm function
    '''
    def __init__(self, module, name, argtypes, rettypes):
        self.module = module
        self.name = name
        self.argtypes = argtypes
        self.rettypes = rettypes
        self.idx = len(module.imported_functions) + len(module.functions)
        module.functions.append(self)

        # Code generation
        self.code = b''

        # Local variable types
        self.local_types = [ ]

    # Webassembly "op codes" (machine code)
    def alloca(self, type):
        idx = len(self.argtypes) + len(self.local_types)
        self.local_types.append(type)
        return idx

    def local_get(self, idx):
        self.code += b'\x20' + encode_unsigned(idx)

    def local_set(self, idx):
        self.code += b'\x21' + encode_unsigned(idx)

    def global_get(self, gvar):
        self.code += b'\x23' + encode_unsigned(gvar.idx)

    def global_set(self, gvar):
        self.code += b'\x24' + encode_unsigned(gvar.idx)

    def iconst(self, value):
        self.code += b'\x41' + encode_signed(value)

    def iadd(self):
        self.code += b'\x6a'

    def imul(self):
        self.code += b'\x6c'

    def ret(self):
        self.code += b'\x0f'

    def call(self, func):
        self.code += b'\x10' + encode_unsigned(func.idx)

class WasmGlobalVariable:
    '''
    A natively defined Wasm global variable
    '''
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
    return b'\x60' + encode_vector(func.argtypes) + encode_vector(func.rettypes)

def encode_import_function(func):
    return (encode_string(func.envname) + 
            encode_string(func.name) + 
            b'\x00' +
            encode_unsigned(func.idx))

def encode_global(gvar):
    if gvar.type == i32:
        return i32 + b'\x01\x41' + encode_signed(gvar.initializer) + b'\x0b'
    elif gvar.type == f64:
        return f64 + b'\x01\x44' + encode_f64(gvar.initializer) + b'\x0b'

def encode_export_function(func):
    return encode_string(func.name) + b'\x00' + encode_unsigned(func.idx)

def encode_function_code(func):
    localtypes = [ b'\x01' + ltype for ltype in func.local_types ]
    if not func.code[-1:] == b'\x0b':
        func.code += b'\x0b'
    code = encode_vector(localtypes) + func.code
    return encode_unsigned(len(code)) + code

def encode_module(module):
    # section 1 - signatures
    all_funcs = module.imported_functions + module.functions
    signatures = [encode_signature(func) for func in all_funcs]
    section1 = encode_section(1, encode_vector(signatures))

    # section 2 - Imports
    all_imports = [ encode_import_function(func) for func in module.imported_functions ]
    section2 = encode_section(2, encode_vector(all_imports))

    # section 3 - Functions
    section3 = encode_section(3, encode_vector([encode_unsigned(f.idx) for f in module.functions]))

    # section 7 - Exports
    all_exports = [ encode_export_function(func) for func in module.functions ]
    section7 = encode_section(7, encode_vector(all_exports))

    # section 6 - Globals
    all_globals = [ encode_global(gvar) for gvar in module.global_variables ]
    section6 = encode_section(6, encode_vector(all_globals))

    # section 10 - Code
    all_code = [ encode_function_code(func) for func in module.functions ]
    section10 = encode_section(10, encode_vector(all_code))

    return b''.join([b'\x00asm\x01\x00\x00\x00',
                    section1,
                    section2,
                    section3,
                    section6,
                    section7,
                    section10])

# ----------------- END Tutorial code

# Class representing the world of Wasm
class WabbitWasmModule:
    def __init__(self):
        # You need to set up the Wasm code generation parts here.
        # Similar to the tutorial
        self.module = WasmModule('wabbit')

        # Current function (temporary hack. Set to main)
        self.function = WasmFunction(self.module, 'main', [], [])

        # Environment for tracking symbols
        self.env = ChainMap()

# Top-level function for generating code from the model
def generate_program(model):
    mod = WabbitWasmModule()
    generate(model, mod)
    return mod

# Internal function for generating code on each node

@singledispatch
def generate(node, mod):
    raise RuntimeError(f"Can't generate {node}")

rule = generate.register

@rule(Integer)
def generate_integer(node, mod: WabbitWasmModule):
    mod.function.iconst(node.value)

@rule(BinOp)
def generate_binop(node, mod):
    generate(node.left, mod)
    generate(node.right, mod)
    # Emit the appropriate opcode
    if node.left.type == 'int':
        if node.op == '+':
            mod.function.iadd()
        elif node.op == '-':
            mod.function.isub()
        elif node.op == '*':
            mod.function.imul()
    elif node.left.type == 'float':
        if node.op == '+':
            mod.function.fadd()
        ...

@rule(UnaryOp)
def generate_unaryop(node, mod):
    pass

# if test {
#    consequence;
# } else {
#    altenrative.
# }

@rule(IfStatement)
def generate_if_statement(node, mod):
    generate(node.test, mod)
    mod.function.if_()
    generate(node.consequence, mod)
    mod.function.else_()
    generate(node.alternative, mod)
    mod.function.end_block()

def main(filename):
    from .parse import parse_file
    from .typecheck import check_program
    model = parse_file(filename)
    check_program(model):
    mod = generate_program(model)
    with open('out.wasm', 'wb') as file:
        file.write(encode_module(mod.module))
    print("Wrote out.wasm")

if __name__ == '__main__':
    import sys
    main(sys.argv[1])

        
        

    

                   
