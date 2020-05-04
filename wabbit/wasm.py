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

# Class representing the world of Wasm
class WabbitWasmModule:
    pass

# Top-level function for generating code from the model
def generate_program(model):
    mod = WabbitWasmModule()
    generate(model, mod)
    return mod

# Internal function for generating code on each node
def generate(node, mod):
    raise RuntimeError(f"Can't generate {node}")

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

        
        

    

                   
