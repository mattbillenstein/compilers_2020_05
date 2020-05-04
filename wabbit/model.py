# wabbit/model.py
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

# Top-level class for all model elements/nodes
class Node:
    pass

# These are abstract classes used to group nodes into different categories.
# This can be useful for organizing the model and our thoughts about the
# model.  What kinds of nodes can be used in different places for instance.

class Expression(Node):
    '''
    An expression is something that produces a value.
    '''

class Statement(Node):
    '''
    A statement is typically something that has a side-effect, but does NOT
    produce a value.  For example, assigning a variable, printing, looping.
    '''

class Definition(Statement):
    '''
    A definition is something that defines a name.  For example, a variable 
    declaration like "var x int".   Definitions are often mixed together
    with statements.  So, maybe a special category of statement.
    '''

class Location(Node):
    '''
    A location represents a place to load/store values.  For example, a variable,
    an object attribute, an index in an array, etc.
    '''

class Integer(Expression):
    '''
    Literal Integer: Example: 42
    '''
    def __init__(self, value):
        assert isinstance(value, int)
        self.value = value

    def __repr__(self):
        return f'Integer({self.value})'

    def to_source(self):
        return str(self.value)

class Float(Expression):
    '''
    Example: 4.2
    '''
    def __init__(self, value):
        assert isinstance(value, float)
        self.value = value

    def __repr__(self):
        return f'Float({self.value})'

    def to_source(self):
        return str(self.value)

class BinOp(Expression):
    '''
    Example: left + right
    '''
    def __init__(self, op, left:Expression, right:Expression):
        assert isinstance(left, Expression)
        assert isinstance(right, Expression)
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f'BinOp({self.op}, {self.left}, {self.right})'

    def to_source(self):
        return f'({self.left.to_source()} {self.op} {self.right.to_source()})'
        
class UnaryOp(Expression):
    '''
    Example: -operand
    '''
    def __init__(self, op, operand):
        assert isinstance(op, str)
        assert isinstance(operand, Expression)
        self.op = op
        self.operand = operand

    def __repr__(self):
        return f'UnaryOp({self.op}, {self.operand})'

    def to_source(self):
        return f'({self.op} {self.operand.to_source()})'

# Does this need to be part of the model or not? 
class Grouping(Expression):
    '''
    ( expression )      # Expression surrounded by parenthesis
    '''
    def __init__(self, expression):
        assert isinstance(expression, Expression)
        self.expression = expression
        
    def __repr__(self):
        return f'Grouping({self.expression})'

    def to_source(self):
        return f'({self.expression.to_source()})'

class LoadLocation(Expression):
    '''
    Loading a value out of a location for use in an expression.
    '''
    def __init__(self, location):
        assert isinstance(location, Location)
        self.location = location

    def __repr__(self):
        return f'LoadLocation({self.location})'

    def to_source(self):
        return self.location.to_source()

class Compound(Expression):
    '''
    A series of statements serving as a single expression.
    '''
    def __init__(self, statements):
        assert isinstance(statements, Statements)
        self.statements = statements

    def __repr__(self):
        return f'Compound({self.statements})'

    def to_source(self):
        return '{\n' + self.statements.to_source() + '\n}'

class Statements(Statement):
    '''
    Zero or more statements:

        statement1;
        statement2;
        ...
    '''
    def __init__(self, statements):
        assert isinstance(statements, list)
        assert all(isinstance(stmt, Statement) for stmt in statements)
        self.statements = statements

    def __repr__(self):
        return f'Statements({self.statements})'

    def to_source(self):
        return '\n'.join(stmt.to_source() for stmt in self.statements)

# Example:   Assignment
#
#     a = 2 + 4;
#     
#  location = expression;      

class AssignmentStatement(Statement):
    def __init__(self, location, expression):
        assert isinstance(location, Location)
        assert isinstance(expression, Expression)
        self.location = location
        self.expression = expression

    def __repr__(self):
        return f'AssignmentStatement({self.location}, {self.expression})'

    def to_source(self):
        return f'{self.location.to_source()} = {self.expression.to_source()};'


class ConstDefinition(Definition):
    '''
    const name [type] = value;
    '''
    def __init__(self, name, type, value):
        assert isinstance(name, str)
        assert type is None or isinstance(type, str)
        assert isinstance(value, Expression)
        self.name = name
        self.type = type    
        self.value = value

    def __repr__(self):
        return f'ConstDefinition({self.name}, {self.type}, {self.value})'

    def to_source(self):
        return f'const {self.name} {self.type if self.type else ""} = {self.value.to_source()};'

class VarDefinition(Definition):
    '''
    var name [type] [ = value];
    '''
    def __init__(self, name, type, value):
        assert isinstance(name, str)
        assert type is None or isinstance(type, str)
        assert value is None or isinstance(value, Expression)
        assert not (type is None and value is None)
        self.name = name
        self.type = type
        self.value = value

    def __repr__(self):
        return f'VarDefinition({self.name}, {self.type}, {self.value.to_source()})'

    def to_source(self):
        src = f'var {self.name} {self.type if self.type else ""}'
        if self.value:
            src += f'= {self.value.to_source()}'
        return src

class PrintStatement(Statement):
    '''
    print expression ;
    '''
    def __init__(self, expression):
        assert isinstance(expression, Expression) 
        self.expression = expression

    def __repr__(self):
        return f'PrintStatement({self.expression})'

    def to_source(self):
        return f'print {self.expression.to_source()};'

class IfStatement(Statement):
    '''
    if test { consequence } else { alternative }
    '''
    def __init__(self, test, consequence, alternative):
        assert isinstance(test, Expression)
        assert isinstance(consequence, Statements)
        assert isinstance(alternative, Statements)
        self.test = test
        self.consequence = consequence   #  What are these????  (Don't care now. Will refine as we work on it)
        self.alternative = alternative
        
    def __repr__(self):
        return f'IfStatement({self.test}, {self.consequence}, {self.alternative})'

    def to_source(self):
        # Enhancement.  Don't print else clause if empty.
        return (f'if {self.test.to_source()}' + ' {\n' +
                self.consequence.to_source() + '\n} else {\n' +
                self.alternative.to_source() + '\n}')

class WhileStatement(Statement):
    '''
    while test { body }
    '''
    def __init__(self, test, body):
        assert isinstance(test, Expression)
        assert isinstance(body, Statements)
        self.test = test
        self.body = body

    def __repr__(self):
        return f'WhileStatement({self.test}, {self.body})'

    def to_source(self):
        return (f'while {self.test.to_source()}' + ' {\n' +
                self.body.to_source() + '\n}'
                )

# Wrapper around a expression to indicate usage as a statement
class ExpressionStatement(Statement):
    def __init__(self, expression):
        assert isinstance(expression, Expression)
        self.expression = expression

    def __repr__(self):
        return f'ExpressionStatement({self.expression})'
    
    def to_source(self):
        return f'{self.expression.to_source()};'

class NamedLocation(Location):
    '''
    A location representing a simple variable name like "x"
    '''
    def __init__(self, name):
        assert isinstance(name, str)
        self.name = name
        
    def __repr__(self):
        return f'NamedLocation({self.name})'

    def to_source(self):
        return str(self.name)

# Future expansion (for structures)
class DottedLocation(Location):
    '''
    a.b = 23
    '''
    
# ------ Debugging function to convert a model into source code (for easier viewing)

# Could this be a method on the classes?  Maybe. 

def to_source(node):
    if isinstance(node, Integer):
        return repr(node.value)
    elif isinstance(node, BinOp):
        return f'{to_source(node.left)} {node.op} {to_source(node.right)}'
    elif isinstance(node, UnaryOp):
        ...
    elif isinstance(node, PrintStatement):
        ...
    else:
        raise RuntimeError(f"Can't convert {node} to source")




    
