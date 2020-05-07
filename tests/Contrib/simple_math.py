
from wasm_compiler import *

mod = WasmModule("simple_math")

_print = WasmImportedFunction(mod, "runtime", "_print", [i32], [])
main = WasmFunction(mod, "main", [], [])

main.iconst(2)
main.iconst(3)
main.iconst(4)
main.imul()
main.iadd()
main.call(_print)

main.iconst(2)
main.iconst(3)
main.iadd()
main.call(_print)

main.iconst(2)
main.iconst(3)
main.imul()
main.iconst(4)
main.isub()
main.call(_print)


with open("simple_math.wasm", "wb") as file:
    file.write(encode_module(mod))
