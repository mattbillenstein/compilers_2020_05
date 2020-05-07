# from wabbit.wasm import *
# from wabbit.was# wasm.py

from wabbit.wasm import *
from wabbit.model import *


# def test_wasm():
# mod = WasmModule("example")
# _print = WasmImportedFunction(mod, "runtime", "_print", [INT32], [])
# main = WasmFunction(mod, "main", [], [])
# main.iconst(42)
# main.call(_print)
# main.iconst(2)
# main.iconst(3)
# main.imul()
# main.iconst(4)
# main.iconst(5)
# main.imul()
# main.iadd()
# main.call(_print)
# main.ret()

# # Write to a file
# with open("out_runtime.wasm", "wb") as file:
#     file.write(encode_module(mod))


def test_wasm_basic():
    model = Statements([BinOp("*", Float("9.3"), Float("2.3"))])

    mod = generate_program(model)
    # Write to a file
    with open("out_runtime.wasm", "wb") as file:
        file.write(encode_module(mod))
    assert encode_module(mod) == ""
