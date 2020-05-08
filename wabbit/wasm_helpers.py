import struct

# Wasm Type names
INT32 = b"\x7f"  # (32-bit int)
INT64 = b"\x7e"  # (64-bit int)
FLOAT32 = b"\x7d"  # (32-bit float)
FLOAT64 = b"\x7c"  # (64-bit float)
I32CONST = b"\x41"  # <value>  => i32.const value
F64CONST = b"\x44"  # <value>  => f64.const value


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


def encode_string(name):
    """
    Encode a text name as a UTF-8 vector
    """
    return encode_vector(name.encode("utf-8"))


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


def encode_export_function(func):
    return encode_string(func.name) + b"\x00" + encode_unsigned(func.idx)


def encode_function_code(func):
    localtypes = [b"\x01" + ltype for ltype in func.local_types]
    if not func.code[-1:] == b"\x0b":
        func.code += b"\x0b"
    code = encode_vector(localtypes) + func.code
    return encode_unsigned(len(code)) + code


def encode_global(gvar):
    if gvar.type == INT32:
        return INT32 + b"\x01\x41" + encode_signed(gvar.initializer) + b"\x0b"
    elif gvar.type == FLOAT64:
        return FLOAT64 + b"\x01\x44" + encode_f64(gvar.initializer) + b"\x0b"


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

    # section 6 - Globals
    all_globals = [encode_global(gvar) for gvar in module.global_variables]
    section6 = encode_section(6, encode_vector(all_globals))

    # section 7 - Exports
    all_exports = [encode_export_function(func) for func in module.functions]
    section7 = encode_section(7, encode_vector(all_exports))

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

