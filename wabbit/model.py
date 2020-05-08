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
    def __init__(self, *, lineno=None):
        self.lineno = lineno

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
    type = 'int'
    def __init__(self, value, **options):
        assert isinstance(value, int)
        self.value = value
        super().__init__(**options)

    def __repr__(self):
        return f'Integer({self.value})'

class Float(Expression):
    '''
    Example: 4.2
    '''
    type = 'float'
    def __init__(self, value, **options):
        assert isinstance(value, float)
        self.value = value
        super().__init__(**options)

    def __repr__(self):
        return f'Float({self.value})'

class Bool(Expression):
    '''
    Literal Bool:  true, false
    '''
    type = 'bool'
    def __init__(self, value, **options):
        assert isinstance(value, bool)
        self.value = value
        super().__init__(**options)

    def __repr__(self):
        return f'Bool({self.value})'

class Char(Expression):
    '''
    Literal Char:
    '''
    type = 'char'
    def __init__(self, value, **options):
        assert isinstance(value, str)
        self.value = value
        super().__init__(**options)

    def __repr__(self):
        return f'Char({self.value!r})'

class BinOp(Expression):
    '''
    Example: left + right
    '''
    def __init__(self, op, left, right, **options):
        assert isinstance(left, Expression)
        assert isinstance(right, Expression)
        self.op = op
        self.left = left
        self.right = right
        super().__init__(**options)

    def __repr__(self):
        return f'BinOp({self.op}, {self.left}, {self.right})'

class UnaryOp(Expression):
    '''
    Example: -operand
    '''
    def __init__(self, op, operand, **options):
        assert isinstance(op, str)
        assert isinstance(operand, Expression)
        self.op = op
        self.operand = operand
        super().__init__(**options)

    def __repr__(self):
        return f'UnaryOp({self.op}, {self.operand})'

# Does this need to be part of the model or not? 
class Grouping(Expression):
    '''
    ( expression )      # Expression surrounded by parenthesis
    '''
    def __init__(self, expression, **options):
        assert isinstance(expression, Expression)
        self.expression = expression
        super().__init__(**options)
        
    def __repr__(self):
        return f'Grouping({self.expression})'

class LoadLocation(Expression):
    '''
    Loading a value out of a location for use in an expression.
    '''
    def __init__(self, location, **options):
        assert isinstance(location, Location)
        self.location = location
        super().__init__(**options)

    def __repr__(self):
        return f'LoadLocation({self.location})'

class Compound(Expression):
    '''
    A series of statements serving as a single expression.
    '''
    def __init__(self, statements, **options):
        assert isinstance(statements, Statements)
        self.statements = statements
        super().__init__(**options)

    def __repr__(self):
        return f'Compound({self.statements})'

#   var x = { 2+3; 4+5; 10+11;};    // 21 is answer
#   var x = if test compound else compound;   // Possible extension?
#
#   if test { statements } else { statements }
#

class Statements(Statement):
    '''
    Zero or more statements:

        statement1;
        statement2;
        ...
    '''
    def __init__(self, statements, **options):
        assert isinstance(statements, list)
        assert all(isinstance(stmt, Statement) for stmt in statements)
        self.statements = statements
        super().__init__(**options)

    def __repr__(self):
        return f'Statements({self.statements})'

# Example:   Assignment
#
#     a = 2 + 4;
#     
#  location = expression;      

class AssignmentStatement(Statement):
    def __init__(self, location, expression, **options):
        assert isinstance(location, Location)
        assert isinstance(expression, Expression)
        self.location = location
        self.expression = expression
        super().__init__(**options)

    def __repr__(self):
        return f'AssignmentStatement({self.location}, {self.expression})'

class ConstDefinition(Definition):
    '''
    const name [type] = value;
    '''
    def __init__(self, name, type, value, **options):
        assert isinstance(name, str)
        assert type is None or isinstance(type, str)
        assert isinstance(value, Expression)
        self.name = name
        self.type = type    
        self.value = value
        super().__init__(**options)

    def __repr__(self):
        return f'ConstDefinition({self.name}, {self.type}, {self.value})'

class VarDefinition(Definition):
    '''
    var name [type] [ = value];

    var bar float;
    '''
    def __init__(self, name, type, value, **options):
        assert isinstance(name, str)
        assert type is None or isinstance(type, str)
        assert value is None or isinstance(value, Expression)
        assert not (type is None and value is None)
        self.name = name
        self.type = type
        self.value = value
        super().__init__(**options)

    def __repr__(self):
        return f'VarDefinition({self.name}, {self.type}, {self.value})'

class PrintStatement(Statement):
    '''
    print expression ;
    '''
    def __init__(self, expression, **options):
        assert isinstance(expression, Expression) 
        self.expression = expression
        super().__init__(**options)

    def __repr__(self):
        return f'PrintStatement({self.expression})'

class IfStatement(Statement):
    '''
    if test { consequence } else { alternative }
    '''
    def __init__(self, test, consequence, alternative, **options):
        assert isinstance(test, Expression)
        assert isinstance(consequence, Statements)
        assert isinstance(alternative, Statements)
        self.test = test
        self.consequence = consequence   #  What are these????  (Don't care now. Will refine as we work on it)
        self.alternative = alternative
        super().__init__(**options)
        
    def __repr__(self):
        return f'IfStatement({self.test}, {self.consequence}, {self.alternative})'

class WhileStatement(Statement):
    '''
    while test { body }
    '''
    def __init__(self, test, body, **options):
        assert isinstance(test, Expression)
        assert isinstance(body, Statements)
        self.test = test
        self.body = body
        super().__init__(**options)

    def __repr__(self):
        return f'WhileStatement({self.test}, {self.body})'

class BreakStatement(Statement):
    '''
    break;
    '''
    def __init__(self, **options):
        super().__init__(**options)

class ContinueStatement(Statement):
    '''
    break;
    '''
    def __init__(self, **options):
        super().__init__(**options)


# Wrapper around a expression to indicate usage as a statement
class ExpressionStatement(Statement):
    def __init__(self, expression, **options):
        assert isinstance(expression, Expression)
        self.expression = expression
        super().__init__(**options)

    def __repr__(self):
        return f'ExpressionStatement({self.expression})'

class NamedLocation(Location):
    '''
    A location representing a simple variable name like "x"
    '''
    def __init__(self, name, **options):
        assert isinstance(name, str)
        self.name = name
        super().__init__(**options)
        
    def __repr__(self):
        return f'NamedLocation({self.name})'

# Future expansion (for structures)
class DottedLocation(Location):
    '''
    a.b = 23
    '''


# ------- Functions
class FunctionDefinition(Definition):
    '''
    func square(x int) int { ... }
    '''
    def __init__(self, name, parameters, return_type, statements, **options):
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.statements = statements
        super().__init__(**options)

    def __repr__(self):
        return f'FunctionDefinition({self.name}, {self.parameters}, {self.return_type}, {self.statements})'

class FunctionApplication(Expression):
    '''
    square(10);
    '''
    def __init__(self, name, arguments, **options):
        self.name = name
        self.arguments = arguments
        super().__init__(**options)

    def __repr__(self):
        return f'FunctionApplication({self.name}, {self.arguments})'

class Parameter(Definition):
    '''
    func square(x int) int { ... }
                ^^^^^
    '''
    def __init__(self, name, type, **options):
        self.name = name
        self.type = type
        super().__init__(**options)

    def __repr__(self):
        return f'Parameter({self.name}, {self.type})'

class ReturnStatement(Statement):
    '''
    return expression ;
    '''
    def __init__(self, expression, **options):
        self.expression = expression
        super().__init__(**options)

    def __repr__(self):
        return f'ReturnStatement({self.expression})'

        



# ------ Debugging function to convert a model into source code (for easier viewing)

# Could this be a method on the classes?  Maybe. 

# Pro: Decoupled from the data model (different code, easy to change, etc.)

def to_source(node):
    # Ugh. case-analysis with if-else
    if isinstance(node, Integer):
        return repr(node.value)
    elif isinstance(node, BinOp):
        return f'{to_source(node.left)} {node.op} {to_source(node.right)}'
    elif isinstance(node, UnaryOp):
        return f'{node.op}{to_source(node.operand)}'
    elif isinstance(node, PrintStatement):
        return f'print {to_source(node.expression)};\n'
    else:
        raise RuntimeError(f"Can't convert {node} to source")

# Alternatives to the big-if.

# Visitor Pattern
class NodeVisitor:
    def __init__(self):
        self.env = { } 

    def visit(self, node):
        methname = f'visit_{node.__class__.__name__}'   
        getattr(self, methname)(node)   # A bit more natural for Python

        # Extension:  If no matching method, automatically traverse into child nodes

    def visit_Integer(self, node):
        return repr(node.value)
    
    def visit_Float(self, node):
        ...

    def visit_BinOp(self, node):
        return f'{self.visit(node.left)} {node.op} {self.visit(node.right)}'
              #   ^^^^^
    def visit_UnaryOp(self, node):
        ...

    def visit_PrintStatement(self, node):
        ...

# Example of using visitor pattern
def to_source(node):
    NodeVisitor().visit(node)    

# Another option:  Use singledispatch

from functools import singledispatch

@singledispatch
def to_source(node):
    raise RuntimeError(f"Can't generate source for {node}")

rule = to_source.register     # Decorator shortcut

# Absolutely critical:  The functions here can *** NOT *** be named "to_source"
@rule(Integer)
def to_source_integer(node):
    return str(node.value)

@rule(Float)
def to_source_float(node):
    return str(node.value)

@rule(Bool)
def to_source_bool(node):
    return str(node.value).lower()

@rule(BinOp)
def to_source_binop(node):
    return f'{to_source(node.left)} {node.op} {to_source(node.right)}'

@rule(UnaryOp)
def to_source_unaryop(node):
    return f'({node.op} {to_source(node.operand)})'

@rule(Grouping)
def to_source_grouping(node):
    return f'({to_source(node.expression)})'

@rule(LoadLocation)
def to_source_load_location(node):
    return to_source(node.location)

@rule(Compound)
def to_source_compound(node):
    return '{\n' + to_source(node.statements) + '\n}'

@rule(Statements)
def to_source_statements(node):
    return '\n'.join(to_source(stmt) for stmt in node.statements)

@rule(AssignmentStatement)
def to_source_assignment(node):
    return f'{to_source(node.location)} = {to_source(node.expression)};'

@rule(ConstDefinition)
def to_source_const_definition(node):
    return f'const {node.name} {node.type if node.type else ""} = {to_source(node.value)};'

@rule(VarDefinition)
def to_source_var_definition(node):
    src = f'var {node.name} {node.type if node.type else ""}'
    if node.value:
        src += f'= {to_source(node.value)}'
    return src + ';'

@rule(PrintStatement)
def to_source_print_statement(node):
    return f'print {to_source(node.expression)};'

@rule(IfStatement)
def to_source_if_statement(node):
    # Enhancement.  Don't print else clause if empty.
    return (f'if {to_source(node.test)}' + ' {\n' +
            to_source(node.consequence) + '\n} else {\n' +
            to_source(node.alternative) + '\n}')


@rule(WhileStatement)
def to_source_while_statement(node):
    return (f'while {to_source(node.test)}' + ' {\n' +
            to_source(node.body) + '\n}'
            )

@rule(BreakStatement)
def to_source_break(node):
    return f'break;'

@rule(ContinueStatement)
def to_source_continue(node):
    return f'continue;'

@rule(ExpressionStatement)
def to_source_expr_statement(node):
    return to_source(node.expression) + ';'


@rule(NamedLocation)
def to_source_named_location(node):
    return node.name

