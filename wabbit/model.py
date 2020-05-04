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


from typing import List


class Node():
    pass


class ExpressionNode(Node):
    pass


class StatementNode(Node):
    pass


class Identifier(Node):
    pass


class Location(ExpressionNode):
    '''
    Example: foo.  This resolves to a place in memory at runtime
    '''
    def __init__(self, identifier: Identifier):
        self.identifier = identifier

    def __repr__(self):
        return self.identifier

    def to_source(self):
        return self.identifier


class DeclLocation(Location):
    '''
    Example: var foo int
    '''
    def __init__(self, identifier: Identifier, _type, const=False):
        self.identifier = identifier
        self._type = _type
        self.const = const

    def __repr__(self):
        return f'DeclLocation({self.identifier}, {str(self._type) or "None"}, {"True" if self.const else "False"}) '

    def to_source(self):
        ret = 'const' if self.const else 'var'
        ret += ' ' + self.identifier
        if self._type:
            ret += ' ' + str(self._type)
        return ret


class ScalarNode(ExpressionNode):
    '''
    Example: 42
    '''

    def __repr__(self):
        return self.__class__.__name__ + '(' + str(self.value) + ')'

    def to_source(self):
        return repr(self.value)


class Int(ScalarNode):
    '''
    Example: 42
    '''
    def __init__(self, value: int):
        self.value = value


class Float(ScalarNode):
    '''
    Example: 42.0
    '''
    def __init__(self, value: float):
        self.value = value


class AssignStatement(StatementNode):
    '''
    Example: foo = EXPR
    '''
    def __init__(self, location: Location, expr: ExpressionNode):
        self.location = location
        self.expr = expr

    def __repr__(self):
        return f'Assign({self.location}, {self.expr})'

    def to_source(self):
        return f'{self.location.to_source()} = {self.expr.to_source()};'


class BinOp(ExpressionNode):
    '''
    Example: left + right
    '''
    def __init__(self, op, left: ExpressionNode, right: ExpressionNode):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f'BinOp({self.op}, {self.left}, {self.right})'

    def to_source(self):
        return f'{self.left.to_source()} {self.op} {self.right.to_source()}'


class UnOp(ExpressionNode):
    '''
    Example: -right
    '''
    def __init__(self, op, right: ExpressionNode):
        self.op = op
        self.right = right

    def __repr__(self):
        return f'UnOp({self.op}, {self.right})'

    def to_source(self):
        return f'{self.op}{self.right.to_source()}'


class PrintStatement(StatementNode):
    '''
    Example: print(EXPR)
    '''
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f'Print({self.expr})'

    def to_source(self):
        return f'print {to_source(self.expr)};'


class ConditionalStatement(StatementNode):
    '''
    Example: 
    if EXPR {
        BLOCK
    } else {
        BLOCK
    }
    '''

    def __init__(self, cond: ExpressionNode, blockT: List[StatementNode], blockF: List[StatementNode]):
        self.cond = cond
        self.blockT = blockT
        self.blockF = blockF

    def __repr__(self):
        ret = f'ConditionalStatement({{self.cond.to_source()}},' 
        ret += '[' + to_source(self.blockT) + '], '
        ret += '[' + to_source(self.blockF) + '])'
        return ret

    def to_source(self):
        ret = 'if ' + self.cond.to_source() + ' {\n'
        ret += to_source(self.blockT, indent=1) 
        ret += '} else {\n'
        ret += to_source(self.blockF, indent=1)
        ret += '}'
        return ret

# ------ Debugging function to convert a model into source code (for easier viewing)


def to_source(node, indent=0):
    if isinstance(node, list):
        # list of statements
        ret = ''
        for n in node:
            ret += indent * '\t'
            ret += to_source(n)
        return ret
    elif isinstance(node, StatementNode):
        return node.to_source() + ';\n'
    elif node is None:
        return "None"
    else:
        return node.to_source()
