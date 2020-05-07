# c.py
#
# In this file, we're going to transform Wabbit code to C, using it as
# a kind of low-level machine language. At first glance, this might
# sound somewhat crazy, but it actually makes sense for a number of
# reasons.  First, C compilers are standardized and ubiquitous--being
# available everywhere. Second, C is so minimal in features that you
# can use it at a low-level without having to worry about hidden
# side-effects (i.e., garbage collection, etc.).  You can also abuse
# it all sorts of horrible ways to do unnatural acts of programming
# (useful if making a new language).  Finally, in getting
# your compiler to actually "work", there may be certain runtime
# elements that are quite hard to implement or debug directly with machine
# instructions. Therefore, it might be easier to implement things in C 
# as a first step.
#
# As a preliminary step, please read the short C tutorial at
#
#  https://github.com/dabeaz/compilers_2020_05/wiki/C-Programming-Tutorial
#
# Come back here when you've looked it over.  Our goal is to produce
# low-level C code where you are ONLY allowed to use the 
# the following C features:
#
# 1. You can only declare uninitialized variables.  For example:
# 
#         int x;
#         float y;
#         int z = 2 + 3;     // NO!!!!!!!!
#
#    All variables must be declared before use, at the top of the
#    file or function. Reminder: they are uninitialized.
#
# 2. You can only perform ONE operation at a time. Operations can
#    only involve constants and variabless.  The result of an
#    operation must always be immediately stored in a variable.  For
#    example, to compute 2 + 3 * 4, you might do this:
#
#         int _i1;      /* Temporary variables */
#         int _i2;
#
#         _i1 = 3 * 4;
#         _i2 = 2 + i1;
#
# 3. The only allowed control flow constucts are the following two 
#    statements:
#
#        goto Label;
#        if (_variable) goto Label;
#
#        Label:
#           ... code ...
#
#    No, you don't get "else". And you also don't get code blocks 
#    enclosed in braces { }. 
#
# 4. You may print things with printf().
#
# That's it, those are the only C features you may use.  To help you
# out, Here's a small fragment of Wabbit code that executes a loop:
#
#    /* Sample Wabbit Code */
#    /* Print the first 10 factorials */
#
#    var result = 1;
#    var n = 1;
#
#    while n <= 10 {
#        result = result * n;
#        print result;
#        n = n + 1;
#    }
#
# Here's what the corresponding C code might look like (it can vary
# as long as you object the general rules above):
#
#    #include <stdio.h>
#
#    int result;       
#    int n;
#
#    int main() {
#        int _i1;
#        int _i2;
#        int _i3;
#
#        result = 1;
#        n = 1;
#    L1:
#        _i1 = (n <= 10);
#        if (_i1) goto L2;
#        goto L3;
#    L2:
#        _i2 = result * n;
#        result = _i2;
#        printf("%i\n", result);
#        _i3 = n + 1;
#        n = _i3;
#        goto L1;
#    L3:
#        return 0;
#    }
#         
# One thing to keep in mind... the goal is NOT to produce code for
# humans to read.  Instead, it's to produce code that is minimal and
# which can be reasoned about. There is very little actually happening
# in the above code.  It has calculations and gotos. That is basically
# it.  There is no unseen high-level magic going on. What you see
# it what it is.

# Hints:
# ------
# In the interpreter, you wrote code that just "did the operation"
# right there.  You used Python as the runtime environment.  In the
# type-checker, you wrote code that merely "checked the operation" to
# see if there were any errors.  In this project, you have to do a bit
# of both.  For each object in your model, you're going to write a
# function that *creates* the code for carrying out the operation.
# This will be very similar to the interpreter.  However, in order to
# create this code, you've got to know a few things about types. So,
# that information has to be tracked as well.  In addition, there's
# going to be a bit of extra bookkeeping related to the environment.
# For instance, in the above example, extra "C variables" such as
# "_i1", "_i2" and "_i3" are created to hold temporary values.  You'll
# need to have some way to keep track of that.
#
# Also, one other thing... everything that happens here takes place
# *after* type-checking.  Therefore, you don't need to focus on
# problem related to incorrect programs. Assume that all programs
# are fully correct with respect to their usage of types and names.

import os.path
import sys

from .model import *
from .parse import parse


class TypeVisitor:
    typemap = {
        int: int,
        float: float,
        bool: bool,
        str: str,
    }

    def __init__(self, node):
        self.types = {}
        self.visit(node)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.types})'

    def __iter__(self):
        return iter(self.types.values())

    def set(self, node, type):
        if type is not None:
            type = self.typemap.get(type, type)
            self.types[id(node)] = (node, type)

    def get(self, node):
        return self.types.get(id(node), (None, None))[1]

    def visit(self, node):
        m = getattr(self, f'visit_{node.__class__.__name__}')
        m(node)

    def visit_Block(self, node):
        type = None
        for n in node.statements:
            self.visit(n)

            # first return wins?
            if type is None and isinstance(n, Return):
                type = self.get(n)

        # otherwise, type of last statement
        if type is None:
            type = self.get(n)

        self.set(node, type)

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)

        type = ltype = self.get(node.left)
        rtype = self.get(node.right)
        assert ltype == rtype

        if node.op in ('||', '&&'):
            type = bool

        self.set(node, type)

    def visit_Integer(self, node):
        self.set(node, int)

    def visit_Float(self, node):
        self.set(node, float)

    def visit_Char(self, node):
        self.set(node, str)

    def visit_Bool(self, node):
        self.set(node, bool)

    def visit_Print(self, node):
        self.visit(node.arg)

class CTypeVisitor(TypeVisitor):
    typemap = {
        int: 'int',
        float: 'double',
        str: 'char',
        bool: 'bool'
    }

class CCompilerVisitor:

    def var(self, node):
        return f'v{node.__class__.__name__}_{hex(id(node))[2:]}'

    def get(self, node):
        # get type
        return self.types.get(node)

    def compile_c(self, node):
        self.types = CTypeVisitor(node)
        variables = ''.join(f'{t} {self.var(n)};\n' for n, t in self.types)
        code = self.visit(node)
        return '#include <stdio.h>\n#include <stdbool.h>\nint main() {\n' + variables + code + '\nreturn 0;\n}'

    def visit(self, node):
        m = getattr(self, f'visit_{node.__class__.__name__}')
        return m(node)

    def visit_Block(self, node):
        s = ''
        for n in node.statements:
            s += self.visit(n)
        return s

    def visit_BinOp(self, node):
        return f'''
{self.var(node.left)} = {self.visit(node.left)};
{self.var(node.right)} = {self.visit(node.right)};
{self.var(node)} = {self.var(node.left)} {node.op} {self.var(node.right)};
'''

    def visit_Integer(self, node):
        return str(node.value)

    def visit_Print(self, node):
        s = self.visit(node.arg)

        type = self.get(node.arg)
        format = {
            'int': '%d',
            'double': '%f',
            'char': '%c',
            'bool': '%d',
        }[type]

        s += f'printf("{format}", {self.var(node.arg)});'

        return s

def compile_c(text_or_node):
    node = text_or_node
    if not isinstance(text_or_node, Node):
        node = parse(text_or_node)
    return CCompilerVisitor().compile_c(node)

def main(args):
    if args:
        if os.path.isfile(args[0]):
            with open(args[0]) as file:
                text = file.read()

            output = compile_c(text)
            with open(args[0] + '.c', 'w') as f:
                f.write(output)
        else:
            text = args[0]
            print(compile_c(text))
    else:
        text = sys.stdin.read()
        print(compile_ch(text))

if __name__ == '__main__':
    main(sys.argv[1:])
