# example.py
# flake8: noqa

from wasm import *

mod = WasmModule("example_2")

# var main() void {
#     print 42;
#     print 2*3 + 4*5;
# }

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
with open("example_2.wasm", "wb") as file:
    file.write(encode_module(mod))
