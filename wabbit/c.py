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
from .scope import *

NOOP = '(void)0;\n'

class TypeVisitor:
    def __init__(self, node):
        self.env = Scopes()
#        self.nodes = []
        self.var_ids = {}

        self.visit(node)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.types})'

    def var(self, node):
        name = node.__class__.__name__
        if isinstance(node, Name):
            name += '_' + node.value
        elif hasattr(node, 'name'):
            name += '_' + node.name.value

        i = self.var_ids.get(id(node))
        if i is None:
            self.var_ids[id(node)] = i = len(self.var_ids)

        return f'{name}_{i}'

    def visit(self, node):
        node._var = self.var(node)
#        if not isinstance(node, (Name, Type)):
#            self.nodes.append(node)
        m = getattr(self, f'visit_{node.__class__.__name__}')
        m(node)
#        print('VISIT', node, node._var, node._type, file=sys.stderr)

    @new_scope()
    def visit_Block(self, node):
        for n in node.statements:
            self.visit(n)

    @new_scope()
    def visit_Compound(self, node):
        for n in node.statements:
            self.visit(n)
        node._type = n._type

    def visit_Return(self, node):
        self.visit(node.value)

    def visit_UnaOp(self, node):
        self.visit(node.arg)
        node._type = node.arg._type
        if node.op == '!':
            node._type = 'bool'

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)

        assert node.left._type == node.right._type, (node, node.left._type, node.right._type)

        node._type = node.left._type
        if node.op not in ('+', '-', '*', '/'):
            node._type = 'bool'

    def visit_Integer(self, node):
        node._type = 'int'

    def visit_Float(self, node):
        node._type = 'float'

    def visit_Char(self, node):
        node._type = 'char'

    def visit_Bool(self, node):
        node._type = 'bool'

    def visit_Print(self, node):
#        print(node, node.arg, file=sys.stderr)
        self.visit(node.arg)

    def set_Name(self, node, type):
        node._var = self.var(node)
        node._type = type
#        print('SET_NAME', node, type, node._var, file=sys.stderr)
        self.env.define(node.value, node)
#        self.nodes.append(node)

    def visit_Var(self, node):
        # name, arg, type
        if node.arg:
            self.visit(node.arg)
            type = node.arg._type
        elif node.type:
            type = node.type.type

        self.set_Name(node.name, type)

    def visit_Const(self, node):
        # name, arg, type
        self.visit(node.arg)
        type = node.arg._type
        if node.type:
            assert node.type.type == type

        self.set_Name(node.name, type)

    def visit_Name(self, node):
        # take the var name and type from the var/const node
        n = self.env[node.value]
#        print(node, n, n._var, n._type, file=sys.stderr)
        node._var, node._type = n._var, n._type

    def visit_Assign(self, node):
        self.visit(node.arg)

        if isinstance(node.name, Name):
            # visit to populate from env
            self.visit(node.name)
            return

        # Attribute - recursively lookup the dict to set the value in...
        attr = node.name
        env = self.resolve_Attribute(attr.name)
        env[attr.attr] = arg._type

    def resolve_Attribute(self, node):
        if isinstance(node, Name):
            # we're updating an existing struct, so we don't need
            # current_scope here - update it in whatever scope it lives in...
            return self.env[node.value]
        return self.resolve_Attribute(node.name)[node.attr]

    def visit_If(self, node):
        self.visit(node.cond)
        node._type = node.cond._type
        self.visit(node.block)
        if node.eblock:
            self.visit(node.eblock)

    def visit_While(self, node):
        self.visit(node.cond)
        node._type = node.cond._type
        self.visit(node.block)

    @new_scope(CallScope)
    def visit_Func(self, node):
        # put the function in the global scope
        self.env.global_scope[node.name.value] = node

        # put the args in the local scope
        for arg in node.args:
            self.set_Name(arg.name, arg.type.type)

        # visit the block
        self.visit(node.block)

    def visit_Call(self, node):
        func = self.env.global_scope[node.name.value]

        assert isinstance(func, Func)
        if isinstance(func, Struct):
            duh

        if func.ret_type:
            node._type = func.ret_type.type

        # visit args and check types
        assert len(func.args) == len(node.args)
        args = {}
        for farg, arg in zip(func.args, node.args):
            self.visit(arg)
            assert farg.type.type == arg._type

    def visit_Break(self, node):
        pass

    def visit_Continue(self, node):
        pass

class CCompilerVisitor:
    # wabbit -> C types
    typemap = {
        'int': 'int',
        'float': 'double',
        'bool': 'bool',
        'char': 'char',
        None: 'void*',
    }

    def compile_c(self, node):
        types = TypeVisitor(node)

        s = '#include <stdio.h>\n#include <stdbool.h>\n\n'

        # global vars / functions
        s += '// global variables\n'

        main = None
        for n in node.statements:
            # grab the program main if it exists
            if isinstance(n, Func) and n.name.value == 'main':
                assert main is None
                main = n
                n.name.value = '_main'  # hack, rename wabbit main

            s += self.define(n)

        s += '\nvoid _wabbit_init() {\n'

        for n in node.statements:
            s += self.visit(n)

        s += '}\n\n'

        s += f'''int main() {{
_wabbit_init();
{'_main();' if main else ''}
return 0;
}}
'''

        return s

    def visit(self, node):
        m = getattr(self, f'visit_{node.__class__.__name__}')
        return m(node)

    def visit_Block(self, node):
        s = ''
        for n in node.statements:
            s += self.visit(n)
        return s

    def visit_Compound(self, node):
        s = ''
        for n in node.statements:
            s += self.visit(n)

        # assign the last statement as the return value
        if n._type:
            s += f'{node._var} = {n._var};\n'

        return s

    def visit_UnaOp(self, node):
        s = self.visit(node.arg)
        return s + f'{node._var} = {node.op}{node.arg._var};\n'

    def visit_BinOp(self, node):
        s = self.visit(node.left)

        # shortcircuit ops
        if node.op in ('&&', '||'):
            invert = '!' if node.op == '&&' else ''
            s += f'{node._var} = {node.left._var};\n'
            s += f'if ({invert}{node._var}) goto {node._var}_End;\n'
            s += self.visit(node.right)
            s += f'{node._var} = {node.right._var};\n'
            s += f'{node._var}_End:\n'
            s += NOOP
        else:
            s += self.visit(node.right)
            s += f'{node._var} = {node.left._var} {node.op} {node.right._var};\n'

        return s

    def visit_Integer(self, node):
        return f'{node._var} = {node.value};\n';

    def visit_Float(self, node):
        return f'{node._var} = {node.value};\n';

    def visit_Char(self, node):
        return f'''{node._var} = '{node.value}';\n''';

    def visit_Bool(self, node):
        return f'{node._var} = {"true" if node.value else "false"};\n';

    def visit_Var(self, node):
        if node.arg is None:
            return ''
        s = self.visit(node.arg)
        return s + f'{node.name._var} = {node.arg._var};\n';

    def visit_Const(self, node):
        s = self.visit(node.arg)
        return s + f'{node.name._var} = {node.arg._var};\n';

    def visit_Print(self, node):
        s = self.visit(node.arg)

        if node.arg._type == 'bool':
            s += f'printf({node.arg._var} ? "true\\n": "false\\n");\n'
            return s

        format = {
            'int': '%d',
            'float': '%.6f',  # we emit double
            'char': '%c',
        }[node.arg._type]

        nl = ''
        if node.arg._type in ('int', 'float'):
            nl = '\\n'

        s += f'printf("{format}{nl}", {node.arg._var});\n'

        return s

    def visit_Assign(self, node):
        # would have been defined via var/const
        s = self.visit(node.arg)
        return s + f'{node.name._var} = {node.arg._var};\n';

    def visit_Name(self, node):
        return ''

    def visit_Func(self, node):
        return ''

    def visit_If(self, node):
        s =  self.visit(node.cond)
        s += f'if ({node.cond._var}) goto {node._var}_block;\n'
        if node.eblock:
            s += f'goto {node._var}_eblock;\n'
        else:
            s += f'goto {node._var}_End;\n'
        s += f'{node._var}_block:\n'
        s += self.visit(node.block)
        s += f'goto {node._var}_End;\n'
        if node.eblock:
            s += f'{node._var}_eblock:\n'
            s += self.visit(node.eblock)
        s += f'{node._var}_End:\n'
        s += NOOP
        return s

    def visit_While(self, node):
        self.current_while = node
        s = f'{node._var}:\n'
        s +=  self.visit(node.cond)
        s += f'if ({node.cond._var}) goto {node._var}_Start;\n'
        s += f'goto {node._var}_End;\n'
        s += f'{node._var}_Start:\n'
        s += self.visit(node.block)
        s += f'goto {node._var};\n'
        s += f'{node._var}_End:\n'
        s += NOOP
        self.current_while = None
        return s

    def visit_Return(self, node):
        s = self.visit(node.value)
        return s + f'return {node.value._var};\n'

    def visit_Call(self, node):
        s = ''
        for n in node.args:
            s += self.visit(n)

        args = ', '.join(n._var for n in node.args)

    
        # if node._type:  - some code assigns from functions which return unit...
        s += f'{node._var} = '

        return s + f'{node.name.value}({args});\n'

    def visit_Break(self, node):
        assert self.current_while
        return f'goto {self.current_while._var}_End;\n'

    def visit_Continue(self, node):
        assert self.current_while
        return f'goto {self.current_while._var};\n'

    #### definitions

    def define(self, node):
        m = getattr(self, f'define_{node.__class__.__name__}')
        return m(node)
    
    def define_Node(self, node):
        return f'{self.typemap[node._type]} {node._var};\n';

    def define_Integer(self, node):
        return self.define_Node(node)
    
    def define_Float(self, node):
        return self.define_Node(node)
    
    def define_Char(self, node):
        return self.define_Node(node)
    
    def define_Bool(self, node):
        return self.define_Node(node)
    
    def define_Name(self, node):
        return ''
#        return self.define_Node(node)

    def define_Var(self, node):
        s = self.define_Node(node.name)
        if node.arg:
            s += self.define(node.arg)
        return s

    def define_Const(self, node):
        s = self.define_Node(node.name)
        return s + self.define(node.arg)

    def define_Assign(self, node):
        s = self.define(node.arg)
        return s

    def define_UnaOp(self, node):
        s = self.define_Node(node)
        return s + self.define(node.arg)

    def define_BinOp(self, node):
        s = self.define(node.left)
        s += self.define(node.right)
        return s + self.define_Node(node)

    def define_Block(self, node):
        s = ''
        for n in node.statements:
            s += self.define(n)
        return s
            
    def define_Compound(self, node):
        s = self.define_Node(node)
        return s + self.define_Block(node)

    def define_Func(self, node):
        args = ', '.join(f'{self.typemap[n.type.type]} {n.name._var}' for n in node.args)
        ret_type = self.typemap[node.ret_type.type] if node.ret_type else 'void*'
        s = f'\n{ret_type} {node.name.value}({args}) {{\n'
        s += self.define(node.block)
        s += self.visit(node.block)
        s += '}\n\n'
        return s

    def define_Print(self, node):
        return self.define(node.arg)

    def define_Return(self, node):
        return self.define(node.value)

    def define_If(self, node):
        s = self.define(node.cond)
        s += self.define(node.block)
        if node.eblock:
            s += self.define(node.eblock)
        return s

    def define_While(self, node):
        s = self.define(node.cond)
        s += self.define(node.block)
        return s

    def define_Call(self, node):
        s = f'{self.typemap[node._type]} {node._var};\n'
        for arg in node.args:
            s += self.define(arg)
        return s

    def define_Break(self, node):
        return ''

    def define_Continue(self, node):
        return ''


def compile_c(text_or_node):
    node = text_or_node
    if not isinstance(text_or_node, Node):
        node = parse(text_or_node)
    return CCompilerVisitor().compile_c(node)

def cc(text_or_node, filename):
    code = compile_c(text_or_node)
    with open(filename, 'w') as f:
        f.write(code)
    ret = os.system(f'clang {filename} -o {filename.replace(".c", "")}')
    assert ret == 0, ret

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
        print(compile_c(text))

if __name__ == '__main__':
    main(sys.argv[1:])
