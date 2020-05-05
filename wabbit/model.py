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
    def __repr__(self):
        argstr = ''
        return "{}.{}<{}>({})".format(self.__class__.__module__, self.__class__.__name__, id(self), argstr)


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


class DeclLocation(Location):
    '''
    Example: var foo int
    '''
    def __init__(self, identifier: Identifier, _type=None, const=False):
        self.identifier = identifier
        self._type = _type
        self.const = const

    def __repr__(self):
        return f'DeclLocation({self.identifier}, {str(self._type) or "None"}, {"True" if self.const else "False"}) '


class ScalarNode(ExpressionNode):
    '''
    Example: 42
    '''


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


class UnOp(ExpressionNode):
    '''
    Example: -right
    '''
    def __init__(self, op, right: ExpressionNode):
        self.op = op
        self.right = right

    def __repr__(self):
        return f'UnOp({self.op}, {self.right})'


class PrintStatement(StatementNode):
    '''
    Example: print(EXPR)
    '''
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f'Print({self.expr})'


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
        ret = f'ConditionalStatement({{str(self.cond)}},' 
        ret += '[' + to_repr(self.blockT) + '], '
        ret += '[' + to_repr(self.blockF) + '])'
        return ret

class ConditionalLoopStatement(StatementNode):
    '''
    Example:
    while EXPR {
        BLOCK
    } 
    '''

    def __init__(self, cond: ExpressionNode, block: List[StatementNode]):
        self.cond = cond
        self.block = block

    def __repr__(self):
        return f'ConditionalLoopStatement(' + str(self.cond) + ', [' + to_repr(self.block) + '])'

class BlockExpression(ExpressionNode):
    '''
    Example:
    { x = 1; y; }
    '''

    def __init__(self, block: List[StatementNode]):
        self.block = block

    def __repr__(self):
        return to_repr(self.block)


class ExpressionStatement(StatementNode):
    '''
    Example:
    t;
    '''

    def __init__(self, statement: ExpressionNode):
        self.statement = statement

    def __repr__(self):
        return str(self.statement)


class FuncCall(ExpressionNode):
    def __init__(self, name: str, args: List[ExpressionNode]):
        self.name = name
        self.args = args


class FuncDeclStatement(StatementNode):
    def __init__(self, name: str, args: List[List[str]], retval: str, body: List[StatementNode]):
        self.name = name
        self.retval = retval
        self.args = args
        self.body = body


class ReturnStatement(StatementNode):
    def __init__(self, retval: ExpressionNode):
        self.retval = retval


# ------ Debugging function to convert a model into source code (for easier viewing)


def to_repr(node, indent=0):
    if isinstance(node, list):
        # list of nodes
        return '[' + ', '.join(map(to_repr, node)) + ']'
    else:
        return str(node)

