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
from collections import Counter

class Node(SimpleNamespace):
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


class Statement(Node):
    ...


class Definition(Statement):
    ...


class Expression(Node):
    ...


class Location(Expression):
    ...

class ExpressionStatement(Expression, Statement):
    """
    Expressions on their own CAN be statements
    """
    def __init__(self, expression):
        assert isinstance(expression, Expression)
        super().__init__(expression=expression)

    def to_source(self):
        src = str(self.expression)
        return f"{src};"

class Struct(Node):
    def __init__(self, *fields):
        super().__init__(fields=tuple(fields))
        assert all(isinstance(field, StructField) for field in self.fields)
        c = Counter(field.name for field in self.fields)
        for name, count in c.items():
            if count > 1:
                raise AssertionError("StructField names must be unique")


class StructField(Node):
    def __init__(self, name, type):
        assert isinstance(name, str)
        assert isinstance(type, str)
        super().__init__(name=name, type=type)


class FieldLookup(Location):
    """
    p.x
    p.y
    """
    def __init__(self, struct, fieldname):
        assert isinstance(struct, Struct)
        assert isinstance(fieldname, str)
        assert any(field.name == fieldname for field in struct.fields), f"Struct {struct} has no field {fieldname}"


class Integer(Expression):
    """
    Example: 42
    """

    def __init__(self, value):
        assert isinstance(value, int)
        super().__init__(value=value)

    def to_source(self):
        return f"{self.value}"


class Float(Expression):
    """
    Example: 42.0
    """

    def __init__(self, value):
        assert isinstance(value, float)
        super().__init__(value=value)

    def to_source(self):
        return f"{self.value}"


class Bool(Expression):
    def __init__(self, value):
        assert isinstance(value, bool)
        super().__init__(value=value)


class Identifier(Location):
    def __init__(self, name):
        assert isinstance(name, str)
        super().__init__(name=name)

    def to_source(self):
        return f"{self.name}"


class BinOp(Expression):
    """
    Example: left + right
    """

    def __init__(self, op, left, right):
        assert isinstance(op, str)
        assert op in ('+', '-', '*', '/', '<', '<=', '=>', '>', '==', '!='), f"Operation {op} is invalid"
        super().__init__(op=op, left=left, right=right)

    def to_source(self):
        return f"{self.left} {self.op} {self.right}"

    @classmethod
    def add(cls, left, right):
        return cls(op="+", left=left, right=right)

    @classmethod
    def subtract(cls, left, right):
        return cls(op="-", left=left, right=right)

    @classmethod
    def mult(cls, left, right):
        return cls(op="*", left=left, right=right)

    @classmethod
    def div(cls, left, right):
        return cls(op="/", left=left, right=right)


class Compare(BinOp):
    """
    ==, !=, <, >, <=, >=
    Comparisons operations always end up being Bools
    """

    @classmethod
    def lt(cls, left, right):
        return cls(left=left, right=right, op='<')

    @classmethod
    def lte(cls, left, right):
        return cls(left=left, right=right, op='<=')

    @classmethod
    def gt(cls, left, right):
        return cls(left=left, right=right, op='>')

    @classmethod
    def gte(cls, left, right):
        return cls(left=left, right=right, op='>=')

    @classmethod
    def eq(cls, left, right):
        return cls(left=left, right=right, op='==')

    @classmethod
    def ne(cls, left, right):
        return cls(left=left, right=right, op='!=')


class Unit(Expression):
    def to_source(self):
        return '()'


class Program(Node):
    """
    Collection of statements
    """
    def __init__(self, *statements):
        super().__init__(statements=tuple(statements))
        for stmt in self.statements:
            assert isinstance(stmt, Statement), f"{stmt} is not a statement"

    def to_source(self):
        return "\n".join(str(stmt) for stmt in self.statements)


class Clause(Node):
    """
    Example: LBRACE statements RBRACE

    Provides lexical scoping?
    Should work for if statements, function definitions too maybe?
    """
    def __init__(self, *statements):
        super().__init__(statements=tuple(statements))
        for stmt in self.statements:
            assert isinstance(stmt, Statement), f"{stmt} is not a statement"

    def to_source(self):
        statment_sources = "\n\t".join(str(stmt) for stmt in self.statements)
        return f'{{ \n\t{statment_sources} \n}}'


class CompoundExpr(Clause, Expression):  # Not sure if this is totally correct
    def __init__(self, *statements):
        super().__init__(*statements)

    def to_source(self):
        return '{' + ' '.join(str(stmt) for stmt in self.statements) + '}'


class PrintStatement(Statement):
    """
    PRINT expression SEMI
    """
    def __init__(self, expression):
        assert isinstance(expression, Expression)
        super().__init__(expression=expression)

    def to_source(self):
        return f"print {self.expression};"


class IfStatement(Statement):
    """
    IF expr LBRACE statements RBRACE [ ELSE LBRACE statements RBRACE ]
    """
    def __init__(self, condition, consequent, alternative=None):
        assert isinstance(condition, Expression)
        assert isinstance(consequent, Clause)
        if alternative is not None:
            assert isinstance(alternative, Clause)
        super().__init__(
            condition=condition, consequent=consequent, alternative=alternative
        )

    def to_source(self):
        if_statement = f"if {self.condition} {self.consequent}"
        if self.alternative is not None:
            if_statement += f" else {self.alternative}"
        return dedent(if_statement)


class Assignment(Statement):
    """
    location ASSIGN expression SEMI
    """
    def __init__(self, location, value):
        assert isinstance(location, Location)
        assert isinstance(value, Expression)
        super().__init__(location=location, value=value)

    def to_source(self):
        return f'{self.location} = {self.value};'


class VariableDefinition(Definition):
    def __init__(self, name, type, value):
        assert isinstance(name, str)
        assert type is None or isinstance(type, str)
        assert value is None or isinstance(value, Expression)
        super().__init__(name=name, type=type, value=value)

    def to_source(self):
        src = f'var {self.name}'
        if self.type is not None:
            src += f' {self.type}'
        if self.value is not None:
            src += f' = {self.value}'
        return f"{src};"


class ConstDefinition(Definition):
    def __init__(self, name, value, type=None):
        assert isinstance(name, str)
        assert isinstance(value, Expression)
        assert type is None or isinstance(type, str)
        super().__init__(name=name, value=value, type=type)

    def to_source(self):
        return f"const {self.name}{' ' + self.type if self.type else ''} = {self.value};"


class WhileLoop(Statement):
    def __init__(self, condition, body):
        assert isinstance(condition, Expression)
        assert isinstance(body, Clause)
        super().__init__(condition=condition, body=body)

    def to_source(self):
        if_statement = f"while {self.condition} {self.body}"
        return dedent(if_statement)



# ------ Debugging function to convert a model into source code (for easier viewing)


class NodeVisitor:
    ...  # We'll be removing to_source methods soon


def to_source(node):
    return node.to_source()
    # if isinstance(node, Integer):
    #     return repr(node.value)
    # elif isinstance(node, BinOp):
    #     return f"{to_source(node.left)} {node.op} {to_source(node.right)}"
    # else:
    #     raise RuntimeError(f"Can't convert {node} to source")
