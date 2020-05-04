# model.py
#
# This file defines the data model for Wabbit programs.  The data
# model is a data structure that represents the contents of a program
# as objects, not text.  Sometimes this structure is known as an
# "abstract syntax tree" or AST.  However, the model is not
# necessarily directly tied to the actual syntax of the language.  So,
# we'll prefer to think of it as a more generic data model instead.
#
# To do this, you need to identify the different "elements" that make
# up a program and encode them into classes.  To do this, it may be
# useful to slightly "underthink" the problem. To illustrate, suppose
# you wanted to encode the idea of "assigning a value."  Assignment
# involves a location (the left hand side) and a value like this:
#
#         location = expression;
#
# To represent this idea, make a class with just those parts:
#
#     class Assignment:
#         def __init__(self, location, expression):
#             self.location = location
#             self.expression = expression
#
# What are "location" and "expression"?  Does it matter? Maybe
# not. All you know is that an assignment operator definitely requires
# both of those parts.  DON'T OVERTHINK IT.  Further details will be
# filled in as the project evolves.
# 
# Work on this file in conjunction with the top-level
# "script_models.py" file.  Go look at that file and see what program
# samples are provided.  Then, figure out what those programs look like 
# in terms of data structures.
#
# There is no "right" solution to this part of the project other than
# the fact that a program has to be represented as some kind of data
# structure that's not "text."   You could use classes. You could use 
# tuples. You could make a bunch of nested dictionaries like JSON. 
# The key point: it must be a data structure.
#
# Starting out, I'd advise against making this file too fancy. Just
# use basic data structures. You can add usability enhancements later.
# -----------------------------------------------------------------------------

# The following classes are used for the expression example in script_models.py.
# Feel free to modify as appropriate.  You don't even have to use classes
# if you want to go in a different direction with it.

NoneType = type(None)

class Node:
    is_statement = False

class Integer(Node):
    '''
    Example: 42
    '''
    def __init__(self, value):
        assert isinstance(value, int)
        self.value = value

    def __repr__(self):
        return f'Integer({self.value})'

    def to_source(self):
        return f'{self.value}'

class Float(Node):
    '''
    Example: 42.0
    '''
    def __init__(self, value):
        assert isinstance(value, float)
        self.value = value

    def __repr__(self):
        return f'Float({self.value})'

    def to_source(self):
        return f'{self.value}'

class BinOp(Node):
    '''
    Example: left + right
    '''
    def __init__(self, op, left, right):
        assert op in ('+', '-', '/', '*', '<', '>', '<=', '>=', '!=', '==')
        assert isinstance(left, (Node, str))
        assert isinstance(right, (Node, str))
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f'BinOp({self.op}, {self.left}, {self.right})'

    def to_source(self):
        return f'{to_source(self.left)} {self.op} {to_source(self.right)}'

class UnaOp(Node):
    '''
    Example: left + right
    '''
    def __init__(self, op, arg):
        assert op in ('-',)
        assert isinstance(arg, (Node, str))
        self.op = op
        self.arg = arg

    def __repr__(self):
        return f'UnaOp({self.op}, {self.arg})'

    def to_source(self):
        return f'{self.op}{to_source(self.arg)}'

class Block(Node):
    '''
    List of statements

    stmt1;
    stmt2;
    stmt3;
    '''
    def __init__(self, statements, indent=''):
        assert isinstance(statements, list)
        assert indent == '' or set(indent) == {' '}
        self.statements = statements
        self.indent = indent

    def __repr__(self):
        return f'Block({[_ for _ in self.statements]}, indent={indent})'

    def to_source(self):
        L = []
        for stmt in self.statements:
            s = to_source(stmt) + ('' if not isinstance(stmt, Node) or stmt.is_statement else ';')
            # hack, split lines to add indent, then rejoin them...
            lines = [self.indent + _ for _ in s.split('\n') if _.strip()]
            s = '\n'.join(lines)
            L.append(s)
        return '\n'.join(L) + '\n'

class Print(Node):
    '''
    Print is kinda a special case of a function call - optional parens
    '''
    def __init__(self, arg):
        assert isinstance(arg, (Node, str))
        self.arg = arg

    def __repr__(self):
        return f'Print({self.arg})'

    def to_source(self):
        return f'print {to_source(self.arg)}'

class Const(Node):
    def __init__(self, loc, arg, type=None):
        assert isinstance(loc, str)
        assert isinstance(arg, (Node, str))
        assert isinstance(type, (str, NoneType))
        self.loc = loc
        self.arg = arg
        self.type = type

    def __repr__(self):
        type = f', type={self.type}' if self.type is not None else ''
        return f'Const({self.loc}, {self.arg}{type})'

    def to_source(self):
        type = f' {self.type}' if self.type is not None else ''
        return f'const {self.loc}{type} = {to_source(self.arg)}'

class Var(Node):
    def __init__(self, loc, arg=None, type=None):
        assert isinstance(loc, str)
        assert isinstance(arg, (Node, str, NoneType))
        assert isinstance(type, (str, NoneType))
        self.loc = loc
        self.arg = arg
        self.type = type

    def __repr__(self):
        arg = f', {self.arg}' if self.arg is not None else ''
        type = f', type={self.type}' if self.type is not None else ''
        return f'Var({self.loc}{self.arg}{self.type})'

    def to_source(self):
        arg = f' = {to_source(self.arg)}' if self.arg is not None else ''
        type = f' {self.type}' if self.type is not None else ''
        return f'var {self.loc}{type}{arg}'

class Assign(Node):
    def __init__(self, loc, arg):
        assert isinstance(loc, str)
        assert isinstance(arg, (Node, str))
        self.loc = loc
        self.arg = arg

    def __repr__(self):
        return f'Assign({self.loc}, {self.arg})'

    def to_source(self):
        return f'{self.loc} = {to_source(self.arg)}'

class If(Node):
    is_statement = True

    def __init__(self, cond, block, eblock=None):
        assert isinstance(cond, (Node, str))
        assert isinstance(block, Block)
        assert isinstance(eblock, (Block, NoneType))
        self.cond = cond
        self.block = block
        self.eblock = eblock

    def __repr__(self):
        els = f', {self.eblock}' if self.eblock is not None else ''
        return f'If({self.cond}, {self.block}{els})'

    def to_source(self):
        els = f' else {{\n{to_source(self.eblock)}}}' if self.eblock is not None else ''
        return f'if {to_source(self.cond)} {{\n{to_source(self.block)}}}{els}'

class While(Node):
    is_statement = True

    def __init__(self, cond, block):
        assert isinstance(cond, (Node, str))
        assert isinstance(block, Block)
        self.cond = cond
        self.block = block

    def __repr__(self):
        return f'While({self.cond}, {self.block})'

    def to_source(self):
        return f'while {to_source(self.cond)} {{\n{to_source(self.block)}}}'

class Compound(Node):
    def __init__(self, statements):
        assert isinstance(statements, list)
        assert all(isinstance(_, (Node, str)) for _ in statements)
        self.statements = statements

    def __repr__(self):
        return f'Compound({[_ for _ in self.statements]})'

    def to_source(self):
        s = '; '.join(to_source(_) for _ in self.statements) + ';'
        return f'{{ {s} }}'

# ------ Debugging function to convert a model into source code (for easier viewing)

def to_source(node):
    if isinstance(node, Node):
        return node.to_source()
    return str(node)
