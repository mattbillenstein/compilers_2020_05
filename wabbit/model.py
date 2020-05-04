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


class Node:
    pass


# ================ Program ==============================

class Program(Node):
    """
    a list of statements
    """
    def __init__(self, *statements):
        self.statements = tuple(statements)

    def __repr__(self):
        lines = [to_source(st) for st in self.statements]
        return f"Program{self.statements}"

    def to_source(self):
        statements = [to_source(s) for s in self.statements]
        return "\n".join(statements)


# ========================= Number =======================

class Number(Node):
    pass


class Integer(Number):
    """
    Example: 42
    """
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Integer({self.value})"

    def to_source(self):
        return repr(self.value)


class Float(Number):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Float({self.value})"

    def to_source(self):
        return repr(self.value)


# =======================  Expression ====================

class Expression(Node):
    pass


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

    def to_source(self):
        return f"{to_source(self.left)} {self.op} {to_source(self.right)}"


class UnaryOp:
    """
    Example: - value
    """
    def __init__(self, op, value):
        self.op = op
        self.value = value

    def __repr__(self):
        return f"UnaryOp({self.op}, {self.value})"

    def to_source(self):
        return f"{self.op}{to_source(self.value)}"



# ========================== Statements ==================

class Statement(Node):
    pass


class PrintStatement(Statement):
    """
    print expression
    """
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        return f"PrintStatement({self.expression})\n"

    def to_source(self):
        return f"print {to_source(self.expression)};"


class Assignment(Statement):
    """location = expr"""
    def __init__(self, location, expr):
        self.location = location
        self.expr = expr

    def __repr__(self):
        return f"Assignment({self.location}, {self.expr})"

    def to_source(self):
        return f"{to_source(self.location)} = {to_source(self.expr)};"


class ConstantDefinition(Statement):
    """Examples:
        const pi = 3.14159;
        const tau float;
    """
    def __init__(self, location=None, type=None,  expr=None):
        if type is None:
            type = ''
        assert isinstance(type, str)
        assert location is not None
        assert expr is not None
        self.type = type
        self.location = location
        self.expr = expr

    def __repr__(self):
        return ("ConstantDefinition(" +
                f", {self.location}, {self.type}, {self.expr}")

    def to_source(self):
        parts = [f"const {to_source(self.location)}"]
        if to_source(self.type):
            parts.append(f" {to_source(self.type)}")
        parts.append(f" = {to_source(self.expr)}")
        return ''.join(parts) + ";"


class VariableDefinition(Statement):
    """Examples:
        var int pi;
    """
    def __init__(self, type, location, expr=''):
        self.type = type
        self.location = location
        self.expr = expr

    def __repr__(self):
        if self.expr:
            return ("VariableDefinition(" +
                f", {self.location}, {self.type}, {self.expr}")
        else:
            return ("VariableDefinition(" +
                f", {self.location}, {self.type}")

    def to_source(self):
        parts = [f"var {to_source(self.type)}"]
        parts.append(f" {to_source(self.location)}")
        if self.expr:
            parts.append(f" = {to_source(self.expr)}")
        return ''.join(parts) + ";"


class IfStatement(Statement):
    def __init__(self, condition, result, alternative=None):
        self.condition = condition
        self.result = result
        self.alternative = alternative

    def __repr__(self):
        if self.alternative is None:
            return (f"IfStatement({self.condition}, {self.result})")
        else:
            return (f"IfStatement({self.condition}, {self.result}), {self.alternative}")

    def to_source(self):
        result = f"if {to_source(self.condition)} {{\n{to_source(self.result)}\n}}"
        if self.alternative is not None:
            result += f" else {{\n {to_source(self.alternative)}\n}}"
        return result +"\n"



# =================== Types ===========

class Type(Node):
    """
    Example: float
    """
    def __init__(self, type=''):
        self.type = type

    def __repr__(self):
        return f"Type({self.type})"

    def to_source(self):
        return self.type


class Name(Node):
    """
    Example: x
    """
    def __init__(self, location):
        self.location = location

    def __repr__(self):
        return f"Name({self.location})"

    def to_source(self):
        return f"{self.location}"



def to_source(node):
    if hasattr(node, 'to_source'):
        return getattr(node, 'to_source')()
    elif isinstance(node, str):
        return node
    else:
        raise RuntimeError(f"Can't convert {node} to source")
