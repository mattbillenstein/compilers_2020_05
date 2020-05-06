# interp.py
#
# In order to write a compiler for a programming language, it helps to
# have some kind of specification of how programs written in the
# programming language are actually supposed to work. A language is
# more than just "syntax" or a data model.  There has to be some kind
# of operational semantics that describe what happens when a program
# runs.
#
# One way to specify the operational semantics is to write a so-called
# "definitional interpreter" that directly executes the data
# model. This might seem like cheating--after all, our final goal is
# not to write an interpreter, but a compiler. However, if you can't
# write an interpreter, chances are you can't write a compiler either.
# So, the purpose of doing this is to pin down fine details as well as
# our overall understanding of what needs to happen when programs run.
#
# We'll write our interpreter in Python.  The idea is relatively 
# straightforward.  For each class in the model.py file, you're
# going to write a function similar to this:
#
#    def interpret_node_name(node, env):
#        # Execute "node" in the environment "env"
#        ...
#        return result
#   
# The input to the function will be an object from model.py (node)
# along with an object respresenting the execution environment (env).
# The function will then execute the node in the environment and return
# a result.  It might also modify the environment (for example,
# when executing assignment statements, variable definitions, etc.). 
#
# For the purposes of this projrect, assume that all programs provided
# as input are "sound"--meaning that there are no programming errors
# in the input.  Our purpose is not to create a "production grade"
# interpreter.  We're just trying to understand how things actually
# work when a program runs. 
#
# For testing, try running your interpreter on the models you
# created in the example_models.py file.
#

from collections import ChainMap

from .model import *

class DeepChainMap(ChainMap):
    'Variant of ChainMap that allows direct updates to inner scopes'

    def __setitem__(self, key, value):
        for mapping in self.maps:
            if key in mapping:
                mapping[key] = value
                return
        self.maps[0][key] = value

    def __delitem__(self, key):
        for mapping in self.maps:
            if key in mapping:
                del mapping[key]
                return
        raise KeyError(key)

d = DeepChainMap()

# Top level function that interprets an entire program. It creates the
# initial environment that's used for storing variables.

# TODO
# - Program node, so Block doesn't need to return
# - Scope only if var/const in a block?
# - look at scoping more - make sure we set things in the proper scope

def interpret(node):
    return Interpreter().interpret(node)


class Interpreter:
    def __init__(self):
        self.env = None
        self.stdout = []

    def interpret(self, node):
        x = self.visit(node)

        if isinstance(self.env.get('main'), Func):
            x = self.visit(self.env['main'].block)

        assert self.env is not None and len(self.env.maps) == 1
        return x, self.env.maps[0], self.stdout

    def visit(self, node):
        assert node is not None
        m = getattr(self, f'visit_{node.__class__.__name__}')
        return m(node)

    def _new_scope(self):
        # push new scope, hack if this is the first block to not add an extra
        # scope...
        if self.env is None:
            self.env = DeepChainMap()
        else:
            self.env = self.env.new_child()

    def _del_scope(self):
        if len(self.env.maps) > 1:
            self.env = self.env.parents

    def visit_Name(self, node):
        return self.env.get(node.value)

    def visit_Attribute(self, node):
        return f'{self.visit(node.name)}.{self.visit(node.attr)}'

    def visit_Type(self, node):
        return {
            'int': int,
            'float': float,
        }[node.type]

    def visit_Integer(self, node):
        return node.value

    def visit_Float(self, node):
        return node.value

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        x =  {
            '+': lambda a, b: a+b,
            '-': lambda a, b: a-b,
            '*': lambda a, b: a*b,
            '/': lambda a, b: a/b,
            '<': lambda a, b: a<b,
            '>': lambda a, b: a>b,
            '<=': lambda a, b: a<=b,
            '>=': lambda a, b: a>=b,
            '!=': lambda a, b: a!=b,
            '==': lambda a, b: a==b,
        }[node.op](left, right)
        return x

    def visit_UnaOp(self, node):
        return {
            '-': lambda a: -a,
            '+': lambda a: a,
            '!': lambda a: not a,
        }[node.op](self.visit(node.arg))

    def visit_Block(self, node):
        self._new_scope()

        ret = None
        for n in node.statements:
            ret = self.visit(n)
            if isinstance(n, Return):
                self._del_scope()
                return ret

        self._del_scope()

        # hmm, should a block actually return something? See Compound
        return ret

    def visit_Compound(self, node):
        # same as Block almost...
        return self.visit_Block(node)

    def visit_Print(self, node):
        self.stdout.append(self.visit(node.arg))

    def visit_Const(self, node):
        name = node.name.value
        # set in the current scope
        self.env.maps[0][name] = v = self.visit(node.arg)
        if node.type is not None:
            t = self.visit(node.type)
            assert isinstance(v, t), (v, t)

    def visit_Var(self, node):
        name = node.name.value
        arg = self.visit(node.arg) if node.arg is not None else None
        typ = self.visit(node.type) if node.type is not None else None

        if arg is not None and typ is not None:
            assert isinstance(arg, typ)

        if arg is None and typ is not None:
            arg = typ()

        # set in the current scope
        self.env.maps[0][name] = arg

    def visit_Assign(self, node):
        name = node.name.value
        arg = self.visit(node.arg)
        # FIXME, protect const?
        self.env[name] = arg

    def visit_If(self, node):
        if self.visit(node.cond):
            return self.visit(node.block)
        elif node.eblock is not None:
            return self.visit(node.eblock)

    def visit_While(self, node):
        while self.visit(node.cond):
            ret = self.visit(node.block)
        return ret

    def visit_Func(self, node):
        # store the function block
        self.env[node.name.value] = node

    def visit_Arg(self, node):
        # arg of a function call
        duh
        return f'{self.visit(node.name)} {self.visit(node.type)}'

    def visit_Field(self, node):
        return node.name.value, self.visit(node.type)

    def visit_Return(self, node):
        return self.visit(node.value)

    def visit_Call(self, node):
        func = self.env[node.name.value]

        if isinstance(func, Struct):
            # just return a dict with the fields and the default of the type
            d = {}
            for n in func.fields:
                name, typ = self.visit(n)
                d[name] = typ()
            return d

        self._new_scope()

        # insert all call arguments into the new scope
        for farg, arg in zip(func.args, node.args):
            self.env.maps[0][farg.name.value] = v = self.visit(arg)

        x = self.visit(func.block)

        self._del_scope()

        return x

    def visit_Struct(self, node):
        # just store this model in the env, we'll use it later to create
        # instances...
        self.env[node.name.value] = node

    def visit_Enum(self, node):
        duh
        args = '    ' + ';\n    '.join(self.visit(_) for _ in node.args) + ';\n'
        return f'enum {self.visit(node.name)} {{\n{args}}}\n'

    def visit_Member(self, node):
        duh
        type = f'({self.visit(node.type)})' if node.type else ''
        return f'{self.visit(node.name)}{type}'
