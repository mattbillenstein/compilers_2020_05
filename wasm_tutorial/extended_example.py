"""extended_example.py

This example is used to verify that integer subtraction and division
are working, as well as all four basic operations for floating point number.
"""
# flake8: noqa

from wasm import *

mod = WasmModule('extended_example')

# func f() int {
#    return 28/4;
# }

f = WasmFunction(mod, 'f', [], [i32])
f.iconst(28)
f.iconst(4)
f.idiv()
f.ret()

# func g() int {
#    return 7 - 2;
# }

g = WasmFunction(mod, 'g', [], [i32])
g.iconst(7)
g.iconst(2)
g.isub()
g.ret()

# func h() float {
#    return 2.*0.5 + 5./2.;
# }

h = WasmFunction(mod, 'h', [], [f64])
h.fconst(2.)
h.fconst(0.5)
h.fmul()
h.fconst(5.)
h.fconst(2.)
h.fdiv()
h.fadd()
h.ret()

# func k() int {
#    return 3.5 - 1.25;
# }

k = WasmFunction(mod, 'k', [], [f64])
k.fconst(3.5)
k.fconst(1.25)
k.fsub()
k.ret()


with open('extended_example.wasm', 'wb') as file:
    file.write(encode_module(mod))
