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

class Scalar:
    '''
    Example: 42
    '''
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return self.__class__.__name__ + '(' + str(self.value) + ')'

    def to_source(self):
        return repr(self.value)


class Integer(Scalar):
    '''
    Example: 42
    '''
    pass


class Float(Scalar):
    '''
    Example: 42.0
    '''
    pass

class Var:
    '''
    Example: foo
    '''
    def __init__(self, identifier):
        self.identifier = identifier

    def __repr__(self):
        return self.identifier

    def to_source(self):
        return self.identifier

class VarDecl:
    '''
    Example: var foo int
    '''
    def __init__(self, identifier, _type, expr=None, const=False):
        self.identifier = identifier
        self.type = _type
        self.const = const
        self.expr = expr

    def __repr__(self):
        return f'VarDecl({self.identifier}, {self.type or "None"}, {to_source(self.expr) or None}, {"const" if self.const else "var"}) '

    def to_source(self):
        return f'var {self.identifier} {self.type}'

    def to_source(self):
        ret = 'const' if self.const else 'var'
        ret += ' ' + self.identifier
        if self.type:
            ret += ' ' + self.type
        if self.expr:
            ret += ' = ' + to_source(self.expr)
        return ret


class VarAssign:
    '''
    Example: foo = EXPR
    '''
    def __init__(self, identifier, expr):
        self.identifier = identifier
        self.expr = expr

    def __repr__(self):
        return f'VarAssign({self.identifier}, {self.expr})'

    def to_source(self):
        return f'{self.identifier} = {to_source(self.expr)}'


class BinOp:
    '''
    Example: left + right
    '''
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f'BinOp({self.op}, {self.left}, {self.right})'

    def to_source(self):
        return f'{self.left.to_source()} {self.op} {self.right.to_source()}'

class UnOp:
    '''
    Example: -right
    '''
    def __init__(self, op, right):
        self.op = op
        self.right = right

    def __repr__(self):
        return f'UnOp({self.op}, {self.right})'

    def to_source(self):
        return f'{self.op}{self.right.to_source()}'

class Print:
    '''
    Example: print(EXPR)
    '''
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f'Print({self.expr})'

    def to_source(self):
        return f'print {to_source(self.expr)}'

# ------ Debugging function to convert a model into source code (for easier viewing)

def to_source(node):
    if isinstance(node, list):
        return ";\n".join(to_source(n) for n in node) + ";\n"
    elif node is None:
        return "None"
    else:
        return node.to_source()
