# example.py
# flake8: noqa

from wasm import *

mod = WasmModule('example')

# func f() int {
#    return 2*3 + 4*5;
# }

f = WasmFunction(mod, 'f', [], [i32])
f.iconst(2)
f.iconst(3)
f.imul()
f.iconst(4)
f.iconst(5)
f.imul()
f.iadd()
f.ret()


# func g(x int, y int) int {
#    var z int = x + y;
#    return z;
# }

g = WasmFunction(mod, 'g', [i32, i32], [i32])
z_idx = g.alloca(i32)
g.local_get(0)      # x
g.local_get(1)      # y
g.iadd()            # x + y
g.local_set(z_idx)  # z = x + y
g.local_get(z_idx)  # load z
g.ret()


# var n int = 13;
#
# func h(d int) int {
#     n = n + d;
#     return n;
# }

n_var = WasmGlobalVariable(mod, "n", i32, 13)
h = WasmFunction(mod, "h", [i32], [i32])
h.global_get(n_var)
h.local_get(0)
h.iadd()
h.global_set(n_var)
h.global_get(n_var)
h.ret()

with open('example.wasm', 'wb') as file:
    file.write(encode_module(mod))
