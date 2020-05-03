# wabbit/llvm.py
#
# In this file you will have your compiler generate LLVM output.  Don't
# start this unless you have first worked through the LLVM Tutorial:
#
#     https://github.com/dabeaz/compilers_2020_05/wiki/LLVM-Tutorial
#
# Once you have done that, come back here.
#
# The overall strategy here is going to be very similar to how type
# checking works. Recall, in type checking, there was an environment
# and functions like this:
#
#    def check_expression(node, env):
#        ...
#
# It's going to be almost exactly the same idea here. Instead of an
# environment, define a class that represents an LLVM Module:
#
#    class LLVMModule:
#        ...
#
# This module will contain everything that's needed to output LLVM
# code. Build it from what you learned in the LLVM tutorial (i.e.,
# you'll have a function, an IRBuilder, a basic block, etc.).
#
# Write functions that accept the LLVM module as an argument.  For
# example:
#
#    def generate_expression(node, mod):
#       ...
#
# In these functions, you will produce code by interacting with the 
# module in some way.
#
# One somewhat messy bit concerns the mapping of Wabbit types to
# LLVM types. You'll probably want to make some type objects to help.
# (see below)

from llvmlite import ir
from .model import *

# Define LLVM types corresponding to Wabbit types
int_type = ir.IntType(32)
float_type = ir.DoubleType()
bool_type = ir.IntType(1)
char_type = ir.IntType(8)

# The LLVM world that Wabbit is populating
class WabbitLLVMModule:
    pass

# Top-level function
def generate_program(model):
    mod = WabbitLLVMModule()
    generate(model, mod)
    return mod

# Internal function to to generate code for each node type
def generate(node, mod):
    raise RuntimeError(f"Can't generate code for {node}")

# Sample main program that runs the compiler
def main(filename):
    from .parse import parse_file
    from .typecheck import check_program

    model = parse_file(filename)
    check_program(model):
    mod = generate_program(model)
    with open('out.ll', 'w') as file:
        file.write(str(mod))
    print('Wrote out.ll')

if __name__ == '__main__':
    import sys
    main(sys.argv[1])



