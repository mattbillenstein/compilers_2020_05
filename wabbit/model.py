# model.py
# flake8: noqa
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
#             self.expr = expression
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


class Node:
    pass

class Expression(Node):
    """An expression is something that can be used on the left-hand-side
    of an assignment.
    """
    pass

class Location(Node):
    '''
    A location represents a place to load/store values.  For example, a variable,
    an object attribute, an index in an array, etc.
    '''

class Statement(Node):
    """A statement is a single complete instruction"""
    def __init__(self):
        raise NotImplementedError("Do you mean Statements (plural)?")


class Definition(Statement):
    """A variable definition"""
    pass


# =======================================================
#
# Having define the base classes, we list the others in
# alphabetical order so that they are easier to find
#
# =======================================================


class Assignment(Statement):
    """location = expr"""
    def __init__(self, location, expression):
        self.location = location
        self.expression = expression
        self.is_valid()

    def __repr__(self):
        return f"Assignment({self.location}, {self.expression})"

    def is_valid(self):
        assert isinstance(self.location, Location)
        assert isinstance(self.expression, Expression)


class BinOp(Expression):
    """
    Example: left + right
    """
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right
        self.is_valid()

    def __repr__(self):
        return f"BinOp({self.op}, {self.left}, {self.right})"

    def is_valid(self):
        assert self.op in {'+', '*', '-', '/', '<', '>', '>=', '<=', '=='}
        assert isinstance(self.left, Expression)
        assert isinstance(self.right, Expression)

class Const(Definition):
    """Examples:
        const pi = 3.14159;
        const tau float;
    """
    def __init__(self, name, type, expression):
        self.name = name
        self.type = type
        self.expression = expression
        self.is_valid()

    def __repr__(self):
        if self.type:
            return ("Const(" +
                f"{self.name}, {self.type}, {self.expression})")
        else:
            return ("Const(" +
                f"{self.name}, {self.expression})")

    def is_valid(self):
        assert isinstance(self.type, Type)
        assert isinstance(self.name, str)
        assert isinstance(self.expression, Expression)


class Compound(Expression):
    '''
    A series of statements or expressions serving as a single expression.
    '''
    def __init__(self, *statements):
        self.statements = statements
        self.is_valid()

    def __repr__(self):
        return f'Compound({self.statements})'

    def is_valid(self):
        assert all(isinstance(st, (Expression, Statement)) for st in self.statements)


class Float(Expression):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Float({self.value})"

    def is_valid(self):
        assert isinstance(self.value, float)


class ExpressionStatement(Statement):
    """Currently, the only purpose of this class is to ensure that
       expressions used as statements are properly recreated with
       a final semi-colon when converting back to source.
    """
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        return f"ExpressionStatement({self.expression})"

    def is_valid(self):
        assert isinstance(self.expression, Expression)

class Group(Expression):
    '''
    ( expression )      # Expression surrounded by parenthesis
    '''
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        return f'Group({self.expression})'

    def is_valid(self):
        assert isinstance(self.expression, Expression)

class If(Statement):
    def __init__(self, condition, result, alternative=None):
        self.condition = condition
        self.result = result
        self.alternative = alternative
        self.is_valid()

    def __repr__(self):
        if self.alternative is None:
            return (f"If({self.condition}, {self.result})")
        else:
            return (f"If({self.condition}, {self.result}), {self.alternative}")

    def is_valid(self):
        assert isinstance(self.condition, Expression)
        assert isinstance(self.result, (Statement, Statements))
        assert self.alternative is None or isinstance(self.alternative, (Statement, Statements))


class Integer(Expression):
    """
    Example: 42
    """
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Integer({self.value})"

    def is_valid(self):
        assert isinstance(self.value, int)


class LoadLocation(Expression):
    '''
    Loading a value out of a location for use in an expression.
    '''
    def __init__(self, location):
        self.location = location
        self.is_valid()

    def __repr__(self):
        return f'LoadLocation({self.location})'

    def is_valid(self):
        assert isinstance(self.location, Location)


class NamedLocation(Location):
    """
    A location representing a simple variable name
    """
    def __init__(self, name):
        self.name = name
        self.is_valid()

    def __repr__(self):
        return f"NamedLocation({self.name})"

    def is_valid(self):
        assert isinstance(self.name, str)


class Print(Statement):
    """
    print expression
    """
    def __init__(self, expression):
        self.expression = expression
        self.is_valid()

    def __repr__(self):
        return f"Print({self.expression})\n"

    def is_valid(self):
        assert isinstance(self.expression, (Expression, str))


class Statements(Statement):
    """
    A sequence of statements
    """
    def __init__(self, *statements):
        self.statements = statements
        self.is_valid()

    def __repr__(self):
        return f"Statements{self.statements}"

    def is_valid(self):
        assert all(isinstance(st, Statement) for st in self.statements)


class Type(Node):
    """
    Example: float
    """
    def __init__(self, type):
        self.type = type
        self.is_valid()

    def __repr__(self):
        return f"Type({self.type})"

    def is_valid(self):
        assert self.type is None or isinstance(self.type, str)

class UnaryOp(Expression):
    """
    Example: - value
    """
    def __init__(self, op, value):
        self.op = op
        self.value = value
        self.is_valid()

    def __repr__(self):
        return f"UnaryOp({self.op}, {self.value})"

    def is_valid(self):
        assert self.op == "-"
        assert isinstance(self.value, Expression)


class Var(Definition):
    """Examples:
        var int pi;
    """
    def __init__(self, name, type, expression=''):
        self.name = name
        self.type = type
        self.expression = expression
        self.is_valid()

    def __repr__(self):
        if self.expression:
            return ("Var(" +
                f"{self.name}, {self.type}, {self.expression})")
        else:
            return ("Var(" +
                f"{self.name}, {self.type})")

    def is_valid(self):
        assert isinstance(self.type, Type)
        assert isinstance(self.name, str)
        assert isinstance(self.expression, (str, Expression))


class While(Statement):
    def __init__(self, condition, statements):
        self.condition = condition
        self.statements = statements
        self.is_valid()

    def __repr__(self):
        return (f"While({self.condition}, {self.statements})")

    def is_valid(self):
        assert isinstance(self.condition, Expression)
        assert isinstance(self.statements, (Statement, Statements))

######################## to_source ##################


from functools import singledispatch

@singledispatch
def to_source(node):
    raise RuntimeError("Can't generate source for {node}")

add = to_source.register

# Order alphabetically so that they are easier to find

@add(Assignment)
def to_source_Assignment(node):
    return f"{to_source(node.location)} = {to_source(node.expression)};"

@add(BinOp)
def to_source_BinOp(node):
    return f"{to_source(node.left)} {node.op} {to_source(node.right)}"

@add(Const)
def to_source_Const(node):
    parts = [f"const {node.name}"]
    if to_source(node.type):
        parts.append(f" {to_source(node.type)}")
    parts.append(f" = {to_source(node.expression)}")
    return ''.join(parts) + ";"

@add(Compound)
def to_source_Compound(node):
    statements = [to_source(s) for s in node.statements]
    return "{ " + " ".join(statements) + " }"

@add(Float)
def to_source_Float(node):
    return repr(node.value)

@add(ExpressionStatement)
def to_source_ExpressionStatement(node):
    return f"{to_source(node.expression)};"

@add(Group)
def to_source_Group(node):
    return f"({to_source(node.expression)})"

@add(If)
def to_source_If(node):
    result = f"if {to_source(node.condition)} {{\n{to_source(node.result)}\n}}"
    if node.alternative is not None:
        result += f" else {{\n {to_source(node.alternative)}\n}}"
    return result +"\n"

@add(Integer)
def to_source_Integer(node):
    return repr(node.value)

@add(LoadLocation)
def to_source_LoadLocation(node):
    return to_source(node.location)

@add(NamedLocation)
def to_source_NamedLocation(node):
    return f"{node.name}"

@add(Print)
def to_source_Print(node):
    return f"print {to_source(node.expression)};"

@add(Statements)
def to_source_Statements(node):
    statements = [to_source(s) for s in node.statements]
    return "\n".join(statements)

@add(Type)
def to_source_Type(node):
    if node.type is None:
        return ''
    return node.type

@add(UnaryOp)
def to_source_UnaryOp(node):
    return f"{node.op}{to_source(node.value)}"

@add(Var)
def to_source_Var(node):
    parts = [f"var {node.name}"]
    parts.append(f" {to_source(node.type)}")
    if node.expression:
        parts.append(f" = {to_source(node.expression)}")
    return ''.join(parts) + ";"

@add(While)
def to_source_While(node):
    return f"while {to_source(node.condition)} {{\n{to_source(node.statements)}\n}}"
