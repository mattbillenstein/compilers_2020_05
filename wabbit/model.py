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

class Integer:
    '''
    Example: 42
    '''
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f'Integer({self.value})'

class Float:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f'Float({self.value})'

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

class PrintStatement:
    def __init__(self, node_to_print):
        self.node_to_print = node_to_print

    def __repr__(self):
        return f'PrintStatement({self.node_to_print})'

class Const:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f'Const({self.name}, {self.value})'

class Var:
    def __init__(self, name, myType):
        self.name = name
        self.myType = myType

    def __repr__(self):
        return f'Var({self.name}, {self.myType})'

class Assign:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f'Assign({self.name}, {self.value})'

class Variable:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'Variable({self.name})'

class Compare:
    def __init__(self, op, lhs, rhs):
        self.op = op
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        return f'Compare({self.op}, {self.lhs}, {self.rhs})'

class If:
    def __init__(self, condition, consequence):
        self.condition = condition
        self.consequence = consequence

    def __repr__(self):
        return f'If({self.condition}, {self.consequence})'

class IfElse:
    def __init__(self, condition, consequence, otherwise):
        self.condition = condition
        self.consequence = consequence
        self.otherwise = otherwise

    def __repr__(self):
        return f'IfElse({self.condition}, {self.consequence}, {self.otherwise})'

class While:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f'While({self.condition}, {self.body})'

# ------ Debugging function to convert a model into source code (for easier viewing)

def to_source(node):
    if isinstance(node, Integer):
        return repr(node.value)
    elif isinstance(node, BinOp):
        return f'{to_source(node.left)} {node.op} {to_source(node.right)}'
    elif isinstance(node, list): # TODO this leads to ';' after eg while statements
        return ('\n').join([f'{to_source(x)};' for x in node])
    elif isinstance(node, PrintStatement):
        return f'print {to_source(node.node_to_print)}'
    elif isinstance(node, Float):
        return f'{node.value}'
    elif isinstance(node, Const):
        return f'const {node.name} = {to_source(node.value)}'
    elif isinstance(node, Var):
        return f'var {node.name} {node.myType}'
    elif isinstance(node, Assign):
        if isinstance(node.name, str):
            return f'{node.name} = {to_source(node.value)}'
        return f'{to_source(node.name)} = {to_source(node.value)}'
    elif isinstance(node, Variable):
        return f'{node.name}'
    elif isinstance(node, Compare):
        return f'{to_source(node.lhs)} {node.op} {to_source(node.rhs)}'
    elif isinstance(node, If): # TODO: this and IfElse need the same body formatting as while
        return f'''if {to_source(node.condition)} {{
    {to_source(node.consequence)}
}}'''
    elif isinstance(node, IfElse):
        return f'''if {to_source(node.condition)} {{
    {to_source(node.consequence)}
}} else {{
    {to_source(node.otherwise)}
}}'''
    elif isinstance(node, While): # TODO: what if we're a nested while, then it's not 4 spaces is it?
        body = f'    {to_source(node.body)}'
        if isinstance(node.body, list):
            body = '\n'.join([f'    {to_source(each)};' for each in node.body])
        return f'''while {to_source(node.condition)} {{
{body}
}}'''
    else:
        raise RuntimeError(f"Can't convert {node} to source")




