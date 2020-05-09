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
from collections.abc import Iterable
import ast

class Node(SimpleNamespace):
    def to_source(self):
        raise NotImplementedError

    def __repr__(self):
        rep = (
            f"{self.__class__.__name__}("
            + ", ".join(
                "{key}={value}".format(key=key, value=repr(value))
                for key, value in self.__dict__.items()
            )
            + ")"
        )
        try:
            return black_format_code(rep)
        except ImportError as e:
            # Just in case you don't have `black` installed :-)
            return rep
        except Exception as e:
            print('WARN: Unexpected error formatting code ', e)
            return rep

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


class StructDefinition(Definition):
    """
    STRUCT NAME LBRACE { struct_field } RBRACE
    """
    def __init__(self, name, *fields):
        super().__init__(name=name, fields=tuple(fields))
        for field in self.fields:
            assert isinstance(field, StructField), f"Expected StructField, got {type(field)}"

        assert all(isinstance(field, StructField) for field in self.fields)
        c = Counter(field.name for field in self.fields)
        for name, count in c.items():
            if count > 1:
                raise AssertionError("StructField names must be unique")

    def to_source(self):
        fields = '\n'.join(str(field) for field in self.fields)
        return f"struct {self.name} {{ {fields}\n}}"


class StructField(Node):
    """
    NAME type SEMI
    """
    def __init__(self, name, type):
        assert isinstance(name, str)
        assert isinstance(type, str)
        super().__init__(name=name, type=type)

    def to_source(self):
        return f"{self.name} {self.type};"


class FieldLookup(Location):
    """
    p.x
    p.y
    """

    def __init__(self, location, fieldname, nested=False):
        assert isinstance(location, Location), f"Expected Location. got {type(location)} {repr(location)}"
        assert isinstance(fieldname, str), f"Expected str. got {type(fieldname)}"
        super().__init__(location=location, fieldname=fieldname, nested=nested)

    def to_source(self):
        return f"{self.location}.{self.fieldname}"

class Integer(Expression):
    """
    Example: 42
    """

    def __init__(self, value):
        assert isinstance(value, int)
        super().__init__(value=value)

    def to_source(self):
        return f"{self.value}"

    def __str__(self):
        return str(self.value)

class Float(Expression):
    """
    Example: 42.0
    """

    def __init__(self, value):
        assert isinstance(value, float)
        super().__init__(value=value)

    def to_source(self):
        return f"{self.value}"

    def __str__(self):
        return "{:.6f}".format(self.value)


class Bool(Expression):
    def __init__(self, value):
        assert isinstance(value, bool)
        super().__init__(value=value)
    def to_source(self):
        return 'true' if self.value else 'false'

    def __str__(self):
        return str(self.value)

class CharacterLiteral(Expression):
    def __init__(self, value):
        assert isinstance(value, str)

        super().__init__(value=value)

    def to_source(self):
        return f"{repr(self.value)}"

    def __str__(self):
        return self.value

class UnaryOp(Expression):
    def __init__(self, op, operand):
        assert isinstance(op, str)
        assert op in ('+', '-', '!'), f"Invalid Unary operand: {op}"
        assert isinstance(operand, Expression)
        super().__init__(op=op, operand=operand)

    def to_source(self):
        return f'{self.op}{self.operand}'


class Identifier(Location):
    def __init__(self, name):
        assert isinstance(name, str)
        super().__init__(name=name)

    def to_source(self):
        return f"{self.name}"

    def __str__(self):
        return self.name


class BinOp(Expression):
    """
    Example: left + right
    """

    def __init__(self, op, left, right):
        assert isinstance(op, str)
        assert op in (
            "+",
            "-",
            "*",
            "/",
            "<",
            "<=",
            ">=",
            ">",
            "==",
            "!=",
            "&&",
            "||"
        ), f"Operation {op} is invalid"
        assert isinstance(left, Expression)
        assert isinstance(right, Expression)
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
        return cls(left=left, right=right, op="<")

    @classmethod
    def lte(cls, left, right):
        return cls(left=left, right=right, op="<=")

    @classmethod
    def gt(cls, left, right):
        return cls(left=left, right=right, op=">")

    @classmethod
    def gte(cls, left, right):
        return cls(left=left, right=right, op=">=")

    @classmethod
    def eq(cls, left, right):
        return cls(left=left, right=right, op="==")

    @classmethod
    def ne(cls, left, right):
        return cls(left=left, right=right, op="!=")


class Unit(Expression):
    def to_source(self):
        return "()"


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
        return f"{{ \n\t{statment_sources} \n}}"


class CompoundExpr(Expression):  # Not sure if this is totally correct
    def __init__(self, clause):
        assert isinstance(clause, Clause)
        super().__init__(clause=clause)

    def to_source(self):
        return "{" + " ".join(str(stmt) for stmt in self.clause.statements) + "}"


class PrintStatement(Statement):
    """
    PRINT expression SEMI
    """

    def __init__(self, expression):
        assert isinstance(expression, Expression), f"Expected expression got {type(expression)}"
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
        return f"{self.location} = {self.value};"


class VariableDefinition(Definition):
    def __init__(self, name, type, value):
        assert isinstance(name, str)
        assert type is None or isinstance(type, str)
        assert value is None or isinstance(value, Expression)
        super().__init__(name=name, type=type, value=value)

    def to_source(self):
        src = f"var {self.name}"
        if self.type is not None:
            src += f" {self.type}"
        if self.value is not None:
            src += f" = {self.value}"
        return f"{src};"


class ConstDefinition(Definition):
    def __init__(self, name, value, type=None):
        assert isinstance(name, str)
        assert isinstance(value, Expression)
        assert type is None or isinstance(type, str)
        super().__init__(name=name, value=value, type=type)

    def to_source(self):
        return (
            f"const {self.name}{' ' + self.type if self.type else ''} = {self.value};"
        )


class WhileLoop(Statement):
    def __init__(self, condition, body):
        assert isinstance(condition, Expression)
        assert isinstance(body, Clause)
        super().__init__(condition=condition, body=body)

    def to_source(self):
        if_statement = f"while {self.condition} {self.body}"
        return dedent(if_statement)


class Parameter(Node):
    def __init__(self, name, type):
        assert isinstance(name, str)
        assert isinstance(type, str)
        super().__init__(name=name, type=type)

    def to_source(self):
        return f"{self.name} {self.type}"


class FunctionDefinition(Definition):
    def __init__(self, name, parameters, rtype, body):
        assert isinstance(name, str)
        assert parameters is None or isinstance(parameters, Iterable)
        parameters = tuple(parameters) if parameters else tuple()
        assert all(isinstance(param, Parameter) for param in parameters)
        assert rtype is None or isinstance(rtype, str)
        assert isinstance(body, Clause)
        super().__init__(name=name, parameters=parameters, rtype=rtype, body=body)

    def to_source(self):
        src = f"func {self.name} ({', '.join(str(param) for param in self.parameters)}) {self.rtype} {self.body}"
        return src


class ReturnStatement(Statement):
    def __init__(self, expression):
        assert isinstance(expression, Expression)
        super().__init__(expression=expression)

    def to_source(self):
        return f"return {self.expression};"


class FunctionOrStructCall(Expression):
    def __init__(self, name, arguments):
        assert isinstance(name, str)  # can functions be stored at locations?
        assert arguments is None or isinstance(arguments, Iterable)
        arguments = tuple(arguments) if arguments else tuple()
        assert all(isinstance(arg, Expression) for arg in arguments)
        super().__init__(name=name, arguments=arguments)

    def to_source(self):
        return f"{self.name}({', '.join(str(arg) for arg in self.arguments)})"

class EnumChoice(Node):
    def __init__(self, name, type=None):
        assert isinstance(name, str)
        assert type is None or isinstance(type, str)
        super().__init__(name=name, type=type)

    def to_source(self):
        return repr(self)


class EnumDefinition(Definition):
    def __init__(self, name, enum_choices):
        super().__init__(name=name, enum_choices=enum_choices)
        for choice in self.enum_choices:
            assert isinstance(choice, EnumChoice)

    def to_source(self):
        return repr(self)

class EnumLookup(Location):
    def __init__(self, enum_location, choice_name, value_expression=None):
        assert isinstance(enum_location, Location)
        assert isinstance(choice_name, str)
        assert value_expression is None or isinstance(value_expression, Expression)
        super().__init__(enum_location=enum_location, choice_name=choice_name, value_expression=value_expression)

    def to_source(self):
        return repr(self)

class MatchCase(Node):
    def __init__(self, pattern, consequent):
        super().__init__(pattern=pattern, consequent=consequent)
        assert isinstance(consequent, Expression)
        assert isinstance(pattern, Pattern) # ??


    def to_source(self):
        return repr(self)

class Pattern(Node):
    def __init__(self, name, type):
        assert isinstance(name, str), f"expected str got {type(name)}"
        assert type is None or isinstance(type, str), f'expected None or str got {type(name)}'
        super().__init__(name=name, type=type)

class MatchExpression(Expression):
    def __init__(self, expression, cases=None):
        super().__init__(expression=expression, cases=cases)
        assert cases is None or all(isinstance(case, MatchCase) for case in cases)

    def to_source(self):
        return repr(self)


class BreakStatement(Statement):
    def to_source(self):
        return 'break;'


class ContinueStatement(Statement):
    def to_source(self):
        return 'continue;'


class NodeVisitor:
    ...  # We'll be removing to_source methods soon

class Grouping(Expression):
    """
    LPAREN expression RPAREN
    """
    def __init__(self, expression):
        assert isinstance(expression, Expression)
        super().__init__(expression=expression)

    def to_source(self):
        return f'({self.expression})'

def to_source(node):
    return node.to_source()


#  Implement some classes to better represent wabbit objects as Python objects
#  Mostly, just for printing


class WabbitUnit:
    def __bool__(self):
        return False

    def __hash__(self):
        return hash(None)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __repr__(self):
        return 'WabbitUnit()'

    def __str__(self):
        return '()'

class WabbitFloat(float):
    def __str__(self):
        return "{:.6f}".format(self)
        # not sure if 6 this is actually significant/correct...
        # but that's what is in the output files, so ¯\_(ツ)_/¯

    def __repr__(self):
        return f'WabbitFloat({self})'

from functools import lru_cache

@lru_cache(maxsize=1024)
def black_format_code(source):
    import black
    kwargs = {
        'line_length': 120,
    }
    reformatted_source = black.format_file_contents(
        source, fast=True, mode=black.FileMode(**kwargs)
    )
    return reformatted_source
