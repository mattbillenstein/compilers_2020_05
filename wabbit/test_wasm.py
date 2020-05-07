# from wabbit.wasm import *
# from wabbit.was# wasm.py

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

    def iadd(self):
        self.code += b"\x6a"

    def imul(self):
        self.code += b"\x6c"

    def ret(self):
        self.code += b"\x0f"

    def call(self, func):
        self.code += b"\x10" + encode_unsigned(func.idx)

    def alloca(self, type):
        idx = len(self.argtypes) + len(self.local_types)
        self.local_types.append(type)

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


def test_wasm():
    mod = WasmModule("example")
    _print = WasmImportedFunction(mod, "runtime", "_print", [i32], [])
    main = WasmFunction(mod, "main", [], [])
    main.iconst(42)
    main.call(_print)
    main.iconst(2)
    main.iconst(3)
    main.imul()
    main.iconst(4)
    main.iconst(5)
    main.imul()
    main.iadd()
    main.call(_print)
    main.ret()

    # Write to a file
    with open("out_runtime.wasm", "wb") as file:
        file.write(encode_module(mod))
