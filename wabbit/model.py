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
    _var = ''
    _type = None

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

class Name(Node):
    def __init__(self, value):
        assert isinstance(value, str)
        self.value = value

    def __repr__(self):
        return f'Name({self.value})'

class Type(Node):
    def __init__(self, type):
        assert isinstance(type, str)
        self.type = type

    def __repr__(self):
        return f'Type({self.type})'

class Char(Node):
    def __init__(self, value):
        assert isinstance(value, str)
        self.value = value

    def unescape(self):
        return self.value.encode('utf8').decode('unicode_escape')

    def __repr__(self):
        return f"Char('{self.value}')"

class Integer(Node):
    '''
    Example: 42
    '''
    def __init__(self, value):
        assert isinstance(value, int)
        self.value = value

    def __repr__(self):
        return f'Integer({self.value})'

class Float(Node):
    '''
    Example: 42.0
    '''
    def __init__(self, value):
        assert isinstance(value, float)
        self.value = value

    def __repr__(self):
        return f'Float({self.value})'

class Bool(Node):
    def __init__(self, value):
        assert isinstance(value, bool)
        self.value = value

    def __repr__(self):
        return f'Bool({self.value})'

class Break(Node):
    def __repr__(self):
        return f'Break()'

class Continue(Node):
    def __repr__(self):
        return f'Continue()'

class BinOp(Node):
    '''
    Example: left + right
    '''
    def __init__(self, op, left, right):
        assert op in ('+', '-', '/', '*', '<', '>', '<=', '>=', '!=', '==', '&&', '||'), op
        assert isinstance(left, Node)
        assert isinstance(right, Node)
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f'BinOp({self.op}, {self.left}, {self.right})'

class UnaOp(Node):
    '''
    Example: left + right
    '''
    def __init__(self, op, arg):
        assert op in ('-', '+', '!')
        assert isinstance(arg, Node)
        self.op = op
        self.arg = arg

    def __repr__(self):
        return f'UnaOp({self.op}, {self.arg})'

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
        indent = f", indent='{self.indent}'" if self.indent else ''
        return f'Block({[_ for _ in self.statements]}{indent})'

    def __eq__(self, other):
        return dict(self.__dict__, **{'indent': ''}) == dict(other.__dict__, **{'indent': ''})

class Print(Node):
    '''
    Print is kinda a special case of a function call - optional parens
    '''
    def __init__(self, arg):
        assert isinstance(arg, Node)
        self.arg = arg

    def __repr__(self):
        return f'Print({self.arg})'

class Const(Node):
    def __init__(self, name, arg, type=None):
        assert isinstance(name, Name)
        assert isinstance(arg, Node)
        assert isinstance(type, (Type, NoneType))
        self.name = name
        self.arg = arg
        self.type = type

    def __repr__(self):
        type = f', type={self.type}' if self.type is not None else ''
        return f'Const({self.name}, {self.arg}{type})'

class Var(Node):
    def __init__(self, name, arg=None, type=None):
        assert isinstance(name, Name)
        assert isinstance(arg, (Node, NoneType))
        assert isinstance(type, (Type, NoneType))
        assert arg is not None or type is not None
        self.name = name
        self.arg = arg
        self.type = type

    def __repr__(self):
        arg = f', {self.arg}' if self.arg is not None else ''
        type = f', type={self.type}' if self.type is not None else ''
        return f'Var({self.name}{arg}{type})'

class Assign(Node):
    def __init__(self, name, arg):
        assert isinstance(name, (Name, Attribute))
        assert isinstance(arg, Node)
        self.name = name
        self.arg = arg

    def __repr__(self):
        return f'Assign({self.name}, {self.arg})'

class If(Node):
    is_statement = True

    def __init__(self, cond, block, eblock=None):
        assert isinstance(cond, Node)
        assert isinstance(block, Block)
        assert isinstance(eblock, (Block, NoneType))
        self.cond = cond
        self.block = block
        self.eblock = eblock

    def __repr__(self):
        els = f', {self.eblock}' if self.eblock is not None else ''
        return f'If({self.cond}, {self.block}{els})'

class While(Node):
    is_statement = True

    def __init__(self, cond, block):
        assert isinstance(cond, Node)
        assert isinstance(block, Block)
        self.cond = cond
        self.block = block

    def __repr__(self):
        return f'While({self.cond}, {self.block})'

class Compound(Node):
    def __init__(self, statements):
        assert isinstance(statements, list)
        assert all(isinstance(_, Node) for _ in statements)
        self.statements = statements

    def __repr__(self):
        return f'Compound({self.statements})'

class Func(Node):
    is_statement = True

    def __init__(self, name, block, args=None, ret_type=None):
        assert isinstance(name, Name)
        assert isinstance(block, Block)
        args = args or []
        assert isinstance(args, list)
        assert all(isinstance(_, Node) for _ in args)
        assert isinstance(ret_type, (Type, NoneType))
        self.name = name
        self.args = args
        self.ret_type = ret_type
        self.block = block

    def __repr__(self):
        args = (', '+ repr(self.args)) if self.args else ''
        ret_type = (', ' + self.ret_type.type) if self.ret_type is not None else ''
        return f'Func({self.name}, {self.block}{args}{ret_type})'

class Return(Node):
    def __init__(self, value):
        assert isinstance(value, Node)
        self.value = value

    def __repr__(self):
        return f'Return({self.value})'

class ArgDef(Node):
    '''arg definition in a function definition'''
    def __init__(self, name, type):
        assert isinstance(name, Name)
        assert isinstance(type, Type)
        self.name = name
        self.type = type

    def __repr__(self):
        return f'ArgDef({self.name}, {self.type})'

class Field(Node):
    '''field of a function struct'''
    def __init__(self, name, type):
        assert isinstance(name, Name)
        assert isinstance(type, Type)
        self.name = name
        self.type = type

    def __repr__(self):
        return f'Field({self.name}, {self.type})'

class Call(Node):
    def __init__(self, name, args):
        assert isinstance(name, Name)
        args = args or []
        assert isinstance(args, list)
        assert all(isinstance(_, Node) for _ in args)
        self.name = name
        self.args = args

    def __repr__(self):
        args = (', ' + repr(self.args)) if self.args else ''
        return f'Call({self.name}{args})'

class Struct(Node):
    is_statement = True

    def __init__(self, name, fields):
        assert isinstance(name, Name)
        assert isinstance(fields, list)
        assert all(isinstance(_, Field) for _ in fields)
        assert len(fields) > 0
        self.name = name
        self.fields = fields

    def __repr__(self):
        return f'Struct({self.name}, {self.fields})'

class Enum(Node):
    is_statement = True

    def __init__(self, name, args):
        assert isinstance(name, Name)
        assert isinstance(args, list)
        assert all(isinstance(_, Node) for _ in args)
        assert len(args) > 0
        self.name = name
        self.args = args

    def __repr__(self):
        return f'Enum({self.name}, {self.args})'

class Member(Node):
    '''member of an enum definition'''
    def __init__(self, name, type=None):
        assert isinstance(name, Name)
        assert isinstance(type, (Type, NoneType))
        self.name = name
        self.type = type

    def __repr__(self):
        type = f', {self.type}' if self.type is not None else ''
        return f'Member({self.name}{type})'

class Attribute(Node):
    def __init__(self, name, attr):
        assert isinstance(name, (Name, Attribute))
        assert isinstance(attr, str)
        self.name = name
        self.attr = attr

    def __repr__(self):
        return f'Attribute({self.name}, {self.attr})'

class Unit(Node):
    def __repr__(self):
        return f'Unit()'

    def __str__(self):
        return '()'

UNIT = Unit()


def compare_model(m1, m2):
    if m1 != m2:
        print(m1)
        print()
        print(m2)
        raise ValueError('Mismatched Models')
