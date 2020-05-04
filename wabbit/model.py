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

from types import SimpleNamespace
from textwrap import dedent

class Model(SimpleNamespace):
    def to_source(self):
        raise NotImplementedError

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            + ", ".join(
                "{key}={value}".format(key=key, value=repr(value))
                for key, value in self.__dict__.items()
            )
            + ")"
        )

    def __str__(self):
        return self.to_source()


class Integer(Model):
    """
    Example: 42
    """

    def __init__(self, value):
        super().__init__(value=value)

    def to_source(self):
        return f"{self.value}"


class Float(Model):
    """
    Example: 42.0
    """
    def __init__(self, value):
        super().__init__(value=value)

    def to_source(self):
        return f'{self.value}'


class BinOp(Model):
    """
    Example: left + right
    """

    def __init__(self, op, left, right, **kwargs):
        super().__init__(op=op, left=left, right=right, **kwargs)

    def to_source(self):
        return f"{self.left} {self.op} {self.right}"


class Add(BinOp):
    def __init__(self, left, right):
        super().__init__(
            op='+',
            left=left,
            right=right
        )

class Subtract(BinOp):
    def __init__(self, left, right):
        super().__init__(
            op='-',
            left=left,
            right=right
        )

class Mult(BinOp):
    def __init__(self, left, right):
        super().__init__(
            op='*',
            left=left,
            right=right
        )

class Div(BinOp):
    def __init__(self, left, right):
        super().__init__(
            op='/',
            left=left,
            right=right
        )


class Assignment(BinOp):
    def __init__(self, name, value, **kwargs):
        super().__init__(left=name, right=value, op="=", **kwargs)

class Type(Model):
    ...

def infer_type(value):
    ...

class Const(Assignment):
    def __init__(self, name, value=None, type_=None):
        self._type = type_
        super().__init__(
            left=name,
            op='=',
            right=value,
            type=type_ or self._infer_type(value)
        )

    def _infer_type(self):
        ...

    def to_source(self):
        return f'const {self.left} {self.type} = {self.right};'

class Var(Assignment):
    def __init__(self, name, value=None, type_=None):
        self._type = None

class IfStatement(Model):
    def __init__(self, condition, body, else_clause=None):
        super().__init__(condition=condition, body=body, else_clause=else_clause)  # expression?  # ???

    def to_source(self):
        if_statement = f'if {self.condition} {{ ' \
               f'    {self.body} ' \
               f'}}'
        if self.else_clause != None:
            if_statement += f' else {{\n    {self.else_clause} \n}}'
        return dedent(if_statement)


class PrintStatement(Model):
    def __init__(self, expression):
        super().__init__(expression=expression)

    def to_source(self):
        return f"print {self.expression};"

class Program(Model):
    def __init__(self, *statements):
        self.statements = statements

    def to_source(self):
        return '\n'.join(str(stmt) for stmt in self.statements)

# ------ Debugging function to convert a model into source code (for easier viewing)


def to_source(node):
    return node.to_source()
    # if isinstance(node, Integer):
    #     return repr(node.value)
    # elif isinstance(node, BinOp):
    #     return f"{to_source(node.left)} {node.op} {to_source(node.right)}"
    # else:
    #     raise RuntimeError(f"Can't convert {node} to source")
