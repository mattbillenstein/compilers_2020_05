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
    def __init__(self, *, lineno=None):
        self.lineno = lineno

class Expression(Node):
    """An expression is something that can be used on the left-hand-side
    of an assignment.
    """


# class Location(Node):
#     '''
#     A location represents a place to load/store values.  For example, a variable,
#     an object attribute, an index in an array, etc.
#     '''

class Statement(Node):
    """A statement is a single complete instruction"""
    pass


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
    def __init__(self, location, expression, **options):
        self.location = location
        self.expression = expression
        super().__init__(**options)
        self.is_valid()

    def __repr__(self):
        return f"Assignment({self.location}, {self.expression})"

    def is_valid(self):
        try:
            assert isinstance(self.location, Name)
            assert isinstance(self.expression, (Name, Expression, Statements))
        except AssertionError:
            print("self.location", self.location)
            print("self.expression", self.expression)
            raise

class BinOp(Expression):
    """
    Example: left + right
    """
    def __init__(self, op, left, right, **options):
        self.op = op
        self.left = left
        self.right = right
        super().__init__(**options)
        # self.is_valid()

    def __repr__(self):
        return f"BinOp('{self.op}', {self.left}, {self.right})"

    def is_valid(self):
        try:
            assert self.op in {'+', '*', '-', '/', '<', '>', '>=', '<=', '=='}
            # assert isinstance(self.left, Expression)
            # assert isinstance(self.right, Expression)
        except AssertionError:
            print("in BinOp, self.op = ", self.op)
            print("in BinOp, self.left = ", self.left)
            print("in BinOp, self.right = ", self.right)
            raise


class Bool(Expression):
    def __init__(self, value, **options):
        self.value = value
        super().__init__(**options)

    def __repr__(self):
        return f"Bool('{self.value}')"


class Char(Expression):
    def __init__(self, value, **options):
        self.value = value
        super().__init__(**options)

    def __repr__(self):
        return f"Char({self.value})"

    def is_valid(self):
        assert isinstance(self.value, str)


class Const(Definition):
    """Examples:
        const pi = 3.14159;
        const tau float;
    """
    def __init__(self, name, value, type=None, **options):
        self.name = name
        self.value = value
        self.type = type
        super().__init__(**options)

    def __repr__(self):
        type = f", '{self.type}'" if self.type is not None else ''
        return f"Const('{self.name}', {self.value}{type})"


class Compound(Expression):
    '''
    A series of statements or expressions serving as a single expression.
    '''
    def __init__(self, *statements, **options):
        self.statements = statements
        super().__init__(**options)
        self.is_valid()

    def __repr__(self):
        return f'Compound({self.statements})'

    def is_valid(self):
        assert all(isinstance(st, (Expression, Statement)) for st in self.statements)


class Float(Expression):
    def __init__(self, value, **options):
        self.value = value
        super().__init__(**options)

    def __repr__(self):
        return f"Float({self.value})"

    def is_valid(self):
        assert isinstance(self.value, float)


class ExpressionStatement(Statement):
    """Currently, the only purpose of this class is to ensure that
       expressions used as statements are properly recreated with
       a final semi-colon when converting back to source.
    """
    def __init__(self, expression, **options):
        self.expression = expression
        super().__init__(**options)

    def __repr__(self):
        return f"ExpressionStatement({self.expression})"

    def is_valid(self):
        assert isinstance(self.expression, Expression)

class Group(Expression):
    '''
    ( expression )      # Expression surrounded by parenthesis
    '''
    def __init__(self, expression, **options):
        self.expression = expression
        super().__init__(**options)

    def __repr__(self):
        return f'Group({self.expression})'

    def is_valid(self):
        assert isinstance(self.expression, Expression)

class If(Statement):
    def __init__(self, condition, result, alternative=None, **options):
        self.condition = condition
        self.result = result
        self.alternative = alternative
        super().__init__(**options)
        # self.is_valid()

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
    def __init__(self, value, **options):
        self.value = value
        super().__init__(**options)

    def __repr__(self):
        return f"Integer({self.value})"

    def is_valid(self):
        assert isinstance(self.value, int)


class Name(Node):
    """
    a variable name
    """
    def __init__(self, name, **options):
        self.name = name
        super().__init__(**options)
        self.is_valid()

    def __repr__(self):
        return f"Name({self.name})"

    def is_valid(self):
        try:
            assert isinstance(self.name, str)
        except AssertionError:
            print("problem in Name(); self.name = ", self.name)
            raise


class Print(Statement):
    """
    print expression
    """
    def __init__(self, expression, **options):
        self.expression = expression
        super().__init__(**options)
        self.is_valid()

    def __repr__(self):
        return f"Print({self.expression})\n"

    def is_valid(self):
        assert isinstance(self.expression, (Expression, Name, str))


class Statements(Statement):
    """
    A sequence of statements
    """
    def __init__(self, *statements, **options):
        self.statements = statements
        super().__init__(**options)
        self.is_valid()

    def __repr__(self):
        return f"Statements{self.statements}"

    def is_valid(self):
        assert all(isinstance(st, Statement) for st in self.statements)


class Type(Node):
    """
    Example: float
    """
    def __init__(self, type, **options):
        self.type = type
        super().__init__(**options)
        self.is_valid()

    def __repr__(self):
        return f"Type({self.type})"

    def is_valid(self):
        assert self.type is None or isinstance(self.type, str)

class UnaryOp(Expression):
    """
    Example: - value
    """
    def __init__(self, op, value, **options):
        self.op = op
        self.value = value
        super().__init__(**options)
        # self.is_valid()

    def __repr__(self):
        return f"UnaryOp('{self.op}', {self.value})"

    def is_valid(self):
        try:
            assert self.op in  ["-", "+", "!"]
        except AssertionError:
            print(self.op)
            raise
        assert isinstance(self.value, (int, float, Name))


class Var(Definition):
    """Examples:
        var int pi;
    """
    def __init__(self, name, type=None, value=None, **options):
        self.name = name
        self.type = type
        self.value = value
        super().__init__(**options)

    def __repr__(self):
        type = f", '{self.type}'" if self.type is not None else ''
        value = f", 'value={self.value}" if self.value is not None else ''
        return f"Var('{self.name}'{type}{value})"


class While(Statement):
    def __init__(self, condition, statements, **options):
        self.condition = condition
        self.statements = statements
        super().__init__(**options)
        self.is_valid()

    def __repr__(self):
        return (f"While({self.condition}, {self.statements})")

    def is_valid(self):
        try:
            assert isinstance(self.condition, (Expression, Name, Bool))
            assert isinstance(self.statements, (Statement, Statements))
        except AssertionError:
            print("self.condition = ", self.condition)
            raise


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


@add(Bool)
def to_source_Bool(node):
    return str(node.value)

@add(Char)
def to_source_Char(node):
    return node.value

@add(Const)
def to_source_Const(node):
    type = f' {node.type}' if node.type else ''
    return f'const {node.name}{type} = {to_source(node.value)};'

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

@add(Name)
def to_source_Name(node):
    return f"{node.name}"

@add(Print)
def to_source_Print(node):
    return f"print {to_source(node.expression)};"

@add(Statements)
def to_source_Statements(node):
    statements = [to_source(s) for s in node.statements]
    return "\n".join(statements)

@add(UnaryOp)
def to_source_UnaryOp(node):
    return f"{node.op}{to_source(node.value)}"

@add(Var)
def to_source_Var(node):
    type = f' {node.type}' if node.type else ''
    value = f' = {to_source(node.value)}' if node.value else ''
    return f'var {node.name}{type}{value};'

@add(While)
def to_source_While(node):
    return f"while {to_source(node.condition)} {{\n{to_source(node.statements)}\n}}"
