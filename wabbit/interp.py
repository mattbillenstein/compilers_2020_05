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

import os.path
import sys
from collections import ChainMap
from functools import wraps

from .model import *
from .parse import parse

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

def new_scope(func):
    '''Call function with new scope, remove it after the function exits'''
    def inner(*args, **kwargs):
        self = args[0]
        try:
            if self.env is None:
                self.env = DeepChainMap()
            else:
                self.env = self.env.new_child()

            return func(*args, **kwargs)
        finally:
            # don't remove the last scope since this is what we return to check
            # simple expressions
            if len(self.env.maps) > 1:
                self.env = self.env.parents

    return inner


class Interpreter:
    # TODO
    # - Program node, so Block doesn't need to return
    # - Scope only if var/const in a block?

    def __init__(self):
        self.env = None
        self.stdout = []

    def current_scope(self):
        return self.env.maps[0]

    def interpret(self, node):
        ret = self.visit(node)

        if isinstance(self.env.get('main'), Func):
            ret = self.visit(self.env['main'].block)

        assert self.env is not None and len(self.env.maps) == 1
        return ret, self.current_scope(), self.stdout

    def visit(self, node):
        assert node is not None
        m = getattr(self, f'visit_{node.__class__.__name__}')
        return m(node)

    def visit_Name(self, node):
        return self.env.get(node.value)

    def visit_Type(self, node):
        return {
            'int': int,
            'float': float,
        }[node.type]

    def visit_Integer(self, node):
        return node.value

    def visit_Float(self, node):
        return node.value

    def visit_Char(self, node):
        # only during execution, return the unescaped char
        return node.unescape()

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        assert type(left) == type(right), (left, right)

        if node.op == '/':
            if isinstance(left, int):
                # integer division
                return left // right
            return left / right

        return {
            '+': lambda a, b: a+b,
            '-': lambda a, b: a-b,
            '*': lambda a, b: a*b,
            '<': lambda a, b: a<b,
            '>': lambda a, b: a>b,
            '<=': lambda a, b: a<=b,
            '>=': lambda a, b: a>=b,
            '!=': lambda a, b: a!=b,
            '==': lambda a, b: a==b,
        }[node.op](left, right)

    def visit_UnaOp(self, node):
        return {
            '-': lambda a: -a,
            '+': lambda a: a,
            '!': lambda a: not a,
        }[node.op](self.visit(node.arg))

    @new_scope
    def visit_Block(self, node, args=None):
        if args:
            # called with args, insert them into the current scope
            self.current_scope().update(args)

        ret = None
        for n in node.statements:
            ret = self.visit(n)
            if isinstance(n, Return):
                break

        # hmm, should a block actually return something? See Compound
        return ret

    def visit_Compound(self, node):
        # same as Block almost...
        return self.visit_Block(node)

    def visit_Print(self, node):
        self.stdout.append(self.visit(node.arg))

    def visit_Const(self, node):
        name = node.name.value
        self.current_scope()[name] = v = self.visit(node.arg)

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
        self.current_scope()[name] = arg

    def visit_Assign(self, node):
        # FIXME, protect const somehow?
        arg = self.visit(node.arg)

        if isinstance(node.name, Name):
            name = node.name.value
            self.env[name] = arg
            return

        # Attribute - recursively lookup the dict to set the value in...
        attr = node.name
        env = self.resolve_Attribute(attr.name)
        env[attr.attr] = arg

    def resolve_Attribute(self, node):
        if isinstance(node, Name):
            # we're updating an existing struct, so we don't need
            # current_scope() here - update it in whatever scope it lives in...
            return self.env[node.value]
        return self.resolve_Attribute(node.name)[node.attr]

    def visit_If(self, node):
        if self.visit(node.cond):
            return self.visit(node.block)
        elif node.eblock is not None:
            return self.visit(node.eblock)

    def visit_While(self, node):
        while self.visit(node.cond):
            self.visit(node.block)

    def visit_Func(self, node):
        # just store the function node into the current scope, see Call for
        # calling...
        self.env[node.name.value] = node

    def visit_Return(self, node):
        return self.visit(node.value)

    def visit_Call(self, node):
        func = self.env[node.name.value]

        if isinstance(func, Struct):
            struct = func
            # visit args and put them into a dict for this instance of the
            # struct...
            assert len(struct.fields) == len(node.args)

            # hack, revisit the type of this...
            values = {}
            for field, arg in zip(struct.fields, node.args):
                values[field.name.value] = self.visit(arg)
            return values

        # visit args and put them into a scope
        assert len(func.args) == len(node.args)
        args = {}
        for farg, arg in zip(func.args, node.args):
            args[farg.name.value] = self.visit(arg)

        # visit block, args get injected into the block scope there
        return self.visit_Block(func.block, args)

    def visit_Struct(self, node):
        # just store this model in the env, we'll use it later to create
        # instances...
        self.env[node.name.value] = node

    def visit_Field(self, node):
        return node.name.value, self.visit(node.name)

    def visit_Attribute(self, node):
        obj = self.visit(node.name)
        attr = node.attr
        if isinstance(obj, dict):
            return obj[attr]
        return getattr(obj, attr)

    # TODO: enum stuff

    def visit_Enum(self, node):
        duh
        args = '    ' + ';\n    '.join(self.visit(_) for _ in node.args) + ';\n'
        return f'enum {self.visit(node.name)} {{\n{args}}}\n'

    def visit_Member(self, node):
        duh
        type = f'({self.visit(node.type)})' if node.type else ''
        return f'{self.visit(node.name)}{type}'


def interpret(text_or_node):
    node = text_or_node
    if not isinstance(text_or_node, Node):
        node = parse(text_or_node)
    return Interpreter().interpret(node)

def main(args):
    if args:
        if os.path.isfile(args[0]):
            with open(args[0]) as file:
                text = file.read()
        else:
            text = args[0]
    else:
        text = sys.stdin.read()

    ret, env, stdout = interpret(text)
    for s in stdout:
        sys.stdout.write(s)


if __name__ == '__main__':
    main(sys.argv[1:])
