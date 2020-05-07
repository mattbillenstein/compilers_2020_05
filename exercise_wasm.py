from wabbit.wasm import write_out, WasmModule, WasmImportedFunction, WasmFunction, encode_module, i32
from wabbit.model import *
from wabbit.parse import parse_source

def harness(name, source):
    print(name)
    print('source:', source)
    node = parse_source(source)
    print('model: ', node)
    write_out(node)
    print()

# harness('0', 'print 3;')
harness('0', 'print 3 + 201;')

# mod = WasmModule('example')
# _print = WasmImportedFunction(mod, 'runtime','_print', [i32], [])
# main = WasmFunction(mod, 'main', [], [])
# main.iconst(42)
# main.call(_print)
# with open('out_runtime.wasm', 'wb') as file:
    # file.write(encode_module(mod))
# print("Wrote out.wasm")

# write_out(PrintStatement(Integer(2)))
