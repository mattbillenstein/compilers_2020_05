# transform.py
#
# The goal of this project is to apply transforms to the model,
# possibly for the purpose of code optimization, or to simplify
# later code generation.  Note: This is a completely optional
# part of the compiler.  If you're busy working on other things,
# continue working on that.  However, if you want a break,
# come back here.
#
# As an example, you could implement constant folding. Suppose
# you had a BinOp like this:
#
#    node = BinOp('+', Integer(2), Integer(3))
#
# You could replace the node with a new node like this:
#
#    node = Integer(5)
#
# To the compiler, it won't matter---the finally produced code
# will be the same. 
#
# One thing that's a bit different about this project is that 
# it's mostly just focused on the structure of the model itself
# and not aspects of type checking or code generation.  Mostly
# it's just about transformation.  You write functions like this:
#
#   def transform_binop(node):
#       ... look at node ...
#       newnode = ... make a new node (if required) ...
#       return newnode
#

from .model import *

def transform(node):
    # Return the node back (unmodified) or a new node in its place
    return node

# Main function (for testing)
def main(filename):
    from .parse import parse_file
    model = parse_file(filename)
    model = transform(model)
    print(model)

if __name__ == '__main__':
    import sys
    main(sys.argv[1])
