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

# TODO UnaryOp
# TODO Grouping (for when they put parens around things to say which go first)
# TODO implement is_correct for everything

def checkMe(n):
    ''''''
    assert(n.is_correct())

class Node:
    def __init__(self):
        self.is_expression = False
        self.is_assignable = False

    def is_correct(self):
        return True

class Statements(Node):
    def __init__(self, statements):
        super().__init__()
        self.statements = statements

    def __repr__(self):
        return f'Statements({self.statements})'

    def is_correct(self):
        if not isinstance(self.statements, list):
            return False
        return all([isinstance(Node, x) and x.is_correct() for x in self.statements])

class Integer(Node):
    '''
    Example: 42
    '''
    def __init__(self, value):
        super().__init__()
        self.value = value
        self.is_expression = True
        checkMe(self)

    def __repr__(self):
        return f'Integer({self.value})'

    def is_correct(self):
        return isinstance(self.value, int)

class Float(Node):
    def __init__(self, value):
        super().__init__()
        self.value = value
        self.is_expression = True
        checkMe(self)

    def __repr__(self):
        return f'Float({self.value})'

    def is_correct(self):
        return isinstance(self.value, float)

class BinOp(Node):
    '''
    Example: left + right
    '''
    def __init__(self, op, left, right):
        super().__init__()
        self.op = op
        self.left = left
        self.right = right
        self.is_expression = True
        checkMe(self)

    def is_correct(self):
        legal_ops = ['+', '-', '/', '*', '==', '!=', '&&', '||', '!', '<', '<=', '>', '>=', '==', '!=' ]
        if not self.op in legal_ops:
            return False
        if not self.left.is_expression:
            return False
        if not self.right.is_expression:
            return False
        return True

    def __repr__(self):
        return f'BinOp({self.op}, {self.left}, {self.right})'

    def to_source(self):
        return f'{to_source(node.left)} {node.op} {to_source(node.right)}'

class PrintStatement(Node):
    def __init__(self, node_to_print):
        super().__init__()
        self.node_to_print = node_to_print
        checkMe(self)

    def __repr__(self):
        return f'PrintStatement({self.node_to_print})'

class Const(Node):
    def __init__(self, name, value):
        super().__init__()
        self.name = name
        self.value = value
        checkMe(self)

    def __repr__(self):
        return f'Const({self.name}, {self.value})'

class Var(Node):
    def __init__(self, name, myType):
        super().__init__()
        self.name = name
        self.myType = myType
        self.is_assignable = True
        checkMe(self)

    def __repr__(self):
        return f'Var({self.name}, {self.myType})'

class Assign(Node):
    def __init__(self, name, value):
        super().__init__()
        self.name = name
        self.value = value
        checkMe(self)

    def __repr__(self):
        return f'Assign({self.name}, {self.value})'

    def is_correct(self):
        if (not (isinstance(self.name, Node) and self.name.is_assignable)):
            return False
        return isinstance(self.value, Node) and self.value.is_expression


class Variable(Node):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.is_expression = True
        self.is_assignable = True
        checkMe(self)

    def __repr__(self):
        return f'Variable({self.name})'

    def is_correct(self):
        return isinstance(self.name, str)

class If(Node):
    def __init__(self, condition, consequence):
        super().__init__()
        self.condition = condition
        self.consequence = consequence
        checkMe(self)

    def __repr__(self):
        return f'If({self.condition}, {self.consequence})'

    def is_correct(self):
        return isinstance(self.consequence, Statements)

class IfElse(Node):
    def __init__(self, condition, consequence, otherwise):
        super().__init__()
        self.condition = condition
        self.consequence = consequence
        self.otherwise = otherwise
        checkMe(self)

    def __repr__(self):
        return f'IfElse({self.condition}, {self.consequence}, {self.otherwise})'

    def is_correct(self):
        if not isinstance(self.consequence, Statements):
            return False
        return isinstance(self.otherwise, Statements)

class While(Node):
    def __init__(self, condition, body):
        super().__init__()
        self.condition = condition
        self.body = body
        checkMe(self)

    def __repr__(self):
        return f'While({self.condition}, {self.body})'

    def is_correct(self):
        return isinstance(self.body, Statements)

class CompoundExpression(Node):
    def __init__(self, statements):
        super().__init__()
        self.statements = statements
        self.is_expression = True
        checkMe(self)

    def __repr__(self):
        return f'CompoundExpression({self.statements})'

    def is_correct(self):
        return isinstance(self.statements, Statements)

# ------ Debugging function to convert a model into source code (for easier viewing)

nesting_level = 0

def to_source_list(l):
    global nesting_level
    indent = nesting_level * '    '
    return ('\n').join([f'{indent}{to_source(x)};' for x in l.statements]) # TODO this leads to ';' after eg while statements

def to_source_node_or_list(x):
    if isinstance(x, list):
        return to_source_list(x)
    return to_source(x)

def to_source_nested_body(body):
    global nesting_level
    nesting_level += 1
    body = to_source_node_or_list(body)
    nesting_level -= 1
    return body

def to_source(node):
    if isinstance(node, Integer):
        return repr(node.value)
    elif isinstance(node, BinOp):
        return f'{to_source(node.left)} {node.op} {to_source(node.right)}'
    elif isinstance(node, Statements):
        return to_source_list(node)
    elif isinstance(node, PrintStatement):
        return f'print {to_source(node.node_to_print)}'
    elif isinstance(node, Float):
        return f'{node.value}'
    elif isinstance(node, Const):
        return f'const {node.name} = {to_source(node.value)}'
    elif isinstance(node, Var):
        if node.myType is None:
            return f'var {node.name}'
        return f'var {node.name} {node.myType}'
    elif isinstance(node, Assign):
        if isinstance(node.name, str):
            return f'{node.name} = {to_source(node.value)}'
        return f'{to_source(node.name)} = {to_source(node.value)}'
    elif isinstance(node, Variable):
        return f'{node.name}'
    elif isinstance(node, If):
        return f'''if {to_source(node.condition)} {{
{to_source_nested_body(node.consequence)}
}}'''
    elif isinstance(node, IfElse):
        return f'''if {to_source(node.condition)} {{
{to_source_nested_body(node.consequence)}
}} else {{
{to_source_nested_body(node.otherwise)}
}}'''
    elif isinstance(node, While):
        return f'''while {to_source(node.condition)} {{
{to_source_nested_body(node.body)}
}}'''
    elif isinstance(node, CompoundExpression):
        return f'{{ {"; ".join([to_source(each) for each in node.statements.statements])}; }}'
    else:
        raise RuntimeError(f"Can't convert {node} to source")




