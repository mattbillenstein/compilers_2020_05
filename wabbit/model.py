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


class Statement(Node):
    """A statement is a single complete instruction"""
    pass


class ManyStatements(Node):
    """A collection of statements"""
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

    def __repr__(self):
        return f"Assignment({self.location}, {self.expression})"


class BinOp(Expression):
    """
    Example: left + right
    """
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f"BinOp({self.op}, {self.left}, {self.right})"


class ConstantDefinition(Statement):
    """Examples:
        const pi = 3.14159;
        const tau float;
    """
    def __init__(self, location, type, expression):
        assert isinstance(type, Type)
        self.type = type
        self.location = location
        self.expression = expression

    def __repr__(self):
        if self.type:
            return ("ConstantDefinition(" +
                f"{self.location}, {self.type}, {self.expression})")
        else:
            return ("ConstantDefinition(" +
                f"{self.location}, {self.expression})")


class Float(Expression):
    def __init__(self, value):
        assert isinstance(value, float)
        self.value = value

    def __repr__(self):
        return f"Float({self.value})"


class IfStatement(Statement):
    def __init__(self, condition, result, alternative=None):
        assert isinstance(condition, Expression)
        assert isinstance(result, (Statement, ManyStatements))
        assert alternative is None or isinstance(alternative, (Statement, ManyStatements))
        self.condition = condition
        self.result = result
        self.alternative = alternative

    def __repr__(self):
        if self.alternative is None:
            return (f"IfStatement({self.condition}, {self.result})")
        else:
            return (f"IfStatement({self.condition}, {self.result}), {self.alternative}")


class Integer(Expression):
    """
    Example: 42
    """
    def __init__(self, value):
        assert isinstance(value, int)
        self.value = value

    def __repr__(self):
        return f"Integer({self.value})"


class Name(Expression):
    """
    Example: x
    """
    def __init__(self, location):
        self.location = location

    def __repr__(self):
        return f"Name({self.location})"

class Program(ManyStatements):
    """
    A collection of statements
    """
    def __init__(self, *statements):
        self.statements = tuple(statements)
        assert all(isinstance(st, Statement) for st in self.statements)

    def __repr__(self):
        lines = [to_source(st) for st in self.statements]
        return f"Program{self.statements}"


class PrintStatement(Statement):
    """
    print expression
    """
    def __init__(self, expression):
        assert isinstance(expression, (Expression, str))
        self.expression = expression

    def __repr__(self):
        return f"PrintStatement({self.expression})\n"


class Type(Node):
    """
    Example: float
    """
    def __init__(self, type):
        assert type is None or isinstance(type, str)
        self.type = type

    def __repr__(self):
        return f"Type({self.type})"

class UnaryOp(Expression):
    """
    Example: - value
    """
    def __init__(self, op, value):
        assert isinstance(op, str)
        assert isinstance(value, Expression)
        self.op = op
        self.value = value

    def __repr__(self):
        return f"UnaryOp({self.op}, {self.value})"


class VariableDefinition(Statement):
    """Examples:
        var int pi;
    """
    def __init__(self, type, location, expression=''):
        self.type = type
        self.location = location
        self.expression = expression

    def __repr__(self):
        if self.expression:
            return ("VariableDefinition(" +
                f"{self.location}, {self.type}, {self.expression})")
        else:
            return ("VariableDefinition(" +
                f"{self.location}, {self.type})")


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

@add(ConstantDefinition)
def to_source_ConstantDefinition(node):
    parts = [f"const {to_source(node.location)}"]
    if to_source(node.type):
        parts.append(f" {to_source(node.type)}")
    parts.append(f" = {to_source(node.expression)}")
    return ''.join(parts) + ";"

@add(Float)
def to_source_Float(node):
    return repr(node.value)

@add(IfStatement)
def to_source_IfStatement(node):
    result = f"if {to_source(node.condition)} {{\n{to_source(node.result)}\n}}"
    if node.alternative is not None:
        result += f" else {{\n {to_source(node.alternative)}\n}}"
    return result +"\n"

@add(Integer)
def to_source_Integer(node):
    return repr(node.value)

@add(Name)
def to_source_Name(node):
    return f"{node.location}"

@add(PrintStatement)
def to_source_PrintStatement(node):
    return f"print {to_source(node.expression)};"

@add(Program)
def to_source_Program(node):
    for s in node.statements:
        print(s)
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

@add(VariableDefinition)
def to_source_VariableDefinition(node):
    parts = [f"var {to_source(node.type)}"]
    parts.append(f" {to_source(node.location)}")
    if node.expression:
        parts.append(f" = {to_source(node.expression)}")
    return ''.join(parts) + ";"
